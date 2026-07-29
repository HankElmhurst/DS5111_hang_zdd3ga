"""Tests for the transcript extraction pipeline."""

import sys
import io
import json

from youtube_transcript_api import YouTubeTranscriptApi
from bin.extract_transcripts import main

class MockTranscriptContainer:
    """Test double mimicking a transcript API response container."""
    def to_raw_data(self):
        """Return a fake transcript entry list."""
        return [{"start": 10.5, "text": "Automated container tracking loop text entry."}]

def test_main_success(monkeypatch, capsys):
    """main() fetches a transcript and emits valid JSONL."""
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", lambda self, vid: MockTranscriptContainer())
    monkeypatch.setattr(sys, "stdin", io.StringIO("fake_video_999\n"))
    main()
    lines = capsys.readouterr().out.strip().split("\n")
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["video_id"] == "fake_video_999"
    assert "Automated container tracking" in parsed["raw_text"]

def test_main_handles_fetch_error(monkeypatch, capsys):
    """main() emits nothing when the API fetch raises."""
    def boom(self, vid):
        raise Exception("unfetchable")
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", boom)
    monkeypatch.setattr(sys, "stdin", io.StringIO("bad_id\n"))
    main()
    assert capsys.readouterr().out.strip() == ""
