# AGENTS.md

## Repo Snapshot
- Repository: `jtgsystems/free-sitemap-generator`
- Default branch: `main`
- Visibility: `public`
- Summary: Free sitemap generator - Create XML sitemaps for SEO
- Detected stack: Python

## Read First
- `README.md`
- `CONTRIBUTING.md`
- `pyproject.toml`
- `requirements.txt`
- `setup.py`
- `.github/workflows/`

## Key Paths
- `sitemap_generator/`

## Working Rules
- Keep changes focused on the task and match the existing file layout and naming patterns.
- Update tests and docs when behavior changes or public interfaces move.
- Do not commit secrets, credentials, ad-hoc exports, or large generated artifacts unless the repository already tracks them intentionally.
- Prefer the existing automation and CI workflow over one-off commands when both paths exist.
- Avoid archive-style folders unless the task explicitly targets them: `.retired/`.

## Verified Commands
- Install: `python -m pip install -r requirements.txt`
- Test: `python -m pytest`
- Build: `python -m build`

## Change Checklist
- Run the relevant tests or static checks for the files you changed before finishing.
- Keep human-facing docs aligned with behavior changes.
- If the repo has specialized areas later, add nested `AGENTS.md` files close to that code instead of overloading the root file.

## Notes
- CI source of truth lives in `.github/workflows/`.

This file should stay short, specific, and current. Update it whenever the repo's real setup or verification steps change.
