"""Tests for the enrichment engine and strategy classes."""

import sys
import io
import json
from bin.enrich_transcripts import EnrichmentEngine, LLMStrategy


class MockLLMStrategy(LLMStrategy):
    """Deterministic, offline test double — no SDK, no network, no cost.
    Returns a schema-valid enriched record so we can verify the engine's
    stdin -> enrich -> stdout plumbing in isolation."""
    def enrich(self, video_id: str, raw_text: str) -> dict:
        return {
            "video_id": video_id,
            "cleaned_text": raw_text.replace("00:01", "").strip(),
            "tech_terms": ["mock_term"],
            "book_names": [],
        }


def test_engine_streams_enriched_output(monkeypatch, capsys):
    """Engine reads a row from stdin and emits enriched JSONL."""
    row = {"video_id": "ds5111_v001", "raw_text": "00:01 Welcome to class."}
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(row) + "\n"))

    EnrichmentEngine(MockLLMStrategy()).run_stream()

    lines = capsys.readouterr().out.strip().split("\n")
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["video_id"] == "ds5111_v001"
    assert parsed["cleaned_text"] == "Welcome to class."
    assert parsed["tech_terms"] == ["mock_term"]


def test_engine_skips_malformed_line(monkeypatch, capsys):
    """Malformed JSON lines are skipped, valid rows survive."""
    stream = json.dumps({"video_id": "v1", "raw_text": "ok"}) + "\nNOT_JSON\n"
    monkeypatch.setattr(sys, "stdin", io.StringIO(stream))

    EnrichmentEngine(MockLLMStrategy()).run_stream()

    lines = [l for l in capsys.readouterr().out.strip().split("\n") if l]
    assert len(lines) == 1                       # good row survives; bad row skipped
    assert json.loads(lines[0])["video_id"] == "v1"


def test_engine_survives_strategy_failure(monkeypatch, capsys):
    """Engine emits nothing and doesn't crash when strategy raises."""
    class ExplodingStrategy(LLMStrategy):
        """Test double whose enrich() always raises."""
        def enrich(self, video_id, raw_text):
            raise RuntimeError("simulated model outage")

    monkeypatch.setattr(sys, "stdin",
                        io.StringIO(json.dumps({"video_id": "v1", "raw_text": "ok"}) + "\n"))

    EnrichmentEngine(ExplodingStrategy()).run_stream()

    assert capsys.readouterr().out.strip() == ""  # nothing emitted, no crash
