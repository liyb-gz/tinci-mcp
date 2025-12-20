# Cantonese MCP Server (canmcp)

An MCP (Model Context Protocol) server that provides Cantonese pronunciation lookup and tonal pattern analysis for lyric writing.

## Features

-   **Jyutping Romanization**: Convert Cantonese text to Jyutping pronunciation using [ToJyutping](https://github.com/CanCLID/ToJyutping)
-   **Tonal Pattern Analysis**: Analyze lyrics using the 1056/0243 classification systems for matching syllables to melody

## Installation

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
# Clone or navigate to the project directory
cd canmcp

# Install dependencies
uv sync
```

## Usage

### Running the Server

```bash
uv run canmcp
```

### Configuring with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
    "mcpServers": {
        "canmcp": {
            "command": "uv",
            "args": ["--directory", "/path/to/canmcp", "run", "canmcp"]
        }
    }
}
```

### Configuring with Cursor

Add to your Cursor MCP settings:

```json
{
    "mcpServers": {
        "canmcp": {
            "command": "uv",
            "args": ["--directory", "/path/to/canmcp", "run", "canmcp"]
        }
    }
}
```

## Tools

### `get_jyutping`

Convert Cantonese text to Jyutping romanization.

**Input:**

-   `text`: Cantonese text (Traditional or Simplified Chinese)

**Output:**

```json
{
    "text": "你好",
    "jyutping": [
        ["你", "nei5"],
        ["好", "hou2"]
    ],
    "romanization": "nei5 hou2"
}
```

### `get_tone_pattern`

Analyze tonal patterns for lyric writing using the 1056 or 0243 system.

**Input:**

-   `text`: Cantonese text to analyze
-   `system`: Either `"1056"` or `"0243"` (default: `"0243"`)

**Output:**

```json
{
    "text": "你好",
    "system": "1056",
    "pattern": "51",
    "breakdown": [
        { "character": "你", "jyutping": "nei5", "tone": 5, "mapped": "5" },
        { "character": "好", "jyutping": "hou2", "tone": 2, "mapped": "1" }
    ]
}
```

## Tonal Systems

The 1056 and 0243 systems group Cantonese's 9 tones into 4 categories for matching with musical notes:

| Tone Numbers | 1056 Value | 0243 Value | Description |
| ------------ | ---------- | ---------- | ----------- |
| 1, 2, 7      | 1          | 3          | High tones  |
| 4            | 0          | 0          | Low falling |
| 3, 5, 8      | 5          | 4          | Mid tones   |
| 6, 9         | 6          | 2          | Low tones   |

Reference: [HK01 Article on Cantonese Lyric Writing](https://www.hk01.com/社區專題/118873/填詞其實唔難-粵語歌愛好者話你知填詞冷知識)

## License

MIT
