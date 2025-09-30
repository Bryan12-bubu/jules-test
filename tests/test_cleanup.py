import os
import time
import shutil

# Correctly import from the 'app' package
from app.main import cleanup_temp_files

def test_cleanup_temp_files(tmp_path, monkeypatch):
    """
    Tests the file cleanup logic using pytest fixtures for isolation.
    - Creates one new file and one old file in a temporary directory.
    - Runs the cleanup function.
    - Asserts that the old file is deleted and the new one remains.
    """
    # Arrange: Use monkeypatch to set constants for this test only
    monkeypatch.setattr('app.main.MAX_FILE_AGE_SECONDS', 60) # 1 minute
    monkeypatch.setattr('app.main.TEMP_DIR', str(tmp_path))

    temp_dir = str(tmp_path)
    new_file_path = os.path.join(temp_dir, "new_file.txt")
    old_file_path = os.path.join(temp_dir, "old_file.txt")

    # Create a new file (modification time is now)
    with open(new_file_path, "w") as f:
        f.write("new")

    # Create an old file
    with open(old_file_path, "w") as f:
        f.write("old")

    # Set the old file's modification time to be in the past (e.g., 120 seconds ago)
    two_minutes_ago = time.time() - 120
    os.utime(old_file_path, (two_minutes_ago, two_minutes_ago))

    # Act
    cleanup_temp_files()

    # Assert
    assert os.path.exists(new_file_path)
    assert not os.path.exists(old_file_path)
