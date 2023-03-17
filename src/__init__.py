from typing import cast

import aqt
from aqt import gui_hooks, mw
from aqt.addcards import AddCards
from aqt.deckchooser import DeckChooser
from aqt.qt import *

from .dialog import LinkedTagsDialog
from .linked_tags import linked_tags_for_deck

CONFIG = mw.addonManager.getConfig(__name__)


def on_addcards_deck_changed(addcards: AddCards, deck_name: str) -> None:
    tags = linked_tags_for_deck(CONFIG, deck_name)
    addcards.editor.tags.setText(" ".join(tags))


def add_deck_browser_menu_item(menu: QMenu, deck_id: int) -> None:
    def open_dialog() -> None:
        deck_name = mw.col.decks.name(deck_id)
        dialog = LinkedTagsDialog(mw, CONFIG, deck_name)
        dialog.exec()

    action = QAction("Linked tags", mw)
    qconnect(action.triggered, open_dialog)
    menu.addAction(action)


class MyDeckChooser(DeckChooser):
    deckChanged = pyqtSignal(str)

    def onDeckChange(self) -> None:
        super().onDeckChange()
        self.deckChanged.emit(self.deckName())


def setupChoosers(self: AddCards) -> None:
    self.modelChooser = aqt.modelchooser.ModelChooser(self.mw, self.form.modelArea)
    self.deckChooser = MyDeckChooser(self.mw, self.form.deckArea)
    qconnect(self.deckChooser.deckChanged, lambda d: on_addcards_deck_changed(self, d))


def on_addcards_init(self: AddCards) -> None:
    deckChooser = cast(MyDeckChooser, self.deckChooser)
    deckChooser.deckChanged.emit(deckChooser.deckName())


AddCards.setupChoosers = setupChoosers
gui_hooks.deck_browser_will_show_options_menu.append(add_deck_browser_menu_item)
gui_hooks.add_cards_did_init.append(on_addcards_init)
