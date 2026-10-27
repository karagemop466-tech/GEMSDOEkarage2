"""Compatibility import: one shared evaluator, no private scoring implementation."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vendor'))
from gems57.evaluate_holdout import evaluate, pooled_summary, VERSION
__all__ = ['evaluate', 'pooled_summary', 'VERSION']
