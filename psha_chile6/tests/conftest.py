import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))


def pytest_configure(config):
    config.addinivalue_line("markers", "data: needs the classified catalog and the Slab2 grids")
    config.addinivalue_line("markers", "built: needs source models built by run.py and fit_check.py")


@pytest.fixture(scope="session")
def paths():
    try:
        import paths as p
    except Exception as e:
        pytest.skip(f"paths.py cannot be imported: {e}")
    return p


@pytest.fixture(scope="session")
def catalog(paths):
    import pandas as pd
    if not paths.CATALOG.exists():
        pytest.skip(f"no {paths.CATALOG}")
    return pd.read_csv(paths.CATALOG, low_memory=False, dtype={"id": str, "dup_ids": str})
