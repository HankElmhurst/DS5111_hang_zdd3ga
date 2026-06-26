import sys
import io
import json
import pytest
from youtube_transcript_api import YouTubeTranscriptApi
from bin.extract_transcripts import main

class MockTranscriptContainer:
    def to_raw_data(self):
        return [{"start": 10.5, "text": "Automated container tracking loop text entry."}]

def test_main_success(monkeypatch, capsys):
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", lambda self, vid: MockTranscriptContainer())
    monkeypatch.setattr(sys, "stdin", io.StringIO("fake_video_999\n"))
    main()
    lines = capsys.readouterr().out.strip().split("\n")
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["video_id"] == "fake_video_999"
    assert "Automated container tracking" in parsed["raw_text"]

def test_main_handles_fetch_error(monkeypatch, capsys):
    def boom(self, vid):
        raise Exception("unfetchable")
    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", boom)
    monkeypatch.setattr(sys, "stdin", io.StringIO("bad_id\n"))
    main()
    assert capsys.readouterr().out.strip() == ""
