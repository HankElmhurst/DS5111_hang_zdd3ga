# 2605_DS5111_zdd3ga

Software Automation in Data Science — YouTube transcript enrichment pipeline.

## Project objective

This repo runs a three-stage pipeline: extract YouTube transcripts by video ID
(`bin/extract_transcripts.py`), enrich them through an LLM strategy
(`bin/enrich_transcripts.py`, Gemini by default), and validate the resulting
JSONL records against a schema contract (`bin/validate_schema.py`).
Input is video IDs on stdin; output is schema-valid JSONL on stdout.

## Starting point (assumptions)

Before you begin, you should already have:

- A fresh Ubuntu VM (e.g. an AWS EC2 instance)
- An SSH key on the VM that can authenticate to GitHub
  (verify with `ssh -T git@github.com` → expect `Hi <username>!`)
- `git` available (ships with Ubuntu)

## Setup steps

1. **Clone this repo onto the VM**

```bash
   git clone git@github.com:HankElmhurst/2605_DS5111_zdd3ga.git
   cd 2605_DS5111_zdd3ga
```

2. **Bootstrap the base system** — installs `make`, the Python venv package, and `tree`.

```bash
   bash init.sh
```

3. **Set your git identity**

```bash
   bash init_git_creds.sh
```

4. **Build the virtual environment and install dependencies**

```bash
   make update
```

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | Yes, for enrichment | Auth for the Google Gemini client; pipeline exits with a critical log if absent |
| `WEBSHARE_USER` | Optional | Webshare residential proxy username for transcript extraction |
| `WEBSHARE_PASSWORD` | Optional | Webshare residential proxy password; without both, extraction uses direct IP routing |

Set these in a repo-root `.env` file (gitignored) or export them in the shell.

## Verification

```bash
make lint   # pylint over bin/ and tests/ — expect 10.00/10, exit 0
make test   # pytest — expect 17 passed, 1 skipped, 1 xfailed
```

## Running the pipeline

```bash
make run    # extract → enrich (mock input) → validate
```

## Make targets

| Target | Purpose |
|---|---|
| `make env` | Create the `env/` virtual environment |
| `make update` | Install/refresh dependencies from requirements.txt |
| `make lint` | Quality gate: pylint with repo pylintrc |
| `make test` | Run the pytest suite |
| `make run` | Execute the pipeline end-to-end |

## Notes

- `make` (no target) prints the makefile — handy for a quick look.
- The `env/` virtual environment is **not** committed; it is regenerated per machine via `make update`.
