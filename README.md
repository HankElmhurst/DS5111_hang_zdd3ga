# DS5111_hang_zdd3ga

Software Automation in Data Science — environment bootstrap for a fresh VM.

This repo automates going from a bare Ubuntu VM to a working Python data-science
environment, backed up on GitHub.

## Starting point (assumptions)

Before you begin, you should already have:

- A fresh Ubuntu VM that just came up (e.g. an AWS EC2 instance)
- An SSH key on the VM that can authenticate to GitHub
  (verify with `ssh -T git@github.com` → expect `Hi <username>!`)
- `git` available (ships with Ubuntu)

## Setup steps

1. **Clone this repo onto the VM**

   ```bash
   git clone git@github.com:HankElmhurst/DS5111_hang_zdd3ga.git
   cd DS5111_hang_zdd3ga
   ```

2. **Bootstrap the base system** — installs `make`, the Python venv package, and `tree`.

   ```bash
   bash scripts/init.sh
   ```

   *Quick test:* run `tree`. If it lists the directory instead of "command not
   found", the bootstrap worked.

3. **Set your git identity** — tags your commits with your name and email.

   ```bash
   bash scripts/init_git_creds.sh
   ```

   *Quick test:* the script echoes your config. You should see your
   `user.email` and `user.name` printed to the console. You can re-check any
   time with `git config --global --list`.

4. **Build the Python virtual environment** — `make update` creates the `env`
   and installs everything in `requirements.txt`.

   ```bash
   make update
   ```

   *Quick test:* activate the environment and list packages.

   ```bash
   . env/bin/activate
   pip list
   ```

   You should see `(env)` on the left of your prompt, and `pandas` and `numpy`
   in the package list.

## What's in this repo

| File | Purpose |
|---|---|
| `scripts/init.sh` | Base system bootstrap (make, venv, tree) |
| `scripts/init_git_creds.sh` | Sets git user.name / user.email |
| `makefile` | `make update` builds the venv from requirements |
| `requirements.txt` | Python packages (pandas, numpy) |

## Notes

- `make` (with no target) prints the makefile contents — handy for a quick look.
- The `env/` virtual environment is **not** committed; it is regenerated on each
  machine via `make update`. Keep it listed in `.gitignore`.
