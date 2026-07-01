import os
from unittest.mock import patch

from stortrooper_editor.ui import MainWindow


class DummySettings:
    def __init__(self):
        self.data = {}

    def value(self, key, default=None):
        return self.data.get(key, default)

    def setValue(self, key, value):
        self.data[key] = value


def test_recent_files_no_duplicates(qtbot, tmp_path):
    # Setup dummy settings and resource path
    res_path = tmp_path / "res"
    res_path.mkdir()

    dummy_settings = DummySettings()

    with patch("stortrooper_editor.ui.QSettings", return_value=dummy_settings):
        window = MainWindow(str(res_path))
        qtbot.addWidget(window)

        file1 = str(tmp_path / "project1.stp")
        file2 = str(tmp_path / "project2.stp")

        # 1. Add files
        window.add_recent_file(file1)
        window.add_recent_file(file2)

        # Verify both are in recent files, with the most recent at the top
        actions = window.recent_menu.actions()
        assert len(actions) == 2
        assert actions[0].data() == os.path.abspath(file2)
        assert actions[1].data() == os.path.abspath(file1)

        # 2. Add file1 again (duplicate check)
        window.add_recent_file(file1)

        # Verify no duplicate, and file1 is now at the top
        actions = window.recent_menu.actions()
        assert len(actions) == 2
        assert actions[0].data() == os.path.abspath(file1)
        assert actions[1].data() == os.path.abspath(file2)

        # 3. Add relative path of file2 and check duplicate prevention / normalization
        rel_file2 = os.path.relpath(file2)
        window.add_recent_file(rel_file2)

        # Verify no duplicate, and file2 is now at the top (with normalized path)
        actions = window.recent_menu.actions()
        assert len(actions) == 2
        assert actions[0].data() == os.path.abspath(file2)
        assert actions[1].data() == os.path.abspath(file1)


def test_recent_files_remove_invalid(qtbot, tmp_path, mocker):
    res_path = tmp_path / "res"
    res_path.mkdir()

    dummy_settings = DummySettings()

    # Mock QMessageBox.critical to prevent popup blocking tests
    mock_critical = mocker.patch("PySide6.QtWidgets.QMessageBox.critical")

    with patch("stortrooper_editor.ui.QSettings", return_value=dummy_settings):
        window = MainWindow(str(res_path))
        qtbot.addWidget(window)

        invalid_file = str(tmp_path / "non_existent.stp")
        window.add_recent_file(invalid_file)

        # Confirm it is in the recent menu
        actions = window.recent_menu.actions()
        assert len(actions) == 1
        assert actions[0].data() == os.path.abspath(invalid_file)

        # Try to open the invalid file
        success = window.open_project_file(invalid_file)

        # Should fail and call QMessageBox.critical
        assert not success
        mock_critical.assert_called_once()

        # Verify the invalid file is removed from the recent menu/settings
        actions = window.recent_menu.actions()
        assert len(actions) == 0
        assert len(window.settings.value("recent_files", [])) == 0
