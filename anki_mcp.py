"""Anki MCP Server — manage Anki flashcards via AnkiConnect."""

import httpx
from mcp.server.fastmcp import FastMCP

ANKI_CONNECT_URL = "http://localhost:8765"

mcp = FastMCP("anki")


async def anki_request(action: str, **params) -> dict | list | None:
    """Send a request to AnkiConnect and return the result."""
    payload = {"action": action, "version": 6}
    if params:
        payload["params"] = params

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                ANKI_CONNECT_URL,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
    except httpx.ConnectError:
        raise RuntimeError(
            "Cannot connect to AnkiConnect. Is Anki running with the AnkiConnect add-on installed?"
        )
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"AnkiConnect HTTP error: {exc.response.status_code}")

    body = resp.json()
    if body.get("error"):
        raise RuntimeError(f"AnkiConnect error: {body['error']}")
    return body.get("result")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_decks() -> list[str]:
    """List all deck names in Anki."""
    return await anki_request("deckNames")


@mcp.tool()
async def list_models() -> list[str]:
    """List all note type (model) names in Anki."""
    return await anki_request("modelNames")


@mcp.tool()
async def get_model_fields(model_name: str) -> list[str]:
    """Get the field names for a given note type (model).

    Args:
        model_name: The name of the note type / model.
    """
    return await anki_request("modelFieldNames", modelName=model_name)


@mcp.tool()
async def create_deck(deck_name: str) -> int:
    """Create a new deck. Use '::' for nested decks (e.g. 'Parent::Child').

    Args:
        deck_name: Name of the deck to create.
    """
    return await anki_request("createDeck", deck=deck_name)


@mcp.tool()
async def add_note(
    deck_name: str,
    model_name: str,
    fields: dict[str, str],
    tags: list[str] | None = None,
    allow_duplicate: bool = False,
) -> int:
    """Add a new note (flashcard) to Anki.

    Args:
        deck_name: Target deck name.
        model_name: Note type / model name (e.g. 'Basic', 'Cloze').
        fields: Dict mapping field names to values. Supports HTML.
        tags: Optional list of tags.
        allow_duplicate: Allow duplicate notes in the same deck. Defaults to False.
    """
    note = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": fields,
        "options": {
            "allowDuplicate": allow_duplicate,
            "duplicateScope": "deck",
        },
        "tags": tags or [],
    }
    return await anki_request("addNote", note=note)


@mcp.tool()
async def search_notes(query: str) -> list[dict]:
    """Search for notes using Anki's search syntax and return their details.

    Common query examples:
      - 'deck:MyDeck' — all notes in a deck
      - 'tag:mytag' — notes with a specific tag
      - '"some text"' — notes containing specific text
      - 'added:7' — notes added in the last 7 days

    Args:
        query: Anki search query string.
    """
    note_ids = await anki_request("findNotes", query=query)
    if not note_ids:
        return []
    notes_info = await anki_request("notesInfo", notes=note_ids)
    results = []
    for note in notes_info:
        results.append(
            {
                "noteId": note["noteId"],
                "modelName": note["modelName"],
                "tags": note["tags"],
                "fields": {
                    name: field["value"]
                    for name, field in note["fields"].items()
                },
            }
        )
    return results


@mcp.tool()
async def update_note(
    note_id: int,
    fields: dict[str, str] | None = None,
    tags: list[str] | None = None,
) -> None:
    """Update an existing note's fields and/or tags.

    Args:
        note_id: The ID of the note to update.
        fields: Optional dict of field names to new values.
        tags: Optional list of tags (replaces all existing tags).
    """
    note: dict = {"id": note_id}
    if fields is not None:
        note["fields"] = fields
    if tags is not None:
        note["tags"] = tags
    await anki_request("updateNote", note=note)


@mcp.tool()
async def update_note_tags(note_id: int, tags: list[str]) -> None:
    """Replace all tags on a note.

    Args:
        note_id: The ID of the note to update.
        tags: The new list of tags (replaces all existing tags).
    """
    # Get current tags, remove them, then add new ones
    notes_info = await anki_request("notesInfo", notes=[note_id])
    if not notes_info:
        raise RuntimeError(f"Note {note_id} not found")
    old_tags = notes_info[0].get("tags", [])
    if old_tags:
        await anki_request(
            "removeTags", notes=[note_id], tags=" ".join(old_tags)
        )
    if tags:
        await anki_request("addTags", notes=[note_id], tags=" ".join(tags))


@mcp.tool()
async def delete_notes(note_ids: list[int]) -> None:
    """Delete one or more notes from Anki.

    Args:
        note_ids: List of note IDs to delete.
    """
    await anki_request("deleteNotes", notes=note_ids)


@mcp.tool()
async def sync() -> None:
    """Trigger a sync with AnkiWeb."""
    await anki_request("sync")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
