# Git training guide

A hands-on course in the git skills a professional developer uses every day, practised on this project. Work through the missions **in your own terminal, typing every command yourself**. By the end you'll have used everything in the "Everyday commands" table on real work, and your GitHub history will show it.

Time needed: about an hour per mission. Do one or two a week, and keep going: regular activity over several weeks matters more than a burst in one day.

---

## Part 1: Set up your computer (once)

### 1. Get a Unix-style terminal
- **macOS:** open the **Terminal** app.
- **Linux:** open your terminal.
- **Windows:** install **WSL2**, which gives you Linux inside Windows. Open PowerShell **as administrator** and run `wsl --install`, restart, then open **Ubuntu** from the Start menu. Do all the steps below inside Ubuntu.

### 2. Install the tools
```bash
# macOS (install Homebrew first from https://brew.sh)
brew install git gh python

# Ubuntu / WSL2
sudo apt update && sudo apt install -y git gh python3 python3-venv python3-pip
```
If `gh` isn't found on Ubuntu, follow https://github.com/cli/cli/blob/trunk/docs/install_linux.md.

### 3. Tell git who you are
Use the same email as your GitHub account so your commits are linked to your profile.
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global pull.rebase false
```
Check with `git config --list`.

### 4. Log in to GitHub from the terminal
```bash
gh auth login
```
Choose **GitHub.com → HTTPS → Yes (authenticate git) → Login with a web browser**, and follow the steps.

### 5. Get the project
```bash
cd ~
git clone https://github.com/snok-dev/solar-wind-sizer.git
cd solar-wind-sizer
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
python3 -m pytest
```
✅ You should see all tests pass. Run `solarwind --help` to try the tool.

> Each time you open a new terminal: `cd ~/solar-wind-sizer && source .venv/bin/activate`

---

## Part 2: How git thinks (5 minutes)

| Idea | What it means |
|---|---|
| **Repository** | The project folder plus its full history (hidden in `.git/`) |
| **Commit** | A saved snapshot with a message explaining the change |
| **Branch** | A separate line of work. `main` is the stable version; you build features on other branches |
| **Staging** (`git add`) | Choosing which changes go into the next commit |
| **Remote** (`origin`) | The copy on GitHub |
| **Push / pull** | Send your commits to GitHub / bring GitHub's commits to you |
| **Pull request (PR)** | Asking to merge a branch into `main`, with a place to review and discuss |

The everyday loop:

```
git switch main → git pull → git switch -c my-change → edit → test → git add → git commit → git push → open PR → merge
```

---

## Part 3: Missions

### Mission 1: Your first branch, commit and pull request
**Goal:** add Glasgow to the built-in locations (roadmap: "More locations").

```bash
git switch main
git pull
git switch -c add-glasgow-location
```

1. Open `src/solarwind/solar.py` and add a line to `LOCATIONS`:
   ```python
   "glasgow": {"annual": 2.4, "low": 0.4, "high": 4.5},
   ```
2. Add a test to `tests/test_solar.py`:
   ```python
   def test_glasgow_is_a_known_location():
       assert solar.peak_sun_hours("Glasgow") == 2.4
   ```
3. Check and save your work:
   ```bash
   python3 -m pytest
   git status                 # see what changed
   git diff                   # see exactly how it changed
   git add src/solarwind/solar.py tests/test_solar.py
   git commit -m "Add Glasgow to built-in locations"
   git push -u origin add-glasgow-location
   ```
4. Open the pull request:
   ```bash
   gh pr create --fill
   ```
5. On GitHub, open the PR. Wait for the **Tests** check to turn green ✅, then click **Merge pull request** and **Delete branch**.
6. Back in the terminal, update your `main`:
   ```bash
   git switch main
   git pull
   git branch -d add-glasgow-location
   ```

✅ **Done when:** `git log --oneline` shows your commit on `main`.

---

### Mission 2: Plan work with issues
**Goal:** turn the roadmap into GitHub issues and close one with a PR.

```bash
gh issue create --title "Add more built-in locations" --body "Birmingham, Bristol, Newcastle, Port Harcourt, Kano" --label "good first issue"
gh issue list
```
Create issues for 4–5 other roadmap items too. Then, for the issue above:
```bash
git switch -c more-locations
# add Birmingham and Bristol to LOCATIONS, plus a test
git add -A
git commit -m "Add Birmingham and Bristol locations"
git push -u origin more-locations
gh pr create --title "Add Birmingham and Bristol" --body "Closes #2"   # use your issue's number
```
✅ **Done when:** merging the PR automatically closes the issue.

---

### Mission 3: Read the history
**Goal:** find out who changed what, when and why. You'll do this constantly.

```bash
git log --oneline --graph --all     # the shape of the history
git log -p -- src/solarwind/wind.py # every change to one file
git show HEAD                       # the latest commit in full
git blame src/solarwind/solar.py    # which commit last touched each line
git diff main..some-branch          # compare two branches
```
✅ **Done when:** you can answer "in which commit were real-world wind losses added, and why?" from the terminal.

---

### Mission 4: Undo things safely
Practise each one on a throwaway branch: `git switch -c practice-undo`.

| Situation | Command |
|---|---|
| Throw away edits to a file you haven't staged | `git restore file.py` |
| Unstage a file (keep the edits) | `git restore --staged file.py` |
| Fix the message of your last commit (before pushing) | `git commit --amend -m "Better message"` |
| Undo the last commit but keep the changes (before pushing) | `git reset --soft HEAD~1` |
| Undo a commit that's already pushed | `git revert <commit-id>` (adds a new commit that reverses it) |
| Put work aside to switch branches | `git stash`, later `git stash pop` |

⚠️ Never use `git reset --hard` or `git push --force` on `main`: they can destroy work others depend on.

✅ **Done when:** you've used each row at least once. Then delete the branch with `git switch main && git branch -D practice-undo`.

---

### Mission 5: Resolve a merge conflict
A conflict happens when two branches change the same lines. Make one on purpose:

```bash
git switch main
git switch -c conflict-a
# in src/solarwind/solar.py change DEFAULT_PERFORMANCE_RATIO to 0.78
git commit -am "Use 0.78 performance ratio"
git switch main
git switch -c conflict-b
# change the same line to 0.82
git commit -am "Use 0.82 performance ratio"
git merge conflict-a
```
Git stops and marks the file:
```
<<<<<<< HEAD
DEFAULT_PERFORMANCE_RATIO = 0.82
=======
DEFAULT_PERFORMANCE_RATIO = 0.78
>>>>>>> conflict-a
```
Edit the file to keep the line you want (say `0.8`), delete the marker lines, then:
```bash
python3 -m pytest
git add src/solarwind/solar.py
git commit -m "Merge conflict-a, keep 0.8 performance ratio"
```
Clean up: `git switch main && git branch -D conflict-a conflict-b`.

✅ **Done when:** you can resolve a conflict calmly, without fear.

---

### Mission 6: Keep a branch up to date
While you work on a branch, `main` may move on, for example when you merge another PR.

```bash
git switch main && git pull
git switch my-feature
git merge main          # bring the new main into your branch
python3 -m pytest
git push
```
✅ **Done when:** you've updated a branch that was behind `main`, then merged its PR.

---

### Mission 7: Keep secrets out of git
- Check `.gitignore` before committing. It already ignores `.venv/`, `.env` and build files.
- Always look at `git status` and `git diff --staged` before committing.
- **Never** commit passwords, API keys or tokens. If you do by accident, removing the file isn't enough, because it stays in the history. **Change (rotate) the key immediately**, then remove it.

✅ **Done when:** you've made a habit of reading `git diff --staged` before every commit.

---

### Mission 8: Release a version
After you've merged a few features:

1. Update `version` in `pyproject.toml` and `__version__` in `src/solarwind/__init__.py` (e.g. `0.2.0`), on a branch with a PR as usual.
2. After merging:
   ```bash
   git switch main && git pull
   git tag -a v0.2.0 -m "Version 0.2.0: more locations, autonomy days"
   git push origin v0.2.0
   gh release create v0.2.0 --generate-notes
   ```
✅ **Done when:** your repo shows a release on its GitHub page.

---

## Everyday commands

| Command | What it does |
|---|---|
| `git status` | What's changed and what's staged |
| `git diff` / `git diff --staged` | Exact changes not yet staged / staged |
| `git add <file>` / `git add -A` | Stage a file / everything |
| `git commit -m "message"` | Save a snapshot |
| `git switch -c <name>` | Create and move to a new branch |
| `git switch <name>` | Move to an existing branch |
| `git branch` | List branches |
| `git pull` | Get the latest commits from GitHub |
| `git push -u origin <branch>` | Send a new branch to GitHub (after that, just `git push`) |
| `git log --oneline --graph` | Compact history |
| `git merge <branch>` | Combine another branch into this one |
| `git stash` / `git stash pop` | Shelve / restore unfinished work |
| `gh pr create --fill` | Open a pull request |
| `gh pr list` / `gh pr checks` | See PRs / their test results |
| `gh issue create` / `gh issue list` | Create / list issues |

### Good commit messages
- Start with a verb, describe **what** changed: "Add Weibull wind distribution", "Fix panel count rounding for zero load"
- One logical change per commit
- If it needs explaining, add a body: `git commit` (no `-m`) opens an editor; leave a blank line after the title

---

## Ready-to-apply checklist

- [ ] Repository is **public**, with a **licence**, a clear **README** and a **roadmap**
- [ ] Several **open issues** describing real planned work
- [ ] Your own work arrives through **branches and pull requests**, with green test checks
- [ ] **Commits spread over several weeks**, with clear messages
- [ ] At least one **release** tagged
- [ ] You can explain what every file in `src/solarwind/` does
- [ ] You're comfortable doing Missions 1–6 without looking at this guide
