# anki-mcp

Talk to your Anki flashcards from Claude. Create cards, search your collection, edit and delete notes, and trigger syncs — all through natural conversation in Claude Desktop.

This is an [MCP server](https://modelcontextprotocol.io/) that connects Claude Desktop to your local Anki app via [AnkiConnect](https://foosoft.net/projects/anki-connect/). Everything runs locally on your machine.

## What you can do with it

Just talk to Claude naturally. No special syntax, no commands — just describe what you want:

- **"Create 10 flashcards about the French Revolution for my History deck"** — Claude checks your available decks and note types, then creates the cards with proper formatting and tags
- **"Find all my cards tagged 'spanish' that mention irregular verbs"** — searches your collection and shows you the full card contents
- **"That third card is wrong, the answer should be 'fue' not 'era'"** — Claude looks up the card and updates it in place
- **"Split that card into three separate cards, one per verb tense"** — deletes the original and creates new atomic cards
- **"Sync my collection"** — triggers an AnkiWeb sync so your changes appear on your phone

Claude has access to your full collection — it can see your decks, note types, fields, and tags, so it can make smart decisions about where to put cards and how to format them.

## Setup

Three things: Anki with AnkiConnect, this repo, and a one-time config change in Claude Desktop.

### Step 1: Install AnkiConnect in Anki

1. Open [Anki](https://apps.ankiweb.net/)
2. Go to **Tools > Add-ons > Get Add-ons...**
3. Paste this code: `2055492159`
4. Click **OK** and **restart Anki**

This installs [AnkiConnect](https://ankiweb.net/shared/info/2055492159), a lightweight add-on that lets other programs on your computer talk to Anki. You can verify it's working by visiting http://localhost:8765 in your browser — you should see `AnkiConnect v.6`.

### Step 2: Clone this repo

You'll need [uv](https://docs.astral.sh/uv/) (a fast Python package manager). If you don't have it:

```sh
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# or with Homebrew
brew install uv
```

Then clone this repo wherever you like:

```sh
git clone https://github.com/james-rosen/anki-mcp.git
```

No need to install anything else — `uv` handles dependencies automatically on first run.

### Step 3: Tell Claude Desktop about the server

Open your Claude Desktop config file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the `anki` entry to the `mcpServers` section. If the file already has other servers configured, just add the `"anki": { ... }` block alongside them:

```json
{
  "mcpServers": {
    "anki": {
      "command": "uv",
      "args": [
        "--directory", "/absolute/path/to/anki-mcp",
        "run", "anki_mcp.py"
      ]
    }
  }
}
```

**Important**: Replace `/absolute/path/to/anki-mcp` with the full path to where you cloned the repo. For example:
- macOS: `/Users/yourname/projects/anki-mcp`
- Windows: `C:\\Users\\yourname\\projects\\anki-mcp`

> **Tip**: If Claude Desktop can't find `uv`, use the full path instead of just `"command": "uv"`. Run `which uv` in your terminal to find it (e.g. `/Users/yourname/.local/bin/uv`).

### Step 4: Restart and verify

1. **Make sure Anki is open** — the tools only work while Anki is running
2. **Fully quit Claude Desktop** (Cmd+Q on macOS, not just close the window) and reopen it
3. Start a **new conversation**
4. Click the **Connectors** menu near the input area and confirm **anki** is toggled on
5. Ask Claude **"What decks do I have in Anki?"** — if it lists your decks, you're all set

## Tools

Claude sees these tools and decides when to use them based on your requests. You don't need to call them by name — just describe what you want in plain English.

| Tool | What it does |
|---|---|
| `list_decks` | Lists all your deck names |
| `list_models` | Lists your note types (Basic, Cloze, etc.) |
| `get_model_fields` | Shows the fields for a note type (e.g. Front/Back for Basic) |
| `create_deck` | Creates a new deck — use `::` for sub-decks (e.g. `Languages::Spanish`) |
| `add_note` | Creates a flashcard with the deck, note type, fields, and tags you specify |
| `search_notes` | Searches your collection using [Anki's search syntax](https://docs.ankiweb.net/searching.html) and returns full card details |
| `update_note` | Edits a card's content or tags |
| `update_note_tags` | Replaces all tags on a card |
| `delete_notes` | Deletes one or more cards by ID |
| `sync` | Triggers a sync with AnkiWeb |

## Search syntax

When you ask Claude to find cards, it uses Anki's built-in search syntax under the hood. You can speak naturally ("find my Spanish cards from this week") and Claude will translate, or use the syntax directly if you prefer:

| Query | What it finds |
|---|---|
| `deck:Spanish` | All notes in the Spanish deck |
| `deck:Languages::Spanish` | Notes in a sub-deck |
| `tag:verb` | Notes tagged "verb" |
| `"irregular verb"` | Notes containing the exact phrase |
| `front:bonjour` | Notes where the Front field contains "bonjour" |
| `added:7` | Notes added in the last 7 days |
| `rated:1` | Notes reviewed today |
| `is:due` | Notes that are currently due |
| `tag:verb deck:Spanish` | Combine multiple filters |

Full reference: [Anki search documentation](https://docs.ankiweb.net/searching.html)

## How it works

```
You
 ↕  chat
Claude Desktop
 ↕  stdio (JSON messages)
anki_mcp.py (this server)
 ↕  HTTP to localhost:8765
Anki desktop app (via AnkiConnect add-on)
```

Everything runs on your machine. The only network call is between this script and Anki on localhost. No data leaves your computer (unless you trigger a sync to AnkiWeb).

## License

MIT
