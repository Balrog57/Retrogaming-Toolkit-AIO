
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Adjust path so we can import from Retrogaming-Toolkit-AIO
sys.path.append(os.path.abspath("Retrogaming-Toolkit-AIO"))

# Mock 'requests' and 'customtkinter' before importing utils
sys.modules['requests'] = MagicMock()
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()

# Now we can import utils
import utils

class TestUtilsBug(unittest.TestCase):

    def test_startupinfo_bug_on_posix(self):
        """
        Reproduce the bug where subprocess.STARTUPINFO is accessed on POSIX systems
        in extract_with_7za and DependencyManager.
        """
        # We need to simulate a POSIX environment where STARTUPINFO does not exist
        # However, we are running on Linux (likely), so it already doesn't exist.
        # The code in utils.py uses subprocess.STARTUPINFO() unconditionally.

        # We need to mock DependencyManager.bootstrap_7za to return True
        # so it proceeds to the subprocess call.

        with patch.object(utils.DependencyManager, 'bootstrap_7za', return_value=True):
             with patch.object(utils.DependencyManager, '__init__', return_value=None):
                 # We need to mock the instance created inside extract_with_7za
                 # but since we patched __init__, we need to set attributes manually if needed.
                 # Wait, extract_with_7za creates a new DependencyManager.

                 # Let's just try to call extract_with_7za and see it fail with AttributeError
                 # We need to mock subprocess.run so we don't actually run anything,
                 # but the error happens BEFORE subprocess.run, when creating startupinfo.

                 # On Linux, accessing subprocess.STARTUPINFO raises AttributeError.
                 # Let's verify that the code *does* access it.

                 # We need to mock manager.seven_za_path since we bypassed __init__
                 with patch('utils.DependencyManager') as MockManager:
                     instance = MockManager.return_value
                     instance.bootstrap_7za.return_value = True
                     instance.seven_za_path = "dummy_7za"

                     # We need to reload utils or unimport it to ensure we aren't using cached version?
                     # No, we are testing the function directly.

                     # But wait, extract_with_7za instantiates DependencyManager(root).
                     # So patching utils.DependencyManager should work.

                     with patch('subprocess.run') as mock_run:
                        try:
                            utils.extract_with_7za("dummy.zip", "output_dir")
                        except AttributeError as e:
                            # We DO NOT expect "module 'subprocess' has no attribute 'STARTUPINFO'" anymore
                            self.fail(f"Caught AttributeError (fix failed): {e}")

                        # Ensure subprocess.run was called
                        mock_run.assert_called_once()

                        # Ensure startupinfo was NOT passed (or is None) if on posix
                        # But wait, startupinfo argument is always passed, but it should be None on Posix?
                        # No, if we look at the code:
                        # startupinfo = None
                        # if os.name == 'nt': ...
                        # subprocess.run(..., startupinfo=startupinfo, ...)

                        args, kwargs = mock_run.call_args
                        self.assertIn('startupinfo', kwargs)
                        if os.name != 'nt':
                            self.assertIsNone(kwargs['startupinfo'])

    def test_dependency_manager_init_crash(self):
        """
        Ensure DependencyManager.__init__ does NOT crash when LOCALAPPDATA is missing.
        """
        # Save original environ
        original_env = os.environ.copy()
        if 'LOCALAPPDATA' in os.environ:
            del os.environ['LOCALAPPDATA']

        try:
            # This previously raised TypeError. Now it should succeed.
            manager = utils.DependencyManager()

            # Verify the fallback path is set correctly (ending in RetrogamingToolkit)
            # and is under .local/share if HOME is set, but we didn't check HOME.
            # Just checking that it didn't crash is the main point.
            self.assertIsNotNone(manager.app_data_dir)
            self.assertTrue(manager.app_data_dir.endswith('RetrogamingToolkit'))

        except TypeError as e:
            self.fail(f"Caught TypeError (fix failed): {e}")
        except Exception as e:
            self.fail(f"Caught unexpected exception: {type(e).__name__}: {e}")
        finally:
            os.environ.update(original_env)

if __name__ == '__main__':
    unittest.main()
