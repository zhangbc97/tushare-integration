from tushare_integration.models.moneyflow import Moneyflow
from tushare_integration.models.moneyflow_dc import MoneyflowDc
from tushare_integration.models.moneyflow_hsgt import MoneyflowHsgt
from tushare_integration.models.moneyflow_ind_dc import MoneyflowIndDc
from tushare_integration.models.moneyflow_ind_ths import MoneyflowIndThs
from tushare_integration.models.moneyflow_mkt_dc import MoneyflowMktDc
from tushare_integration.models.moneyflow_ths import MoneyflowThs
from tushare_integration.spiders.tushare import DailySpider


class MoneyFlowSpider(DailySpider):
    __spider_name__ = "stock/moneyflow/moneyflow"
    __model__: type[Moneyflow] = Moneyflow


class MoneyFlowHSGTSpider(DailySpider):
    __spider_name__ = "stock/moneyflow/moneyflow_hsgt"
    __model__: type[MoneyflowHsgt] = MoneyflowHsgt


class MoneyFlowDCSpider(DailySpider):
    __spider_name__ = "stock/moneyflow/moneyflow_dc"
    __model__: type[MoneyflowDc] = MoneyflowDc


class MoneyFlowIndDCSpider(DailySpider):
    __spider_name__ = "stock/moneyflow/moneyflow_ind_dc"
    __model__: type[MoneyflowIndDc] = MoneyflowIndDc


class MoneyFlowIndTHSSpider(DailySpider):
    __spider_name__ = "stock/moneyflow/moneyflow_ind_ths"
    __model__: type[MoneyflowIndThs] = MoneyflowIndThs


class MoneyFlowMktDCSpider(DailySpider):
    __spider_name__ = "stock/moneyflow/moneyflow_mkt_dc"
    __model__: type[MoneyflowMktDc] = MoneyflowMktDc


class MoneyFlowTHSSpider(DailySpider):
    __spider_name__ = "stock/moneyflow/moneyflow_ths"
    __model__: type[MoneyflowThs] = MoneyflowThs
