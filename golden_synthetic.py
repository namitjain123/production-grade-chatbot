from pathlib import Path

from dotenv import load_dotenv
from deepeval.synthesizer import Synthesizer

load_dotenv()

SOURCE_DIR = Path(__file__).parent / "DATA" / "true_data_new"
OUTPUT_DIR = Path(__file__).parent / "DATA" / "golden_dataset"

# Docs deepeval's Synthesizer knows how to load. Other extensions (.html, .png) are skipped.
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".md", ".txt", ".mdx"]


def collect_document_paths(directory: Path) -> list[str]:
    # A single crawl saves the same content as .md/.txt/.pdf/etc; keep one per basename
    # so the same article isn't fed in multiple times as duplicate context.
    by_stem: dict[str, Path] = {}
    for file in sorted(directory.iterdir()):
        ext = file.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            continue
        existing = by_stem.get(file.stem)
        if existing is None or SUPPORTED_EXTENSIONS.index(ext) < SUPPORTED_EXTENSIONS.index(existing.suffix.lower()):
            by_stem[file.stem] = file
    return [str(path) for path in by_stem.values()]


document_paths = collect_document_paths(SOURCE_DIR)
if not document_paths:
    raise FileNotFoundError(f"No supported documents found in {SOURCE_DIR}")

synthesizer = Synthesizer()
goldens = synthesizer.generate_goldens_from_docs(
    document_paths=document_paths,
    include_expected_output=True,
)

synthesizer.save_as(file_type="json", directory=str(OUTPUT_DIR))
