"""Rhyme lookup functionality for Cantonese lyrics.

Provides functions to find rhyming characters based on jyutping finals (韻母),
with optional tone filtering for more precise rhyme matching.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from tinci_mcp.tone_mapper import TONE_TO_0243, TONE_TO_1056, ToneSystem

# Build reverse mapping: character -> list of (final, jyutping, tone)
CharacterInfo = dict[str, list[tuple[str, str, int]]]

# Type for the rhyme data structure
RhymeData = dict[str, dict[str, list[dict]]]


@lru_cache(maxsize=1)
def load_rhyme_data() -> RhymeData:
    """Load the rhyme data from the JSON file.
    
    Returns:
        Dictionary mapping finals to their character lists
    """
    data_path = Path(__file__).parent / "data" / "rhymes.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@lru_cache(maxsize=1)
def build_character_index() -> CharacterInfo:
    """Build a reverse index from characters to their finals.
    
    Returns:
        Dictionary mapping each character to a list of (final, jyutping, tone) tuples
    """
    rhyme_data = load_rhyme_data()
    char_index: CharacterInfo = {}
    
    for final, data in rhyme_data.items():
        for entry in data.get("characters", []):
            char = entry["char"]
            jyutping = entry["jyutping"]
            tone = entry["tone"]
            
            if char not in char_index:
                char_index[char] = []
            char_index[char].append((final, jyutping, tone))
    
    return char_index


def get_character_info(char: str) -> list[tuple[str, str, int]] | None:
    """Look up a character's pronunciation info.
    
    Args:
        char: A single Chinese character
        
    Returns:
        List of (final, jyutping, tone) tuples, or None if not found
    """
    char_index = build_character_index()
    return char_index.get(char)


def get_tone_group(tone: int, system: ToneSystem = "0243") -> str:
    """Get the tone group (1056 or 0243) for a tone number.
    
    Args:
        tone: Cantonese tone number (1-9)
        system: Tonal classification system
        
    Returns:
        The tone group digit as a string
    """
    mapping = TONE_TO_1056 if system == "1056" else TONE_TO_0243
    return mapping.get(tone, "?")


def find_rhyming_characters(
    character: str,
    tone_filter: Literal["all", "same", "group"] = "all",
    system: ToneSystem = "0243",
    limit: int = 50,
    target_tone: int | None = None,
    target_group: str | None = None,
) -> dict:
    """Find characters that rhyme with the input character.
    
    Characters rhyme if they share the same jyutping final (韻母).
    
    Args:
        character: The character to find rhymes for
        tone_filter: How to filter by tone:
            - "all": Return all characters with the same final
            - "same": Return only characters with the exact same tone
            - "group": Return characters in the same tone group (1056/0243)
        system: Tonal classification system for "group" filtering
        limit: Maximum number of rhyming characters to return
        target_tone: If specified, filter to this specific tone number (1-9).
            Overrides tone_filter when set.
        target_group: If specified, filter to this tone group (e.g., "0", "2", "3", "4" 
            for 0243 system). Overrides tone_filter when set.
        
    Returns:
        Dictionary with:
        - input: Input character info
        - final: The jyutping final used for matching
        - rhymes: List of rhyming characters with their jyutping and tone info
        - total_count: Total number of rhyming characters (before limit)
    """
    # Look up the input character
    char_info = get_character_info(character)
    if not char_info:
        return {
            "error": f"Character '{character}' not found in rhyme database",
            "input": {"character": character},
            "rhymes": [],
        }
    
    # Use the first pronunciation by default
    final, jyutping, tone = char_info[0]
    input_tone_group = get_tone_group(tone, system)
    
    # Get all characters with the same final
    rhyme_data = load_rhyme_data()
    final_data = rhyme_data.get(final, {})
    all_rhymes = final_data.get("characters", [])
    
    # Determine filtering mode
    # target_tone and target_group override tone_filter
    use_target_tone = target_tone is not None
    use_target_group = target_group is not None
    
    # Filter by tone if requested
    filtered_rhymes = []
    for entry in all_rhymes:
        # Skip the input character itself
        if entry["char"] == character:
            continue
            
        entry_tone = entry["tone"]
        entry_tone_group = get_tone_group(entry_tone, system)
        
        # Apply filtering based on priority: target_tone > target_group > tone_filter
        if use_target_tone:
            # Filter to specific target tone
            if entry_tone != target_tone:
                continue
        elif use_target_group:
            # Filter to specific target group
            if entry_tone_group != target_group:
                continue
        elif tone_filter == "same":
            if entry_tone != tone:
                continue
        elif tone_filter == "group":
            if entry_tone_group != input_tone_group:
                continue
        # "all" includes everything
        
        filtered_rhymes.append({
            "character": entry["char"],
            "jyutping": entry["jyutping"],
            "tone": entry_tone,
            "tone_group": entry_tone_group,
        })
    
    total_count = len(filtered_rhymes)
    
    # Apply limit
    limited_rhymes = filtered_rhymes[:limit]
    
    # Build result with filter info
    result = {
        "input": {
            "character": character,
            "jyutping": jyutping,
            "tone": tone,
            "tone_group": input_tone_group,
        },
        "final": final,
        "system": system,
        "tone_filter": tone_filter,
        "rhymes": limited_rhymes,
        "count": len(limited_rhymes),
        "total_count": total_count,
    }
    
    # Add target info if specified
    if use_target_tone:
        result["target_tone"] = target_tone
    if use_target_group:
        result["target_group"] = target_group
    
    return result


def get_available_finals() -> list[str]:
    """Get a list of all available finals in the rhyme database.
    
    Returns:
        Sorted list of finals (韻母)
    """
    rhyme_data = load_rhyme_data()
    return sorted(rhyme_data.keys())


def get_characters_by_final(
    final: str,
    tone_filter: int | None = None,
    limit: int = 100,
) -> dict:
    """Get all characters with a specific final.
    
    Args:
        final: The jyutping final (韻母) to look up
        tone_filter: Optional tone number to filter by
        limit: Maximum number of characters to return
        
    Returns:
        Dictionary with final info and character list
    """
    rhyme_data = load_rhyme_data()
    
    if final not in rhyme_data:
        return {
            "error": f"Final '{final}' not found in rhyme database",
            "available_finals": get_available_finals(),
        }
    
    all_chars = rhyme_data[final].get("characters", [])
    
    if tone_filter is not None:
        filtered = [c for c in all_chars if c["tone"] == tone_filter]
    else:
        filtered = all_chars
    
    return {
        "final": final,
        "tone_filter": tone_filter,
        "characters": filtered[:limit],
        "count": len(filtered[:limit]),
        "total_count": len(filtered),
    }

