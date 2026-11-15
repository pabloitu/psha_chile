import sys
from pathlib import Path

# appended, not prepended: gmm's module names are unique, and other folders also have run.py and figs.py
sys.path.append(str(Path(__file__).resolve().parents[1]))
