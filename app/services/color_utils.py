def rgb_float_to_hex(r: float, g: float, b: float) -> str:
    """
    Convert Figma RGB (0-1 floats) to HEX string.
    """
    return "#{:02X}{:02X}{:02X}".format(
        int(r * 255),
        int(g * 255),
        int(b * 255),
    )
