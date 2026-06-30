# Copyright (c) 2026 Ricardo Quesada
# All rights reserved.

import os

import pytest
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QMessageBox

from stortrooper_editor.commands import (
    ChangeCharacterDataCommand,
    EquipArticleCommand,
    TintArticleCommand,
    UnequipArticleCommand,
)
from stortrooper_editor.ui import MainWindow


@pytest.fixture
def valid_res_path(tmp_path):
    """Creates a temporary resource directory structure with valid PNGs for testing."""
    res = tmp_path / "res"
    res.mkdir()

    # Create two character directories to support randomize testing
    for char_name in ["hero", "sidekick"]:
        char_dir = res / char_name
        char_dir.mkdir()

        # Create articles.txt
        articles_content = """
        # This is a comment
        "HCDataSetFile_data" "1.0"

        "1" "body.png" "body" "body" "0" "0" "-1"
        "2" "shirt_a.png" "tops" "tops" "10" "20" "-1"
        "3" "shirt_b.png" "tops" "tops" "10" "20" "-1"
        """
        (char_dir / "articles.txt").write_text(articles_content, encoding="utf-8")

        # Create data directory and valid images
        data_dir = char_dir / "data"
        data_dir.mkdir()

        for img_name in ["body.png", "shirt_a.png", "shirt_b.png"]:
            img = QImage(10, 10, QImage.Format_ARGB32)
            img.fill(QColor("red" if char_name == "hero" else "blue"))
            img.save(str(data_dir / img_name))

    return str(res)


def test_equip_unequip_undo_redo(qtbot, valid_res_path):
    """Test equipping and unequipping articles with undo/redo."""
    window = MainWindow(valid_res_path)
    qtbot.addWidget(window)
    window.show()

    canvas = window.get_current_canvas()
    assert canvas is not None

    # Initially, body (id: 1) is equipped by default in reload_data
    body = canvas.character_data.get_article_by_id("1")
    assert canvas.is_article_active(body)

    # Let's equip shirt_a (id: 2)
    shirt_a = canvas.character_data.get_article_by_id("2")
    assert not canvas.is_article_active(shirt_a)

    # Push Equip Command
    command = EquipArticleCommand(canvas, shirt_a)
    canvas.undo_stack.push(command)
    assert canvas.is_article_active(shirt_a)

    # Undo
    canvas.undo_stack.undo()
    assert not canvas.is_article_active(shirt_a)

    # Redo
    canvas.undo_stack.redo()
    assert canvas.is_article_active(shirt_a)

    # Push Unequip Command
    command2 = UnequipArticleCommand(canvas, shirt_a)
    canvas.undo_stack.push(command2)
    assert not canvas.is_article_active(shirt_a)

    # Undo Unequip
    canvas.undo_stack.undo()
    assert canvas.is_article_active(shirt_a)

    # Redo Unequip
    canvas.undo_stack.redo()
    assert not canvas.is_article_active(shirt_a)

    canvas.undo_stack.clear()


def test_replace_article_undo_redo(qtbot, valid_res_path):
    """Test replacing an article (equipping another on the same layer) with undo/redo."""
    window = MainWindow(valid_res_path)
    qtbot.addWidget(window)
    window.show()

    canvas = window.get_current_canvas()
    shirt_a = canvas.character_data.get_article_by_id("2")
    shirt_b = canvas.character_data.get_article_by_id("3")

    # Equip shirt_a
    canvas.undo_stack.push(EquipArticleCommand(canvas, shirt_a))
    assert canvas.is_article_active(shirt_a)
    assert not canvas.is_article_active(shirt_b)

    # Equip shirt_b (replaces shirt_a)
    canvas.undo_stack.push(EquipArticleCommand(canvas, shirt_b))
    assert not canvas.is_article_active(shirt_a)
    assert canvas.is_article_active(shirt_b)

    # Undo (should restore shirt_a)
    canvas.undo_stack.undo()
    assert canvas.is_article_active(shirt_a)
    assert not canvas.is_article_active(shirt_b)

    # Redo (should replace with shirt_b again)
    canvas.undo_stack.redo()
    assert not canvas.is_article_active(shirt_a)
    assert canvas.is_article_active(shirt_b)

    canvas.undo_stack.clear()


