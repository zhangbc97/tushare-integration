from tushare_integration.models.moneyflow import Moneyflow
from tushare_integration.models.moneyflow_dc import MoneyflowDc
from tushare_integration.models.moneyflow_hsgt import MoneyflowHsgt
from tushare_integration.models.moneyflow_ind_dc import MoneyflowIndDc
from tushare_integration.models.moneyflow_ind_ths import MoneyflowIndThs
from tushare_integration.models.moneyflow_mkt_dc import MoneyflowMktDc
from tushare_integration.models.moneyflow_ths import MoneyflowThs
from tushare_integration.spiders.tushare import TimeSeriesSpider


class MoneyFlowSpider(TimeSeriesSpider):
    __model__: type[Moneyflow] = Moneyflow


class MoneyFlowHSGTSpider(TimeSeriesSpider):
    __model__: type[MoneyflowHsgt] = MoneyflowHsgt


class MoneyFlowDCSpider(TimeSeriesSpider):
    __model__: type[MoneyflowDc] = MoneyflowDc


class MoneyFlowIndDCSpider(TimeSeriesSpider):
    __model__: type[MoneyflowIndDc] = MoneyflowIndDc


class MoneyFlowIndTHSSpider(TimeSeriesSpider):
    __model__: type[MoneyflowIndThs] = MoneyflowIndThs


class MoneyFlowMktDCSpider(TimeSeriesSpider):
    __model__: type[MoneyflowMktDc] = MoneyflowMktDc


class MoneyFlowTHSSpider(TimeSeriesSpider):
    __model__: type[MoneyflowThs] = MoneyflowThs
