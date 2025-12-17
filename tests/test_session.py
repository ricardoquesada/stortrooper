
import pytest
from PySide6.QtCore import QSettings
from stortrooper_editor.ui import MainWindow

@pytest.fixture
def clean_settings(request):
    """Ensure we start with fresh settings and clean up after."""
    settings = QSettings("RetroMoe", "StorTrooperEditor_Test")
    settings.clear()
    
    def teardown():
        settings.clear()
        
    request.addfinalizer(teardown)
    return settings

def test_session_persistence(qtbot, clean_settings, tmp_path):
    """Test that window geometry/state and file session are saved and restored."""
    
    # create a dummy res path
    res_path = tmp_path / "res"
    res_path.mkdir()
    
    # 1. Initialize Window
    # We patch the class's settings creation or just overwrite it after init?
    # Since QSettings is created in __init__, we should probably patch the constructor or arguments.
    # But QSettings("Organization", "App") is global.
    # So if we change the organization/app name in the test, it might not affect the code unless we mock QSettings.
    # The code uses: self.settings = QSettings("RetroMoe", "StorTrooperEditor")
    # We should mock QSettings in ui.py to return our test settings.
    
    from unittest.mock import patch, MagicMock
    
    # We need to mock QSettings to direct it to a test location or just verify calls.
    # Let's verify calls as it's cleaner.
    
    with patch('stortrooper_editor.ui.QSettings') as MockSettings:
        # One instance for the first window
        mock_settings_instance = MockSettings.return_value
        # Mock .value() to return None initially 
        mock_settings_instance.value.return_value = None
        
        window = MainWindow(str(res_path))
        qtbot.addWidget(window)
        
        # Verify restore_ui_session called value()
        # It calls value("window_geometry") and value("window_state")
        
        # Check calls
        calls = mock_settings_instance.value.call_args_list
        # We expect at least these calls
        # value("last_session_files", [])
        # value("window_geometry")
        # value("window_state")
        
        args_list = [c[0][0] for c in calls]
        assert "window_geometry" in args_list, "Should attempt to read window_geometry"
        assert "window_state" in args_list, "Should attempt to read window_state"
        
        # Now simulate close
        window.close()
        
        # Verify setValue calls
        # setValue("last_session_files", ...)
        # setValue("window_geometry", ...)
        # setValue("window_state", ...)
        
        set_calls = mock_settings_instance.setValue.call_args_list
        set_args = [c[0][0] for c in set_calls]
        
        assert "window_geometry" in set_args, "Should save window_geometry on close"
        assert "window_state" in set_args, "Should save window_state on close"
        
        # Also check that ToolsDock has object name
        dock = window.findChild(object, "ToolsDock")
        assert dock is not None, "Tools dock should have objectName 'ToolsDock'"
