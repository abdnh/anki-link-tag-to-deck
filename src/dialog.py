from typing import Any, Dict, List, Optional

from aqt.main import AnkiQt
from aqt.qt import *
from aqt.utils import getOnlyText

from .linked_tags import LinkedTag, configured_tags_for_deck, update_deck_tags


class LinkedTagsDialog(QDialog):
    def __init__(self, mw: AnkiQt, config: Dict[str, Any], deck_name: str) -> None:
        super().__init__(parent=mw)
        self.mw = mw
        self.config = config
        self.deck_name = deck_name
        self.tags: List[LinkedTag] = []
        self.setup_ui()

    def update_tags(self, tags: List[LinkedTag], refresh_widget: bool = True) -> None:
        self.tags = tags
        if refresh_widget:
            self.listwidget.clear()
            for tag in tags:
                self.listwidget.addItem(tag.name)
        update_deck_tags(self.config, self.deck_name, self.tags)
        self.mw.addonManager.writeConfig(__name__, self.config)

    def setup_ui(self) -> None:
        self.setWindowTitle(f"Linked tags of {self.deck_name}")
        main_layout = QHBoxLayout()

        buttons_layout = QVBoxLayout()
        add_button = QPushButton("Add")
        qconnect(add_button.clicked, self.on_add)
        delete_button = QPushButton("Delete")
        qconnect(delete_button.clicked, self.on_delete)
        self.apply_to_subdecks_checkbox = QCheckBox("Apply to subdecks")
        qconnect(
            self.apply_to_subdecks_checkbox.toggled, self.on_apply_to_subdecks_toggled
        )
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(self.apply_to_subdecks_checkbox)
        buttons_parent = QWidget()
        buttons_parent.setLayout(buttons_layout)

        self.listwidget = listwidget = QListWidget()
        self.listwidget.setSortingEnabled(True)
        qconnect(listwidget.currentItemChanged, self.on_selected_changed)
        self.update_tags(configured_tags_for_deck(self.config, self.deck_name))

        main_layout.addWidget(listwidget)
        main_layout.addWidget(buttons_parent)
        self.setLayout(main_layout)

    def on_add(self) -> None:
        new_tag = getOnlyText(prompt="New tag name:")
        if not new_tag:
            return
        self.tags.append(LinkedTag(new_tag, False))
        self.update_tags(self.tags)

    def on_delete(self) -> None:
        selected_tag = self.selected_tag()
        if not selected_tag:
            return
        self.tags.remove(selected_tag)
        self.update_tags(self.tags)

    def on_apply_to_subdecks_toggled(self, checked: bool) -> None:
        selected_tag = self.selected_tag()
        if not selected_tag:
            return
        selected_tag.apply_to_subdecks = checked
        self.tags[self.tags.index(selected_tag)] = selected_tag
        self.update_tags(self.tags, False)

    def selected_tag(self) -> Optional[LinkedTag]:
        if not self.listwidget.currentItem() and not self.listwidget.selectedItems():
            return None
        if self.listwidget.currentItem():
            name = self.listwidget.currentItem().text().lower()
        else:
            name = self.listwidget.selectedItems()[0].text().lower()
        return next((tag for tag in self.tags if tag.name.lower() == name), None)

    def on_selected_changed(
        self, current: QListWidgetItem, previous: QListWidgetItem
    ) -> None:
        selected = self.selected_tag()
        if not selected:
            return
        self.apply_to_subdecks_checkbox.setChecked(selected.apply_to_subdecks)
