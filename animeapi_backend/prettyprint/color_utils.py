def translate_hex_to_rgb(hex_: int) -> tuple[int, int, int]:
    """Translate hex to rgb"""
    return ((hex_ >> 16) & 0xFF, (hex_ >> 8) & 0xFF, hex_ & 0xFF)
