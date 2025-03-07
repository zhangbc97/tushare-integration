# 新增导入
from tushare_models.cn_cpi import CnCpi
from tushare_models.cn_gdp import CnGdp
from tushare_models.cn_m import CnM
from tushare_models.cn_pmi import CnPmi
from tushare_models.cn_ppi import CnPpi
from tushare_models.gz_index import GzIndex
from tushare_models.hibor import Hibor
from tushare_models.libor import Libor
from tushare_models.sf_month import SfMonth
from tushare_models.shibor import Shibor
from tushare_models.shibor_lpr import ShiborLpr
from tushare_models.shibor_quote import ShiborQuote
from tushare_models.wz_index import WzIndex

from tushare_integration.spiders.tushare import LimitOffsetSpider, TushareSpider


class ShiborSpider(LimitOffsetSpider):
    __model__ = Shibor


class ShiborQuoteSpider(LimitOffsetSpider):
    __model__ = ShiborQuote


class ShiborLprSpider(LimitOffsetSpider):
    __model__ = ShiborLpr


class LiborSpider(LimitOffsetSpider):
    __model__ = Libor


class HiborSpider(LimitOffsetSpider):
    __model__ = Hibor


class WzIndexSpider(TushareSpider):
    __model__ = WzIndex


class GzIndexSpider(TushareSpider):
    __model__ = GzIndex


class CnGdpSpider(TushareSpider):
    __model__ = CnGdp


class CnCpiSpider(TushareSpider):
    __model__ = CnCpi


class CnPpiSpider(TushareSpider):
    __model__ = CnPpi


class CnMSpider(TushareSpider):
    __model__ = CnM


class SfMonthSpider(TushareSpider):
    __model__ = SfMonth


class CnPmiSpider(TushareSpider):
    __model__ = CnPmi
