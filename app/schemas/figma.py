from pydantic import BaseModel, HttpUrl


class FigmaAnalyzeRequest(BaseModel):
    figma_url: HttpUrl
    use_node_id: bool = False


class FigmaAnalyzeResponse(BaseModel):
    file_key: str
    node_id: str | None
    status: str
