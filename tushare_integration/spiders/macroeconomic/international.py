from typing import Type

from tushare_integration.models.us_tbr import UsTbr
from tushare_integration.models.us_tltr import UsTltr
from tushare_integration.models.us_trltr import UsTrltr
from tushare_integration.models.us_trycr import UsTrycr
from tushare_integration.models.us_tycr import UsTycr
from tushare_integration.spiders.tushare import LimitOffsetSpider


class UsTycrSpider(LimitOffsetSpider):
    __model__: Type[UsTycr] = UsTycr
    __limit__: int = 2000


class UsTrycrSpider(LimitOffsetSpider):
    __model__: Type[UsTrycr] = UsTrycr
    __limit__: int = 2000


class UsTbrSpider(LimitOffsetSpider):
    __model__: Type[UsTbr] = UsTbr
    __limit__: int = 2000


class UsTltrSpider(LimitOffsetSpider):
    __model__: Type[UsTltr] = UsTltr
    __limit__: int = 2000


class UsTrltrSpider(LimitOffsetSpider):
    __model__: Type[UsTrltr] = UsTrltr
    __limit__: int = 2000
