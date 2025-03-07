from tushare_models.moneyflow import Moneyflow
from tushare_models.moneyflow_dc import MoneyflowDc
from tushare_models.moneyflow_hsgt import MoneyflowHsgt
from tushare_models.moneyflow_ind_dc import MoneyflowIndDc
from tushare_models.moneyflow_ind_ths import MoneyflowIndThs
from tushare_models.moneyflow_mkt_dc import MoneyflowMktDc
from tushare_models.moneyflow_ths import MoneyflowThs

from tushare_integration.spiders.tushare import TimeSeriesSpider


class MoneyFlowSpider(TimeSeriesSpider):
    __model__: type[Moneyflow] = Moneyflow


class MoneyFlowTHSSpider(TimeSeriesSpider):
    __model__: type[MoneyflowThs] = MoneyflowThs


class MoneyFlowDCSpider(TimeSeriesSpider):
    __model__: type[MoneyflowDc] = MoneyflowDc


class MoneyFlowIndTHSSpider(TimeSeriesSpider):
    __model__: type[MoneyflowIndThs] = MoneyflowIndThs


class MoneyFlowIndDCSpider(TimeSeriesSpider):
    __model__: type[MoneyflowIndDc] = MoneyflowIndDc


class MoneyFlowMktDCSpider(TimeSeriesSpider):
    __model__: type[MoneyflowMktDc] = MoneyflowMktDc


class MoneyFlowHSGTSpider(TimeSeriesSpider):
    __model__: type[MoneyflowHsgt] = MoneyflowHsgt
