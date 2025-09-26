"""Pytest configuration and fixtures."""
import sys
from pathlib import Path

# Add the src directory to the Python path
root_dir = Path(__file__).parent.parent
src_dir = root_dir / "src"
sys.path.insert(0, str(src_dir.absolute()))
