from app.schemas.styles import Color, ExtractedStyles, TextStyle
from app.services.color_utils import rgb_float_to_hex
from app.types.figma import FigmaNode


def extract_styles_from_node(
    node: FigmaNode,
    colors: set[str],
    text_styles: set[tuple[str | None, float | None, int | None, float | None, float | None]],
) -> None:
    """
    Recursively traverse a Figma node tree and collect styles.
    """

    # Colors
    fills = node.get("fills")
    if fills:
        for fill in fills:
            if fill["type"] == "SOLID":
                color = fill["color"]
                hex_color = rgb_float_to_hex(
                    color["r"],
                    color["g"],
                    color["b"],
                )
                colors.add(hex_color)

    # Text styles
    if node.get("type") == "TEXT":
        style = node.get("style")
        if style:
            text_styles.add(
                (
                    style["fontFamily"],
                    style["fontSize"],
                    style["fontWeight"],
                    style["lineHeightPx"],
                    style["letterSpacing"],
                )
            )

    # Recursion
    children = node.get("children")
    if children:
        for child in children:
            extract_styles_from_node(child, colors, text_styles)


def extract_styles(document: FigmaNode) -> ExtractedStyles:
    colors: set[str] = set()
    text_styles: set[tuple[str | None, float | None, int | None, float | None, float | None]] = set()

    extract_styles_from_node(document, colors, text_styles)

    return ExtractedStyles(
        colors=[Color(hex=c) for c in sorted(colors)],
        text_styles=[
            TextStyle(
                font_family=font_family,
                font_size=font_size,
                font_weight=font_weight,
                line_height_px=line_height_px,
                letter_spacing=letter_spacing,
            )
            for (
                font_family,
                font_size,
                font_weight,
                line_height_px,
                letter_spacing,
            ) in sorted(text_styles)
            if font_family is not None and font_size is not None
        ],
    )
