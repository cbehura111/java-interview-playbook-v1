# Senior Java Backend Interview Playbook

Production-grade documentation scaffold for a comprehensive Senior Java Backend interview preparation book.

## What this repository includes

- 60 chapter placeholders under `docs/chapters`
- MkDocs Material site with search, dark/light theme toggle, tabs, and Mermaid support
- GitHub Actions for docs build/deploy, export artifact generation, and tagged releases
- VS Code tasks and launch configuration for authoring workflow
- Automation scripts for chapter creation and summary updates
- Companion chapter code folders under `code/chapter01` to `code/chapter60`
- Export directories for HTML, PDF, and EPUB artifacts

## Quick start

1. Create a virtual environment and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Serve docs locally:

```bash
mkdocs serve
```

4. Build docs:

```bash
mkdocs build --strict
```

## Authoring automation

Create a chapter and update summary automatically:

```bash
python scripts/create_chapter.py 61 "Caching Strategies"
```

Regenerate `SUMMARY.md` from current docs structure:

```bash
python scripts/update_summary.py
```

Build export artifacts:

```bash
python scripts/build_pdf.py
```

## CI/CD workflows

- `.github/workflows/docs.yml`: build docs and deploy to GitHub Pages from `main`
- `.github/workflows/pdf.yml`: generate and upload export artifacts
- `.github/workflows/release.yml`: publish tagged zip release artifacts

## Planned content milestone (v2)

- Fully authored chapters with runnable Java 21 and Spring Boot examples
- Rich architecture, sequence, and design diagrams
- Expanded interview Q&A and production troubleshooting scenarios
