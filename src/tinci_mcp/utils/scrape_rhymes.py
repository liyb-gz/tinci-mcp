#!/usr/bin/env python3
"""Scrape rhyme data from mrpinyin.net for Cantonese lyrics.

This script extracts character data organized by finals (韻母) from
https://lyrics.mrpinyin.net/rhyme.htm and saves it as a JSON file.
"""

import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://lyrics.mrpinyin.net/rhyme.htm"

# Map initial labels from the page to standard jyutping initials
INITIAL_MAP = {
    "0": "",      # No initial (零聲母)
    ".": "",      # No initial variant
    "B": "b",
    "C": "c",
    "D": "d",
    "F": "f",
    "G": "g",
    "GW": "gw",
    "H": "h",
    "J": "j",
    "K": "k",
    "KW": "kw",
    "L": "l",
    "M": "m",
    "N": "n",
    "NG": "ng",
    "P": "p",
    "S": "s",
    "T": "t",
    "W": "w",
    "Z": "z",
}

# Tone column structure: each column header indicates which tones are in that column
# The page uses headers: 0 | 2 | 5 - 4 | 9 - 3
# Based on actual data analysis:
# - Column 1 (header "0"): tone 4 (low falling, 0243 code 0)
# - Column 2 (header "2"): tone 6 (low level, 0243 code 2)
# - Column 3 (header "5 - 4"): tone 5 before "-", tone 3 after "-" (0243 code 4 = mid tones)
# - Column 4 (header "9 - 3"): tone 2 before "-", tone 1 after "-" (mixed 0243 codes 2+3)

TONE_COLUMNS = [
    [4],           # Column 1: tone 4
    [6],           # Column 2: tone 6
    [5, 3],        # Column 3: tone 5, then tone 3 (separated by -)
    [2, 1],        # Column 4: tone 2, then tone 1 (separated by -)
]


def fetch_page() -> str:
    """Fetch the HTML content from the rhyme page."""
    response = requests.get(URL, timeout=30)
    response.encoding = 'utf-8'
    return response.text


def parse_final_section(table: BeautifulSoup, final: str) -> list[dict]:
    """Parse a final section table and extract characters.
    
    Args:
        table: BeautifulSoup table element containing the final's data
        final: The final (韻母) being parsed, e.g., "aa", "oi"
        
    Returns:
        List of character entries with their jyutping
    """
    characters = []
    rows = table.find_all('tr')
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue
            
        # First cell contains the initial (e.g., "B b", "L l", "0 .", etc.)
        first_cell = cells[0].get_text(strip=True)
        
        # Skip header rows that don't have initial info
        if not first_cell or first_cell.isdigit():
            continue
            
        # Extract the initial from first cell (e.g., "B b" -> "B", "GW gw" -> "GW")
        initial_match = re.match(r'^([A-Z]+|[0.])', first_cell.upper())
        if not initial_match:
            continue
            
        initial_label = initial_match.group(1)
        initial = INITIAL_MAP.get(initial_label, "")
        
        # Process each tone column (columns 2-5, index 1-4)
        for col_idx, tones in enumerate(TONE_COLUMNS):
            if col_idx + 1 >= len(cells):
                continue
                
            cell_text = cells[col_idx + 1].get_text(strip=True)
            if not cell_text or cell_text == ".":
                continue
            
            # Split by "-" to separate different tone groups within the cell
            parts = cell_text.split("-")
            
            for part_idx, part in enumerate(parts):
                part = part.strip()
                if not part or part == ".":
                    continue
                    
                # Determine tone for this part
                if part_idx < len(tones):
                    tone = tones[part_idx]
                else:
                    tone = tones[-1]  # Use last tone if more parts than expected
                
                # Each character in the part has the same initial+final+tone
                for char in part:
                    # Skip non-Chinese characters and punctuation
                    if not is_chinese_char(char):
                        continue
                        
                    jyutping = f"{initial}{final}{tone}"
                    characters.append({
                        "char": char,
                        "jyutping": jyutping,
                        "tone": tone,
                    })
    
    return characters


def is_chinese_char(char: str) -> bool:
    """Check if a character is a Chinese character."""
    code = ord(char)
    return (
        0x4E00 <= code <= 0x9FFF or      # CJK Unified Ideographs
        0x3400 <= code <= 0x4DBF or      # CJK Unified Ideographs Extension A
        0x20000 <= code <= 0x2A6DF or    # CJK Unified Ideographs Extension B
        0xF900 <= code <= 0xFAFF or      # CJK Compatibility Ideographs
        0x2F800 <= code <= 0x2FA1F       # CJK Compatibility Ideographs Supplement
    )


def parse_rhyme_page(html: str) -> dict:
    """Parse the entire rhyme page and extract all finals with their characters.
    
    Returns:
        Dictionary mapping finals to their character lists
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    rhyme_data = {}
    
    # Find all tables on the page
    tables = soup.find_all('table')
    
    # The first table is the finals overview table (粵拼韻母表)
    # Subsequent tables contain character data for each final
    
    current_final = None
    
    for table in tables:
        # Try to find the final name from the first row
        first_row = table.find('tr')
        if not first_row:
            continue
            
        first_cell = first_row.find('td')
        if not first_cell:
            continue
            
        cell_text = first_cell.get_text(strip=True)
        
        # Look for pattern like "01 啊aa" or "42 哀oi"
        final_match = re.match(r'^\d+\s+.([a-z]+)$', cell_text)
        if final_match:
            current_final = final_match.group(1)
            characters = parse_final_section(table, current_final)
            
            if characters:
                if current_final not in rhyme_data:
                    rhyme_data[current_final] = {"characters": []}
                    
                # Deduplicate while preserving order
                seen = set()
                for char_entry in characters:
                    key = (char_entry["char"], char_entry["jyutping"])
                    if key not in seen:
                        seen.add(key)
                        rhyme_data[current_final]["characters"].append(char_entry)
    
    return rhyme_data


def main():
    """Main entry point for the scraper."""
    print(f"Fetching rhyme data from {URL}...")
    html = fetch_page()
    
    print("Parsing rhyme data...")
    rhyme_data = parse_rhyme_page(html)
    
    # Get output path
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    output_path = data_dir / "rhymes.json"
    
    # Ensure data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(rhyme_data, f, ensure_ascii=False, indent=2)
    
    # Print summary
    total_chars = sum(len(v["characters"]) for v in rhyme_data.values())
    print(f"\nSaved {len(rhyme_data)} finals with {total_chars} character entries")
    print(f"Output: {output_path}")
    
    # Show sample
    print("\nSample (oi final):")
    if "oi" in rhyme_data:
        for entry in rhyme_data["oi"]["characters"][:10]:
            print(f"  {entry['char']} - {entry['jyutping']}")


if __name__ == "__main__":
    main()

