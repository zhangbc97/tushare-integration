from tushare_integration.spiders.tushare import DailySpider
from tushare_integration.models.moneyflow import Moneyflow
from tushare_integration.models.moneyflow_hsgt import MoneyflowHsgt
from tushare_integration.models.moneyflow_dc import MoneyflowDc
from tushare_integration.models.moneyflow_ind_dc import MoneyflowIndDc
from tushare_integration.models.moneyflow_ind_ths import MoneyflowIndThs
from tushare_integration.models.moneyflow_mkt_dc import MoneyflowMktDc
from tushare_integration.models.moneyflow_ths import MoneyflowThs


class MoneyFlowSpider(DailySpider):
    name = "stock/moneyflow/moneyflow"
    __model__: type[Moneyflow] = Moneyflow


class MoneyFlowHSGTSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_hsgt"
    __model__: type[MoneyflowHsgt] = MoneyflowHsgt


class MoneyFlowDCSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_dc"
    __model__: type[MoneyflowDc] = MoneyflowDc


class MoneyFlowIndDCSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_ind_dc"
    __model__: type[MoneyflowIndDc] = MoneyflowIndDc


class MoneyFlowIndTHSSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_ind_ths"
    __model__: type[MoneyflowIndThs] = MoneyflowIndThs


class MoneyFlowMktDCSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_mkt_dc"
    __model__: type[MoneyflowMktDc] = MoneyflowMktDc


class MoneyFlowTHSSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_ths"
    __model__: type[MoneyflowThs] = MoneyflowThs
