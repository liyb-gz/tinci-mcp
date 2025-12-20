"""MCP Server for Cantonese pronunciation and tonal pattern analysis.

Provides tools for LLMs to:
1. Get Jyutping romanization for Cantonese text
2. Analyze tonal patterns for lyrics using 1056/0243 systems
"""

from typing import Literal

import ToJyutping
from mcp.server.fastmcp import FastMCP

from canmcp.tone_mapper import ToneSystem, analyze_tones

# Initialize the MCP server
mcp = FastMCP("Cantonese Pronunciation Server")


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
    - 2: Mid tones (tones 3, 5, 8)
    - 4: Low tones (tones 6, 9)
    
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


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