def test_tint_undo_redo(qtbot, valid_res_path):
    """Test tinting and resetting tint with undo/redo."""
    window = MainWindow(valid_res_path)
    qtbot.addWidget(window)
    window.show()

    canvas = window.get_current_canvas()
    body = canvas.character_data.get_article_by_id("1")

    # Initially, no tint
    assert body.tint is None

    # Apply Tint
    canvas.undo_stack.push(TintArticleCommand(canvas, body, "#ff0000"))
    assert body.tint == "#ff0000"

    # Undo
    canvas.undo_stack.undo()
    assert body.tint is None

    # Redo
    canvas.undo_stack.redo()
    assert body.tint == "#ff0000"

    # Reset Tint
    canvas.undo_stack.push(TintArticleCommand(canvas, body, None))
    assert body.tint is None

    # Undo Reset
    canvas.undo_stack.undo()
    assert body.tint == "#ff0000"

    canvas.undo_stack.clear()


def test_randomize_undo_redo(qtbot, valid_res_path):
    """Test full character randomization with undo/redo."""
    window = MainWindow(valid_res_path)
    qtbot.addWidget(window)
    window.show()

    canvas = window.get_current_canvas()
    initial_char_name = canvas.character_data.name
    initial_active = [(art.id, art.tint) for art in canvas.active_articles.values()]

    # Trigger Randomize via menu action/method
    window.randomize_character()

    # The character or outfit should have changed (since we have multiple options)
    # Let's verify that we can undo it
    assert canvas.undo_stack.canUndo()

    # Undo
    canvas.undo_stack.undo()
    assert canvas.character_data.name == initial_char_name
    current_active = [(art.id, art.tint) for art in canvas.active_articles.values()]
    assert current_active == initial_active

    # Redo
    canvas.undo_stack.redo()
    # Should be back to the randomized state
    assert canvas.undo_stack.canUndo()

    canvas.undo_stack.clear()


def test_change_outfit_undo_redo(qtbot, valid_res_path):
    """Test change outfit with undo/redo."""
    window = MainWindow(valid_res_path)
    qtbot.addWidget(window)
    window.show()

    canvas = window.get_current_canvas()

    # Let's equip shirt_a first
    shirt_a = canvas.character_data.get_article_by_id("2")
    canvas.undo_stack.push(EquipArticleCommand(canvas, shirt_a))
    assert canvas.is_article_active(shirt_a)

    # Change outfit
    window.change_outfit()

    # The outfit should have changed.
    # Verify we can undo
    assert canvas.undo_stack.canUndo()

    # Undo
    canvas.undo_stack.undo()
    assert canvas.is_article_active(shirt_a)

    # Redo
    canvas.undo_stack.redo()
    assert canvas.undo_stack.canUndo()

    canvas.undo_stack.clear()


def test_dirty_tab_indicator(qtbot, valid_res_path):
    """Test that tab title correctly updates with '*' when dirty."""
    window = MainWindow(valid_res_path)
    qtbot.addWidget(window)
    window.show()

    canvas = window.get_current_canvas()
    assert window.tab_widget.tabText(0) == "Untitled"

    # Make a change (Equip shirt_a)
    shirt_a = canvas.character_data.get_article_by_id("2")
    canvas.undo_stack.push(EquipArticleCommand(canvas, shirt_a))
    assert window.tab_widget.tabText(0) == "Untitled *"

    # Undo
    canvas.undo_stack.undo()
    assert window.tab_widget.tabText(0) == "Untitled"

    # Redo
    canvas.undo_stack.redo()
    assert window.tab_widget.tabText(0) == "Untitled *"

    canvas.undo_stack.clear()


