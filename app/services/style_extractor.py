from app.schemas.styles import Color, TextStyle, ExtractedStyles
from app.services.figma_extractor import extract_styles_from_node
from app.types.figma import FigmaNode


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
