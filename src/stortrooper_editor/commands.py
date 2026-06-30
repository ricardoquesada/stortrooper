# Copyright (c) 2026 Ricardo Quesada
# All rights reserved.

import random

from PySide6.QtGui import QUndoCommand

from .model import CharacterData


class EquipArticleCommand(QUndoCommand):
    def __init__(self, canvas, article):
        super().__init__(f"Equip {article.image_name}")
        self.canvas = canvas
        self.article = article
        self.old_article = None
        self.old_had_article = False

    def redo(self):
        self.old_had_article = self.article.layer_name in self.canvas.active_articles
        if self.old_had_article:
            self.old_article = self.canvas.active_articles[self.article.layer_name]

        self.canvas.update_article(self.article)

    def undo(self):
        if self.old_had_article:
            self.canvas.update_article(self.old_article)
        else:
            self.canvas.remove_article(self.article)


class UnequipArticleCommand(QUndoCommand):
    def __init__(self, canvas, article):
        super().__init__(f"Unequip {article.image_name}")
        self.canvas = canvas
        self.article = article

    def redo(self):
        self.canvas.remove_article(self.article)

    def undo(self):
        self.canvas.update_article(self.article)


class TintArticleCommand(QUndoCommand):
    def __init__(self, canvas, article, new_tint):
        action_name = (
            f"Tint {article.image_name}"
            if new_tint
            else f"Reset Tint {article.image_name}"
        )
        super().__init__(action_name)
        self.canvas = canvas
        self.article = article
        self.new_tint = new_tint
        self.old_tint = article.tint

    def redo(self):
        self.canvas.set_article_tint(self.article, self.new_tint)

    def undo(self):
        self.canvas.set_article_tint(self.article, self.old_tint)


class RandomizeCommand(QUndoCommand):
    def __init__(self, main_window, canvas):
        super().__init__("Randomize Character")
        self.main_window = main_window
        self.canvas = canvas

        self.old_char_data = canvas.character_data
        self.old_active = [
            (art.id, art.tint) for art in canvas.active_articles.values()
        ]

        self.new_char_name = None
        self.new_articles_file = None
        self.new_outfit_ids = []

        if main_window.char_combo.count() > 0:
            char_idx = random.randint(0, main_window.char_combo.count() - 1)
            self.new_char_name = main_window.char_combo.itemText(char_idx)
        else:
            self.new_char_name = canvas.character_data.name

        files = CharacterData.get_available_article_files(
            main_window.res_path, self.new_char_name
        )
        if files:
            self.new_articles_file = random.choice(files)
        else:
            self.new_articles_file = "articles.txt"

        temp_char_data = CharacterData(
            self.new_char_name, main_window.res_path, self.new_articles_file
        )
        temp_char_data.load()
        new_outfit = temp_char_data.get_random_outfit()
        self.new_outfit_ids = [art.id for art in new_outfit]
        self.new_char_data = temp_char_data

    def redo(self):
        self.canvas.set_character(self.new_char_data)
        self.canvas.clear()
        for art_id in self.new_outfit_ids:
            article = self.new_char_data.get_article_by_id(art_id)
            if article:
                self.canvas.update_article(article)

        self.main_window.synchronize_ui_with_canvas(self.canvas)

    def undo(self):
        self.canvas.set_character(self.old_char_data)
        self.canvas.clear()
        for art_id, tint in self.old_active:
            article = self.old_char_data.get_article_by_id(art_id)
            if article:
                article.tint = tint
                self.canvas.update_article(article)

        self.main_window.synchronize_ui_with_canvas(self.canvas)


class ChangeOutfitCommand(QUndoCommand):
    def __init__(self, main_window, canvas):
        super().__init__("Change Outfit")
        self.main_window = main_window
        self.canvas = canvas

        self.old_active = [
            (art.id, art.tint) for art in canvas.active_articles.values()
        ]

        all_categories = list(canvas.character_data.categories.keys())
        excluded = ["body", "hair", "face", "head"]
        target_categories = [c for c in all_categories if c not in excluded]

        new_articles = canvas.character_data.get_random_articles_subset(
            target_categories
        )

        self.new_active = []
        for art in canvas.active_articles.values():
            if art.category in excluded:
                self.new_active.append((art.id, art.tint))
        for art in new_articles:
            self.new_active.append((art.id, None))

    def redo(self):
        self._apply_active(self.new_active)

    def undo(self):
        self._apply_active(self.old_active)

    def _apply_active(self, active_list):
        self.canvas.clear()
        for art_id, tint in active_list:
            article = self.canvas.character_data.get_article_by_id(art_id)
            if article:
                article.tint = tint
                self.canvas.update_article(article)
        self.main_window.synchronize_ui_with_canvas(self.canvas)


class ChangeCharacterDataCommand(QUndoCommand):
    def __init__(self, main_window, canvas, new_char_name, new_articles_file):
        super().__init__(f"Change Character to {new_char_name}")
        self.main_window = main_window
        self.canvas = canvas

        self.old_char_data = (
            canvas.character_data if hasattr(canvas, "character_data") else None
        )
        self.old_active = (
            [(art.id, art.tint) for art in canvas.active_articles.values()]
            if hasattr(canvas, "active_articles")
            else []
        )

        self.new_char_data = CharacterData(
            new_char_name, main_window.res_path, new_articles_file
        )
        self.new_char_data.load()

        self.new_active = []
        if "body" in self.new_char_data.categories:
            first_body = self.new_char_data.categories["body"][0]
            self.new_active.append((first_body.id, None))

    def redo(self):
        self.canvas.set_character(self.new_char_data)
        self.canvas.clear()
        for art_id, tint in self.new_active:
            article = self.new_char_data.get_article_by_id(art_id)
            if article:
                article.tint = tint
                self.canvas.update_article(article)
        self.main_window.synchronize_ui_with_canvas(self.canvas)

    def undo(self):
        if self.old_char_data:
            self.canvas.set_character(self.old_char_data)
            self.canvas.clear()
            for art_id, tint in self.old_active:
                article = self.old_char_data.get_article_by_id(art_id)
                if article:
                    article.tint = tint
                    self.canvas.update_article(article)
        else:
            self.canvas.clear()
            if hasattr(self.canvas, "character_data"):
                self.canvas.character_data = None
        self.main_window.synchronize_ui_with_canvas(self.canvas)
