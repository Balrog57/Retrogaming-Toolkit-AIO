import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure we can import utils
sys.path.append(os.path.abspath("Retrogaming-Toolkit-AIO"))

# Mock customtkinter before importing utils to avoid GUI issues
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['requests'] = MagicMock() # Mock requests too

import utils

class TestUtilsSecurity(unittest.TestCase):
    @patch('subprocess.run')
    @patch('utils.DependencyManager.bootstrap_7za', return_value=True)
    def test_extract_with_7za_uses_double_dash(self, mock_bootstrap, mock_run):
        """
        Verify that extract_with_7za uses '--' to prevent argument injection.
        """
        os.environ['LOCALAPPDATA'] = '/tmp' # Mock LOCALAPPDATA for test

        archive_path = "archive.7z"
        output_dir = "out"

        utils.extract_with_7za(archive_path, output_dir)

        # Check args
        self.assertTrue(mock_run.called)
        args, kwargs = mock_run.call_args
        cmd = args[0]

        print(f"Command called: {cmd}")

        # Expectation: cmd should contain '--' before archive_path
        self.assertIn('--', cmd, "Command is missing '--' delimiter")

        idx_dash = cmd.index('--')
        idx_arch = cmd.index(archive_path)

        self.assertLess(idx_dash, idx_arch, "Archive path should appear after '--'")

        # Ensure switches are before '--'
        for arg in cmd:
            if arg.startswith('-') and arg != '--' and arg != archive_path: # archive_path is not starting with - here but generally checking logic
                idx_arg = cmd.index(arg)
                # If arg is before --, fine. If after, problem.
                if idx_arg > idx_dash:
                    self.fail(f"Switch {arg} found after '--'")

    @patch('subprocess.run')
    @patch('utils.DependencyManager.bootstrap_7za', return_value=True)
    @patch('utils.DependencyManager.download_with_progress')
    @patch('tempfile.mkdtemp', return_value="temp_dir")
    @patch('shutil.move')
    @patch('os.walk')
    @patch('os.path.exists')
    @patch('shutil.rmtree')
    @patch('os.remove')
    @patch('os.makedirs')
    def test_install_dependency_uses_double_dash(self, mock_makedirs, mock_remove, mock_rmtree, mock_exists, mock_walk, mock_move, mock_mkdtemp, mock_dl, mock_bootstrap, mock_run):
        """
        Verify that install_dependency uses '--' to prevent argument injection.
        """
        # Force install path
        mock_exists.return_value = False

        # Mock os.walk to find the file so it doesn't fail
        mock_walk.return_value = [("temp_dir", [], ["target.exe"])]

        manager = utils.DependencyManager()

        with patch('utils.get_binary_path', return_value="/nonexistent/path"):
             manager.install_dependency("TestDep", "http://example.com/dep.zip", "target.exe")

        self.assertTrue(mock_run.called)
        args, kwargs = mock_run.call_args
        cmd = args[0]

        print(f"Install Command called: {cmd}")
        self.assertIn('--', cmd, "Command is missing '--' delimiter")

        idx_dash = cmd.index('--')
        # Find archive argument (ends with .7z or .zip from code logic)
        # install_dependency uses archive_type='7z' by default
        archive_arg = None
        for arg in cmd:
            if 'temp_dep_target.exe.7z' in arg:
                archive_arg = arg
                break

        self.assertIsNotNone(archive_arg)
        idx_arch = cmd.index(archive_arg)
        self.assertLess(idx_dash, idx_arch, "Archive path should appear after '--'")

if __name__ == '__main__':
    unittest.main()
