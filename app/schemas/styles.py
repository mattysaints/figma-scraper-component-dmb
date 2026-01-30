from pydantic import BaseModel
from typing import Optional


class Color(BaseModel):
    hex: str


class TextStyle(BaseModel):
    font_family: str
    font_size: float
    font_weight: Optional[int]
    line_height_px: Optional[float]
    letter_spacing: Optional[float]


class ExtractedStyles(BaseModel):
    colors: list[Color]
    text_styles: list[TextStyle]
