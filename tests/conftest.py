import os
import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

TEST_DB = Path(tempfile.gettempdir()) / "pocketsmart_test.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_PATH"] = str(TEST_DB)
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-characters"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def pytest_sessionfinish(session, exitstatus):
    if TEST_DB.exists():
        TEST_DB.unlink()
