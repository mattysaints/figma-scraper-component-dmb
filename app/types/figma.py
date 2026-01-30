from typing import TypedDict, NotRequired, Literal

class FigmaColor(TypedDict):
    r: float
    g: float
    b: float

class FigmaFill(TypedDict):
    type: Literal["SOLID"]
    color: FigmaColor

class FigmaTextStyle(TypedDict):
    fontFamily: str
    fontSize: float
    fontWeight: int
    lineHeightPx: float
    letterSpacing: float

class FigmaNode(TypedDict):
    type: str
    fills: NotRequired[list[FigmaFill]]
    style: NotRequired[FigmaTextStyle]
    children: NotRequired[list["FigmaNode"]]

class FigmaFile(TypedDict):
    document: NotRequired[FigmaNode]
