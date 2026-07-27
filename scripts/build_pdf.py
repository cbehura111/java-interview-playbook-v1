from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
EXPORTS_DIR = ROOT / "exports"
PDF_DIR = EXPORTS_DIR / "pdf"
HTML_DIR = EXPORTS_DIR / "html"


def run(cmd: list[str]) -> int:
	print("Running:", " ".join(cmd))
	completed = subprocess.run(cmd, cwd=ROOT, check=False)
	return completed.returncode


def main() -> int:
	PDF_DIR.mkdir(parents=True, exist_ok=True)
	HTML_DIR.mkdir(parents=True, exist_ok=True)

	code = run([sys.executable, "-m", "mkdocs", "build", "-d", str(HTML_DIR)])
	if code != 0:
		print("mkdocs build failed")
		return code

	placeholder = PDF_DIR / "README.md"
	placeholder.write_text(
		"# PDF Export\n\n"
		"PDF generation depends on your selected converter (for example WeasyPrint or Pandoc).\n"
		"The HTML site has been built in exports/html and is ready for conversion.\n",
		encoding="utf-8",
	)
	print(f"Build completed: HTML output at {HTML_DIR}")
	print(f"PDF instructions written to {placeholder}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
