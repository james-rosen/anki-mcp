# anki-mcp

An MCP server that lets AI assistants create, search, edit, and delete Anki flashcards via [AnkiConnect](https://foosoft.net/projects/anki-connect/).

## Prerequisites

- [Anki](https://apps.ankiweb.net/) desktop app
- [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on installed in Anki (Tools > Add-ons > Get Add-ons > code `2055492159`)
- [uv](https://docs.astral.sh/uv/) package manager
- Anki must be running when you use the tools

## Setup

### Claude Desktop

Add this to your `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "anki": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/anki-mcp",
        "run", "anki_mcp.py"
      ]
    }
  }
}
```

Replace `/path/to/anki-mcp` with the actual path where you cloned this repo.

Restart Claude Desktop. You should see "anki" in the connectors menu.

### Other MCP clients

Any MCP client that supports stdio transport can use this server. The command is:

```sh
uv --directory /path/to/anki-mcp run anki_mcp.py
```

## Tools

| Tool | Description |
|---|---|
| `list_decks` | List all deck names |
| `list_models` | List all note type (model) names |
| `get_model_fields` | Get field names for a note type |
| `create_deck` | Create a new deck (supports `::` for nesting) |
| `add_note` | Add a new note with deck, model, fields, and optional tags |
| `search_notes` | Search notes using [Anki's search syntax](https://docs.ankiweb.net/searching.html) and return their details |
| `update_note` | Update a note's fields and/or tags |
| `update_note_tags` | Replace all tags on a note |
| `delete_notes` | Delete notes by ID |
| `sync` | Trigger AnkiWeb sync |

## Example usage

> "Create 5 flashcards about photosynthesis in my Biology deck"

> "Search for all cards tagged 'spanish' and fix any formatting issues"

> "What decks do I have?"

## How it works

This server communicates over stdio with your MCP client and makes HTTP requests to AnkiConnect on `localhost:8765`. There is no network access beyond your local machine.

```
MCP Client (Claude Desktop, etc.)
    |  stdio
anki_mcp.py
    |  HTTP localhost:8765
Anki + AnkiConnect
```

## Development

```sh
# Install dependencies
uv sync

# Run directly
uv run anki_mcp.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv run anki_mcp.py
```

## License

MIT
