# tinci-mcp (填詞)

An MCP (Model Context Protocol) server for Cantonese lyric writing (粵語填詞), providing pronunciation lookup, tonal pattern analysis, and rhyme lookup.

## Features

-   **Jyutping Romanization**: Convert Cantonese text to Jyutping pronunciation using [ToJyutping](https://github.com/CanCLID/ToJyutping)
-   **Tonal Pattern Analysis**: Analyze lyrics using the 1056/0243 classification systems for matching syllables to melody
-   **Rhyme Lookup**: Find rhyming characters based on Jyutping finals (韻母), with tone filtering options. Data sourced from [Mr. Pinyin's Rhyme Table](https://lyrics.mrpinyin.net/rhyme.htm)

## Installation

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
# Clone or navigate to the project directory
cd tinci-mcp

# Install dependencies
uv sync
```

## Usage

### Running the Server

```bash
uv run tinci-mcp
```

### Configuring with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
    "mcpServers": {
        "tinci-mcp": {
            "command": "uv",
            "args": ["--directory", "/path/to/tinci-mcp", "run", "tinci-mcp"]
        }
    }
}
```

### Configuring with Cursor

Add to your Cursor MCP settings:

```json
{
    "mcpServers": {
        "tinci-mcp": {
            "command": "uv",
            "args": ["--directory", "/path/to/tinci-mcp", "run", "tinci-mcp"]
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
    "system": "0243",
    "pattern": "43",
    "breakdown": [
        { "character": "你", "jyutping": "nei5", "tone": 5, "mapped": "4" },
        { "character": "好", "jyutping": "hou2", "tone": 2, "mapped": "3" }
    ]
}
```

### `get_rhyming_characters`

Find characters that rhyme with the input character (same Jyutping final/韻母).

**Input:**

-   `character`: A single Chinese character to find rhymes for
-   `tone_filter`: How to filter by tone (default: `"all"`)
    -   `"all"`: Return all rhyming characters regardless of tone
    -   `"same"`: Only return characters with the exact same tone
    -   `"group"`: Return characters in the same tone group (1056/0243)
-   `system`: Tonal classification system (`"1056"` or `"0243"`, default: `"0243"`)
-   `limit`: Maximum number of results (default: `50`)
-   `target_tone`: Find rhymes with a specific tone (1-9), overrides `tone_filter`
-   `target_group`: Find rhymes in a specific tone group, overrides `tone_filter`

**Example 1: Basic rhyme lookup**

```json
// Input: character="來"
{
    "input": {
        "character": "來",
        "jyutping": "loi4",
        "tone": 4,
        "tone_group": "0"
    },
    "final": "oi",
    "rhymes": [
        { "character": "愛", "jyutping": "oi3", "tone": 3, "tone_group": "4" },
        {
            "character": "外",
            "jyutping": "ngoi6",
            "tone": 6,
            "tone_group": "2"
        },
        { "character": "改", "jyutping": "goi2", "tone": 2, "tone_group": "3" }
    ],
    "total_count": 190
}
```

**Example 2: Find rhymes with a different tone**

```json
// Input: character="泉", target_tone=1
// 泉 is cyun4 (tone 4), but we want rhymes with tone 1
{
    "input": {
        "character": "泉",
        "jyutping": "cyun4",
        "tone": 4,
        "tone_group": "0"
    },
    "final": "yun",
    "target_tone": 1,
    "rhymes": [
        {
            "character": "村",
            "jyutping": "cyun1",
            "tone": 1,
            "tone_group": "3"
        },
        {
            "character": "川",
            "jyutping": "cyun1",
            "tone": 1,
            "tone_group": "3"
        },
        { "character": "穿", "jyutping": "cyun1", "tone": 1, "tone_group": "3" }
    ],
    "total_count": 74
}
```

**Example 3: Find rhymes in a different tone group**

```json
// Input: character="泉", target_group="3"
// 泉 is in group 0, but we want rhymes in group 3 (tones 1, 2, 7)
{
    "input": {
        "character": "泉",
        "jyutping": "cyun4",
        "tone": 4,
        "tone_group": "0"
    },
    "final": "yun",
    "target_group": "3",
    "rhymes": [
        {
            "character": "忖",
            "jyutping": "cyun2",
            "tone": 2,
            "tone_group": "3"
        },
        {
            "character": "村",
            "jyutping": "cyun1",
            "tone": 1,
            "tone_group": "3"
        },
        { "character": "川", "jyutping": "cyun1", "tone": 1, "tone_group": "3" }
    ],
    "total_count": 119
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

## Data Sources

-   **Jyutping Data**: [ToJyutping](https://github.com/CanCLID/ToJyutping) - Cantonese romanization library
-   **Rhyme Data**: [Mr. Pinyin's Rhyme Table (押韻 Rhyme)](https://lyrics.mrpinyin.net/rhyme.htm) - Curated rhyming characters organized by Jyutping finals (韻母), specifically designed for Cantonese lyric writing

## License

MIT
