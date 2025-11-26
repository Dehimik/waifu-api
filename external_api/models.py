from typing import List

from pydantic import BaseModel, HttpUrl


class MeowFactResponse(BaseModel):
    """
    {"data": ["..."]}
    """

    data: List[str]


class WaifuPicResponse(BaseModel):
    """
    {"url": "..."}
    """

    url: HttpUrl


class DashboardResponseModel(BaseModel):
    """
    DTO for all APIs
    """

    neko_image_url: HttpUrl
    fact: str
    http_cat_url: HttpUrl
