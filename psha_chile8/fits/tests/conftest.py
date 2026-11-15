import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gr as G
import synth as S


@pytest.fixture(scope="session")
def cat():
    return G.load()


@pytest.fixture(scope="session")
def pool(cat):
    return S.pool(cat)
