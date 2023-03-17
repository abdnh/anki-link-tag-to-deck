import dataclasses
from typing import Any, Dict, List


@dataclasses.dataclass
class LinkedTag:
    name: str
    apply_to_subdecks: bool


def linked_tags_for_deck(config: Dict[str, Any], deck_name: str) -> List[str]:
    """Return all tag names that should be linked to a given deck"""
    tags: List[str] = []
    deck_name = deck_name.lower()
    for deck in config["decks"]:
        if deck_name == deck["name"].lower():
            tags.extend((tag["name"] for tag in deck.get("tags", [])))
        elif deck_name.startswith(f'{deck["name"].lower()}::'):
            tags.extend(
                (tag["name"] for tag in deck.get("tags") if tag["apply_to_subdecks"])
            )

    return tags


def configured_tags_for_deck(config: Dict[str, Any], deck_name: str) -> List[LinkedTag]:
    """Return tags configured for given deck, not considering tags applying indirectly via parent decks"""
    deck_name = deck_name.lower()
    tag_dicts: List[Dict] = next(
        (
            deck.get("tags", [])
            for deck in config["decks"]
            if deck_name == deck["name"].lower()
        ),
        [],
    )
    tags = [LinkedTag(**d) for d in tag_dicts]

    return tags


def update_deck_tags(
    config: Dict[str, Any], deck_name: str, tags: List[LinkedTag]
) -> None:
    deck_name = deck_name.lower()
    for deck in config["decks"]:
        assert isinstance(deck, Dict)
        if deck_name == deck["name"].lower():
            deck.setdefault("tags", [])
            deck["tags"].clear()
            deck["tags"].extend(dataclasses.asdict(tag) for tag in tags)
            return

    deck = {"name": deck_name, "tags": [dataclasses.asdict(tag) for tag in tags]}
    config["decks"].append(deck)
