"""Tone mapping logic for Cantonese lyrics analysis.

Implements the 1056 and 0243 tonal classification systems used in Cantonese
lyric writing to match syllable tones with musical notes.

Reference: https://www.hk01.com/社區專題/118873/填詞其實唔難-粵語歌愛好者話你知填詞冷知識
"""

from typing import Literal

# 1056 System mapping
# - 1: High tones (tones 1, 2, 7)
# - 0: Low falling tone (tone 4)
# - 5: Mid tones (tones 3, 5, 8)
# - 6: Low tones (tones 6, 9)
TONE_TO_1056: dict[int, str] = {
    1: "1",
    2: "1",
    7: "1",
    4: "0",
    3: "5",
    5: "5",
    8: "5",
    6: "6",
    9: "6",
}

# 0243 System mapping (alternative representation)
# - 3: High tones (tones 1, 2, 7)
# - 0: Low falling tone (tone 4)
# - 2: Mid tones (tones 3, 5, 8)
# - 4: Low tones (tones 6, 9)
TONE_TO_0243: dict[int, str] = {
    1: "3",
    2: "3",
    7: "3",
    4: "0",
    3: "2",
    5: "2",
    8: "2",
    6: "4",
    9: "4",
}

ToneSystem = Literal["1056", "0243"]


def extract_tone_from_jyutping(jyutping: str) -> int | None:
    """Extract the tone number from a Jyutping syllable.
    
    Args:
        jyutping: A Jyutping syllable like 'jat1' or 'nei5'
        
    Returns:
        The tone number (1-9) or None if not found
    """
    if not jyutping:
        return None
    
    # Tone is the last character and should be a digit 1-9
    last_char = jyutping[-1]
    if last_char.isdigit():
        tone = int(last_char)
        if 1 <= tone <= 9:
            return tone
    return None


def map_tone(tone: int, system: ToneSystem = "1056") -> str:
    """Map a Cantonese tone number to its 1056 or 0243 value.
    
    Args:
        tone: Cantonese tone number (1-9)
        system: Either "1056" or "0243"
        
    Returns:
        The mapped tone value as a string
    """
    mapping = TONE_TO_1056 if system == "1056" else TONE_TO_0243
    return mapping.get(tone, "?")


def analyze_tones(
    jyutping_pairs: list[tuple[str, str]], 
    system: ToneSystem = "1056"
) -> dict:
    """Analyze a list of character-jyutping pairs for tonal patterns.
    
    Args:
        jyutping_pairs: List of (character, jyutping) tuples
        system: Either "1056" or "0243"
        
    Returns:
        Dictionary with pattern string and detailed breakdown
    """
    breakdown = []
    pattern_chars = []
    
    for char, jyutping in jyutping_pairs:
        tone = extract_tone_from_jyutping(jyutping)
        if tone is not None:
            mapped = map_tone(tone, system)
            pattern_chars.append(mapped)
            breakdown.append({
                "character": char,
                "jyutping": jyutping,
                "tone": tone,
                "mapped": mapped,
            })
        else:
            # Non-tonal characters (punctuation, etc.)
            breakdown.append({
                "character": char,
                "jyutping": jyutping,
                "tone": None,
                "mapped": None,
            })
    
    return {
        "system": system,
        "pattern": "".join(pattern_chars),
        "breakdown": breakdown,
    }

