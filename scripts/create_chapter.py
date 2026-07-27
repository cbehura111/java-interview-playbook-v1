from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS_DIR = ROOT / "docs" / "chapters"
CODE_DIR = ROOT / "code"
DIAGRAMS_DIR = ROOT / "docs" / "diagrams"
TEMPLATE_FILE = ROOT / "templates" / "chapter.md"


def slugify(text: str) -> str:
	cleaned = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
	return re.sub(r"[\s_-]+", "-", cleaned)


def usage() -> None:
	print("Usage: python scripts/create_chapter.py <chapter_number> [title words...]")


def main() -> int:
	if len(sys.argv) < 2:
		usage()
		return 1

	try:
		chapter_number = int(sys.argv[1])
	except ValueError:
		print("chapter_number must be an integer")
		return 1

	if chapter_number < 1:
		print("chapter_number must be >= 1")
		return 1

	raw_title = " ".join(sys.argv[2:]).strip() or "Topic Pending"
	chapter_slug = slugify(raw_title)
	chapter_file = CHAPTERS_DIR / f"{chapter_number:02d}-chapter-{chapter_slug}.md"
	code_chapter_dir = CODE_DIR / f"chapter{chapter_number:02d}"
	diagram_file = DIAGRAMS_DIR / f"chapter-{chapter_number:02d}-{chapter_slug}.mmd"

	if chapter_file.exists():
		print(f"Chapter file already exists: {chapter_file}")
		return 1

	chapter_template = TEMPLATE_FILE.read_text(encoding="utf-8")
	chapter_content = (
		chapter_template
		.replace("{{NUMBER}}", str(chapter_number))
		.replace("{{TITLE}}", raw_title)
	)

	CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
	chapter_file.write_text(chapter_content, encoding="utf-8")

	code_chapter_dir.mkdir(parents=True, exist_ok=True)
	(code_chapter_dir / "README.md").write_text(
		f"# Chapter {chapter_number:02d} Code\n\nCompanion code for {raw_title}.\n",
		encoding="utf-8",
	)

	DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
	if not diagram_file.exists():
		diagram_file.write_text(
			"""flowchart TD
	A[Context] --> B[Key Decision]
	B --> C[Implementation]
	C --> D[Trade-offs]
""",
			encoding="utf-8",
		)

	subprocess.run([sys.executable, str(ROOT / "scripts" / "update_summary.py")], check=False)

	print(f"Created chapter: {chapter_file}")
	print(f"Created code folder: {code_chapter_dir}")
	print(f"Created diagram: {diagram_file}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
