import sys
import io
import pytest
from scripts.clean_ids import main, youtube_id_validation



def test_script_execution(monkeypatch, capsys):
    # 1. Simulate the standard input data
    # We use io.StringIO to make a string act like a readable stream/file
    fake_input = io.StringIO("kcFsuxaJ1es\nasd123\n")
    monkeypatch.setattr(sys, "stdin", fake_input)

    # 2. Run the script's main logic
    main()

    # 3. Capture the printed output
    captured = capsys.readouterr()

    # 4. Assert that the data was modified correctly
    assert captured.out == "kcFsuxaJ1es\n"

# Parametrize fixutures and test functions
@pytest.mark.parametrize(
    "test_input, expected_output",
    [
        ("abcdefghij", False),
        ("abcdefghij9", True ),
        ("abcdefghij98", False),
        ("abcdefghi-9", True),
        ("abcdefghi_9", True),
        ("abcdefgh-_9", True),
        ("abcdefghi!9", False),
        ("1234567890-", True),
        ("1234567890_", True)
    ] 
)

def test_youtube_id_validation(test_input, expected_output):
    assert youtube_id_validation(test_input) == expected_output
