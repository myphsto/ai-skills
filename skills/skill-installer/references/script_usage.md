# Skill Installer Reference

## Script Commands

### list-skills.py

Lists available skills from a GitHub repo.

```bash
# List curated skills (default)
scripts/list-skills.py

# List experimental skills
scripts/list-skills.py --path skills/.experimental

# JSON output
scripts/list-skills.py --format json

# Custom repo
scripts/list-skills.py --repo owner/repo --path skills/custom --ref develop
```

**Options:**
| Flag | Default | Description |
|------|---------|-------------|
| `--repo` | `openai/skills` | GitHub repo (owner/repo) |
| `--path` | `skills/.curated` | Path within repo to list |
| `--ref` | `main` | Git ref |
| `--format` | `text` | Output format (text/json) |

### install-skill-from-github.py

Installs a skill into `~/.agents/skills/`.

```bash
# From curated list
scripts/install-skill-from-github.py --repo openai/skills --path skills/.curated/skill-name

# From URL
scripts/install-skill-from-github.py --url https://github.com/owner/repo/tree/main/path/to/skill

# Multiple skills
scripts/install-skill-from-github.py --repo owner/repo --path skills/skill-a skills/skill-b

# Custom name
scripts/install-skill-from-github.py --repo owner/repo --path skills/foo --name my-skill

# Force git method
scripts/install-skill-from-github.py --repo owner/repo --path skills/foo --method git
```

**Options:**
| Flag | Default | Description |
|------|---------|-------------|
| `--repo` | (required) | GitHub repo (owner/repo) |
| `--url` | (alternative) | Full GitHub URL |
| `--path` | (required) | Path(s) to skill(s) |
| `--ref` | `main` | Git ref |
| `--dest` | `~/.agents/skills` | Destination directory |
| `--name` | (basename of path) | Custom skill name |
| `--method` | `auto` | Download method (auto/download/git) |

## Authentication

Scripts check for tokens in environment variables (in order):
1. `GITHUB_TOKEN`
2. `GH_TOKEN`

For private repos with download failures, scripts fall back to git sparse checkout, trying HTTPS then SSH.

## Installation Locations

- Default: `~/.agents/skills/<skill-name>/`
- Each skill directory must contain a `SKILL.md` file
- Custom destination with `--dest` flag

## Error Handling

- Aborts if destination directory already exists
- Validates SKILL.md exists in source
- Validates paths are relative (no `..` or absolute paths)
- Cleans up temp directories on failure
- Download method falls back to git on 401/403/404

## GitHub API

Skills listing uses GitHub Contents API:
```
https://api.github.com/repos/{repo}/contents/{path}?ref={ref}
```

User agent headers:
- Listing: `opencode-skill-list`
- Installing: `opencode-skill-install`
