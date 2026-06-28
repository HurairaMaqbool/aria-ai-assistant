import os
import tempfile
from pathlib import Path

_test_root = Path(tempfile.mkdtemp(prefix="aria_pytest_"))
os.environ.setdefault("ARIA_DATA_DIR", str(_test_root))
