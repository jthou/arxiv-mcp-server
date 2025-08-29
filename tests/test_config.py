"""Tests for the configuration module."""

import os
import sys
from pathlib import Path
from arxiv_mcp_server.config import Settings, reset_settings
from unittest.mock import patch


@patch.object(Path, "mkdir")
@patch.object(Path, "resolve")
def test_storage_path_default(mock_resolve, mock_mkdir):
    """Test that the default storage path is correctly constructed."""
    # 重置配置实例
    reset_settings()
    
    # Setup the mock to return the path itself when resolved
    mock_resolve.side_effect = lambda: Path.home() / ".arxiv-mcp-server" / "papers"

    settings = Settings()
    expected_path = Path.home() / ".arxiv-mcp-server" / "papers"
    assert settings.STORAGE_PATH == expected_path.resolve()
    # Verify mkdir was called with parents=True and exist_ok=True
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


@patch.object(Path, "mkdir")
def test_storage_path_from_args(mock_mkdir):
    """Test that the storage path from command line args is correctly parsed."""
    test_path = "/tmp/test_storage"
    
    # 保存原始的sys.argv
    original_argv = sys.argv.copy()
    
    try:
        # 设置命令行参数
        sys.argv = ["program", "--storage-path", test_path]
        
        # 重置配置实例
        reset_settings()
        
        settings = Settings()
        assert str(settings.STORAGE_PATH) == test_path
        
        # Verify mkdir was called with parents=True and exist_ok=True
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    finally:
        # 恢复原始的sys.argv
        sys.argv = original_argv


@patch.object(Path, "mkdir")
def test_storage_path_platform_compatibility(mock_mkdir):
    """Test that the storage path works correctly on different platforms."""
    # Test with a path format that would be valid on both Windows and Unix
    test_paths = [
        # Unix-style path
        "/path/to/storage",
        # Path with spaces
        "/path with spaces/to/storage",
    ]

    # 保存原始的sys.argv
    original_argv = sys.argv.copy()
    
    try:
        for test_path in test_paths:
            # Reset mocks for each iteration
            mock_mkdir.reset_mock()

            # 设置命令行参数
            sys.argv = ["program", "--storage-path", test_path]
            
            # 重置配置实例
            reset_settings()
            
            settings = Settings()
            resolved_path = settings.STORAGE_PATH

            # Verify that the path is correctly set
            assert str(resolved_path) == test_path

            # Verify that mkdir was called
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    finally:
        # 恢复原始的sys.argv
        sys.argv = original_argv


def test_storage_path_creates_missing_directory():
    """Test that directories are actually created for the storage path."""
    import tempfile

    # Create a temporary directory for our test
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a path that doesn't exist yet
        test_path = os.path.join(tmpdir, "deeply", "nested", "directory", "structure")

        # Make sure it doesn't exist yet
        assert not os.path.exists(test_path)

        # 保存原始的sys.argv
        original_argv = sys.argv.copy()
        
        try:
            # 设置命令行参数
            sys.argv = ["program", "--storage-path", test_path]
            
            # 重置配置实例
            reset_settings()
            
            # Access the STORAGE_PATH property which should create the directories
            settings = Settings()
            storage_path = settings.STORAGE_PATH

            # Verify the directory was created
            assert os.path.exists(test_path)
            assert os.path.isdir(test_path)

            # Verify the paths refer to the same location
            # Use Path.samefile to handle symlinks (like /var -> /private/var on macOS)
            assert Path(storage_path).samefile(test_path)
        finally:
            # 恢复原始的sys.argv
            sys.argv = original_argv


def test_path_normalization_with_windows_paths():
    """Test Windows-specific path handling using string operations only."""
    # Windows-style paths - we'll test the normalization and joining logic
    windows_style_paths = [
        # Drive letter with backslashes
        "C:\\Users\\username\\Documents\\Papers",
        # Drive letter with forward slashes (also valid on Windows)
        "C:/Users/username/Documents/Papers",
        # Windows-style path with spaces
        "C:\\Program Files\\arXiv\\papers",
    ]

    # Test that our config works with these path formats
    for windows_path in windows_style_paths:
        assert Path(windows_path)  # This should not raise an error

        # Test path joining logic works correctly
        subpath = Path(windows_path) / "subdir"
        assert str(subpath).endswith("subdir")

        # The following check is problematic on real Windows systems
        # where the path separator may be different
        # Check only that the base path is contained in the result (ignoring separator differences)
        base_path_norm = windows_path.replace("\\", "/").replace("//", "/")
        subpath_norm = str(subpath).replace("\\", "/").replace("//", "/")
        assert base_path_norm in subpath_norm

        # Instead of checking exact string equality, verify the Path objects are equivalent
        assert subpath == Path(windows_path).joinpath("subdir")