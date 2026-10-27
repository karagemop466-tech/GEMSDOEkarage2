"""Compatibility import: canonical unchanged fail-closed writer."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vendor'))
from gems57.submission_writer import write_submission
__all__ = ['write_submission']
