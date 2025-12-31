"""MCP Server for Cantonese pronunciation and tonal pattern analysis.

Provides tools for LLMs to:
1. Get Jyutping romanization for Cantonese text
2. Analyze tonal patterns for lyrics using 1056/0243 systems
3. Find rhyming characters for lyrics composition
"""

from typing import Literal

import ToJyutping
from mcp.server.fastmcp import FastMCP

from tinci_mcp.rhyme_lookup import find_rhyming_characters as _find_rhymes
from tinci_mcp.tone_mapper import ToneSystem, analyze_tones

# Initialize the MCP server
mcp = FastMCP("tinci-mcp")


@mcp.tool()
def get_jyutping(text: str) -> dict:
    """Convert Cantonese text to Jyutping romanization.
    
    Returns the Jyutping pronunciation for each character in the input text.
    Jyutping is the standard romanization system for Cantonese, where each
    syllable ends with a tone number from 1-6 (with 7-9 for entering tones).
    
    Args:
        text: Cantonese text to convert (Traditional or Simplified Chinese)
        
    Returns:
        Dictionary with the original text and a list of character-pronunciation pairs
    
    Example:
        Input: "你好"
        Output: {"text": "你好", "jyutping": [["你", "nei5"], ["好", "hou2"]]}
    """
    # ToJyutping.get_jyutping_list returns list of (char, jyutping) tuples
    result = ToJyutping.get_jyutping_list(text)
    
    # Convert to list of lists for JSON serialization
    pairs = [[char, jyutping if jyutping else ""] for char, jyutping in result]
    
    # Also provide a combined romanization string
    romanization_parts = []
    for char, jyutping in result:
        if jyutping:
            romanization_parts.append(jyutping)
    
    return {
        "text": text,
        "jyutping": pairs,
        "romanization": " ".join(romanization_parts),
    }


@mcp.tool()
def get_tone_pattern(
    text: str, 
    system: Literal["1056", "0243"] = "0243"
) -> dict:
    """Analyze the tonal pattern of Cantonese text for lyrics writing.
    
    Converts each character's tone to the 1056 or 0243 system used in
    Cantonese lyric writing to match syllables with melody notes.
    
    The 1056 system groups Cantonese tones as:
    - 1: High tones (tones 1, 2, 7) - highest pitch
    - 0: Low falling (tone 4) - falling pitch  
    - 5: Mid tones (tones 3, 5, 8) - middle pitch
    - 6: Low tones (tones 6, 9) - lowest pitch
    
    The 0243 system uses different digits but same groupings:
    - 3: High tones (tones 1, 2, 7)
    - 0: Low falling (tone 4)
    - 4: Mid tones (tones 3, 5, 8)
    - 2: Low tones (tones 6, 9)
    
    Args:
        text: Cantonese text to analyze
        system: Tonal classification system, either "1056" or "0243"
        
    Returns:
        Dictionary with:
        - text: Original input text
        - system: The system used (1056 or 0243)
        - pattern: Condensed tone pattern string (e.g., "1560")
        - breakdown: Detailed per-character analysis
        
    Example:
        Input: "今天天氣", system="1056"
        Output includes pattern like "1516" showing the tonal contour
    """
    # Get jyutping for each character
    jyutping_list = ToJyutping.get_jyutping_list(text)
    
    # Analyze tones
    analysis = analyze_tones(jyutping_list, system)
    
    return {
        "text": text,
        **analysis,
    }


@mcp.tool()
def get_rhyming_characters(
    character: str,
    tone_filter: Literal["all", "same", "group"] = "all",
    system: Literal["1056", "0243"] = "0243",
    limit: int = 50,
    target_tone: int | None = None,
    target_group: str | None = None,
) -> dict:
    """Find characters that rhyme with the input character for lyrics composition.
    
    Returns characters sharing the same Jyutping final (韻母) as the input character.
    This is essential for writing Cantonese lyrics where rhyming is based on 
    the final sound of syllables.
    
    Args:
        character: A single Chinese character to find rhymes for
        tone_filter: How to filter results by tone:
            - "all": Return all rhyming characters regardless of tone
            - "same": Only return characters with the exact same tone number
            - "group": Return characters in the same tone group (e.g., in the 0243 system, tones 1, 2 and 7 are in the same group (3); tones 3, 5 and 8 are in the same group (4); tones 6 and 9 are in the same group (2))
        system: Tonal classification system for "group" filtering and tone display (1056 or 0243)
        limit: Maximum number of rhyming characters to return (default 50)
        target_tone: If specified, find rhyming characters with this specific tone (1-9).
            Overrides tone_filter. Example: character="泉" (tone 4), target_tone=1 returns
            rhyming characters with tone 1.
        target_group: If specified, find rhyming characters in this tone group.
            Overrides tone_filter. For 0243 system: "0" (tone 4), "2" (tones 6,9), 
            "3" (tones 1,2,7), "4" (tones 3,5,8). Example: character="泉" (group 0),
            target_group="3" returns rhyming characters with tones 1, 2, or 7.
        
    Returns:
        Dictionary with:
        - input: Info about the input character (character, jyutping, tone, tone_group)
        - final: The jyutping final (韻母) used for matching
        - rhymes: List of rhyming characters with their jyutping and tone info
        - count: Number of rhyming characters returned
        - total_count: Total available (before limit)
        - target_tone: (if specified) The target tone used for filtering
        - target_group: (if specified) The target group used for filtering
        
    Example:
        Input: character="來", tone_filter="all"
        Returns rhyming characters like 愛 (oi3), 外 (ngoi6), 改 (goi2), etc.
        that share the same "oi" final.
        
        Input: character="泉", target_tone=1
        Returns rhyming characters with final "yun" but with tone 1.
        
        Input: character="泉", target_group="3"
        Returns rhyming characters with final "yun" but with tones 1, 2, or 7 (group 3).
    """
    return _find_rhymes(
        character=character,
        tone_filter=tone_filter,
        system=system,
        limit=limit,
        target_tone=target_tone,
        target_group=target_group,
    )


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

