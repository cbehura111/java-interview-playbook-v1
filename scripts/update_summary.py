from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_FILE = ROOT / "SUMMARY.md"
DOCS_DIR = ROOT / "docs"
CHAPTERS_DIR = DOCS_DIR / "chapters"
APPENDICES_DIR = DOCS_DIR / "appendices"


def chapter_sort_key(path: Path) -> tuple[int, str]:
	prefix = path.stem.split("-", 1)[0]
	if prefix.isdigit():
		return int(prefix), path.name
	return 9999, path.name


def render_links(title: str, files: list[Path], base: Path) -> list[str]:
	lines = [f"## {title}", ""]
	for file in files:
		rel = file.relative_to(base).as_posix()
		label = file.stem.replace("-", " ").title()
		lines.append(f"- [{label}]({rel})")
	lines.append("")
	return lines


def main() -> int:
	chapters = sorted(CHAPTERS_DIR.glob("*.md"), key=chapter_sort_key)
	appendices = sorted(APPENDICES_DIR.glob("*.md")) if APPENDICES_DIR.exists() else []

	lines = [
		"# Summary",
		"",
		"- [Home](docs/index.md)",
		"- [Preface](docs/preface.md)",
		"- [Introduction](docs/introduction.md)",
		"- [Roadmap](docs/roadmap.md)",
		"",
	]

	lines.extend(render_links("Chapters", chapters, ROOT))

	if appendices:
		lines.extend(render_links("Appendices", appendices, ROOT))

	SUMMARY_FILE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
	print(f"Updated {SUMMARY_FILE}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
