#!/usr/bin/env python3
"""Enrich raw transcripts into structured records via a pluggable LLM strategy.

Reads JSONL transcript records from stdin, delegates enrichment to a selected
LLMStrategy (e.g. Gemini), and writes enriched JSON records to stdout.
"""

import sys
import os
import json
import logging
import argparse
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environmental configurations from local workspace files
load_dotenv()

# Audit logging framework tracking pipeline telemetry
logging.basicConfig(
    filename='logs/pipeline_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LLMStrategy(ABC):
    """
    Contract for any LLM-backed enrichment strategy.

    Given one transcript record (video_id + raw_text), a concrete strategy
    returns a structured, enriched record. The implementation may call a real
    model (Claude) or return a deterministic mock — the engine does not care
    which, as long as this contract is honored.
    """

    @abstractmethod
    def enrich(self, video_id: str, raw_text: str) -> dict:
        """
        Transform one raw transcript into an enriched record.

        Args:
            video_id: Stable identifier for the transcript (non-empty).
            raw_text: Unstructured transcript text; may contain timestamps.

        Returns:
            A dict satisfying the downstream schema contract:
              - video_id (string, required)
              - cleaned_text (str, required)
              - tech_terms   (list[str], optional)
              - book_names   (list[str], optional)

            video_id is echoed back by the concrete strategy 
            so the returned dict matches the full downstream schema
        """
        pass

class GeminiStrategy(LLMStrategy):
    """Enrich transcripts using Google's Gemini model with a fixed JSON schema. """
    def __init__(self, client):
        self.client = client
        self.response_schema = {
            "type": "OBJECT",
            "properties": {
                "video_id": {"type": "STRING"},
                "cleaned_text": {"type": "STRING"},
                "tech_terms": {"type": "ARRAY", "items": {"type": "STRING"}},
                "book_names": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": ["video_id", "cleaned_text"],
        }

    def enrich(self, video_id, raw_text) -> dict:
        prompt = f""" You are an elite data engineer. Clean this transcript text for video_id '{video_id}'.
            1. Strip all timestamps and duration codes.
            2. Extract technical architecture terms and books.
            """

        # ---------------------------------------------------------------------
        # Structured Model Invocation and Instant Stream Flushing
        # Call the 'gemini-2.5-flash' model via the unified SDK interface.
        # Inject the constructed prompt along with the raw text sequence payload.
        # Map the configuration block to use the structured JSON mime-type
        # and enforce your defined response schema parameters.
        # ---------------------------------------------------------------------
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{prompt}\n\nTRANSCRIPT:\n{raw_text}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self.response_schema
            )
        )

        result = json.loads(response.text)
        result["video_id"] = video_id
        return result

class EnrichmentEngine:
    """Stream transcripts from stdin through a strategy and emit enriched JSON to stdout. """
    def __init__(self, strategy: LLMStrategy):
        self.strategy = strategy

    def run_stream(self):
        """Read JSONL records from stdin, enrich each, and write results to stdout. """
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                video_id = data["video_id"]
                raw_text = data["raw_text"]
                logging.info("Orchestrating %s enrichment for video: %s ", type(self.strategy).__name__, video_id)
            except Exception as e:
                logging.error("Failed to parse incoming JSON info: %s ", e)
                continue

            try:
                enriched_result = self.strategy.enrich(video_id, raw_text)
                sys.stdout.write(json.dumps(enriched_result) + "\n")
                sys.stdout.flush()
            except Exception as e:
                logging.error("Failed processing video %s during LLM generation: %s ", video_id, e)

def main(argv=None):
    parser = argparse.ArgumentParser(description = "Multi-LLM Strategy Transcript Enrichment Node.")

    parser.add_argument(
        "--LLM",
        choices=["Gemini"],
        default="Gemini",
        help="Target video transcript enrichment strategy (Default to Google Gemini)."
    )

    # Pass the command line argv variable into the parse_args function
    args = parser.parse_args(argv)
    logging.info("Pipeline Step 2B started. Selected LLM strategy: %s ", args.LLM)

    # -------------------------------------------------------------------------
    # API Environment Validation and Client Initialization
    # Extract the necessary credential key token from the local environment.
    # If the token is missing, log a critical failure and terminate the system.
    # Otherwise, instantiate the official Google GenAI Client utility.
    # -------------------------------------------------------------------------
    my_api_key = os.getenv("GEMINI_API_KEY")

    if not my_api_key:
        logging.critical("No API Key exists. ")
        sys.exit(1)

    if args.LLM == "Gemini":
        client = genai.Client(api_key=my_api_key)
        strategy = GeminiStrategy(client)
    else:
        raise ValueError(f"Unsupported LLM: {args.LLM}")

    engine = EnrichmentEngine(strategy)
    engine.run_stream()

    logging.info("Pipeline Step 2B finished.")

if __name__ == '__main__':
    main()