def test_close_dirty_tab_cancel(qtbot, valid_res_path, mocker):
    """Test that cancelling the save warning prevents the tab from closing."""
    window = MainWindow(valid_res_path)
    qtbot.addWidget(window)
    window.show()

    canvas = window.get_current_canvas()
    shirt_a = canvas.character_data.get_article_by_id("2")
    canvas.undo_stack.push(EquipArticleCommand(canvas, shirt_a))

    # Mock QMessageBox.warning to return Cancel
    mock_warning = mocker.patch(
        "PySide6.QtWidgets.QMessageBox.warning", return_value=QMessageBox.Cancel
    )

    # Try to close tab
    window.on_tab_close_requested(0)

    # Verify QMessageBox was shown and tab was NOT closed
    mock_warning.assert_called_once()
    assert window.tab_widget.count() == 1

    canvas.undo_stack.clear()


def test_close_dirty_tab_discard(qtbot, valid_res_path, mocker):
    """Test that choosing Discard closes the tab without saving."""
    window = MainWindow(valid_res_path)
    qtbot.addWidget(window)
    window.show()

    canvas = window.get_current_canvas()
    shirt_a = canvas.character_data.get_article_by_id("2")
    canvas.undo_stack.push(EquipArticleCommand(canvas, shirt_a))

    # Mock QMessageBox.warning to return Discard
    mock_warning = mocker.patch(
        "PySide6.QtWidgets.QMessageBox.warning", return_value=QMessageBox.Discard
    )

    # Try to close tab
    window.on_tab_close_requested(0)

    # Verify tab was closed
    mock_warning.assert_called_once()
    assert window.tab_widget.count() == 0


def test_close_dirty_tab_save(qtbot, valid_res_path, mocker, tmp_path):
    """Test that choosing Save saves the project and closes the tab."""
    window = MainWindow(valid_res_path)
    qtbot.addWidget(window)
    window.show()

    canvas = window.get_current_canvas()
    shirt_a = canvas.character_data.get_article_by_id("2")
    canvas.undo_stack.push(EquipArticleCommand(canvas, shirt_a))

    # Mock QMessageBox.warning to return Save
    mock_warning = mocker.patch(
        "PySide6.QtWidgets.QMessageBox.warning", return_value=QMessageBox.Save
    )

    # Mock QFileDialog.getSaveFileName to return a valid path
    save_file = tmp_path / "saved_project.stp"
    mock_save_dialog = mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getSaveFileName",
        return_value=(str(save_file), ""),
    )

    # Mock QMessageBox.information (success dialog)
    mocker.patch("PySide6.QtWidgets.QMessageBox.information")

    # Try to close tab
    window.on_tab_close_requested(0)

    # Verify it was saved and closed
    mock_warning.assert_called_once()
    mock_save_dialog.assert_called_once()
    assert os.path.exists(save_file)
    assert window.tab_widget.count() == 0


def test_change_character_data_undo_redo(qtbot, valid_res_path):
    """Test changing character and articles file with undo/redo."""
    window = MainWindow(valid_res_path)
    qtbot.addWidget(window)
    window.show()

    canvas = window.get_current_canvas()
    assert canvas.character_data.name == "hero"

    # Change character to 'sidekick'
    command = ChangeCharacterDataCommand(window, canvas, "sidekick", "articles.txt")
    canvas.undo_stack.push(command)

    assert canvas.character_data.name == "sidekick"
    assert window.char_combo.currentText() == "sidekick"

    # Undo
    canvas.undo_stack.undo()
    assert canvas.character_data.name == "hero"
    assert window.char_combo.currentText() == "hero"

    # Redo
    canvas.undo_stack.redo()
    assert canvas.character_data.name == "sidekick"
    assert window.char_combo.currentText() == "sidekick"

    canvas.undo_stack.clear()
