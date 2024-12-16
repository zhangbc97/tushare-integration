from tushare_integration.models.moneyflow import Moneyflow
from tushare_integration.models.moneyflow_dc import MoneyflowDc
from tushare_integration.models.moneyflow_hsgt import MoneyflowHsgt
from tushare_integration.models.moneyflow_ind_dc import MoneyflowIndDc
from tushare_integration.models.moneyflow_ind_ths import MoneyflowIndThs
from tushare_integration.models.moneyflow_mkt_dc import MoneyflowMktDc
from tushare_integration.models.moneyflow_ths import MoneyflowThs
from tushare_integration.spiders.tushare import DailySpider


class MoneyFlowSpider(DailySpider):

    __model__: type[Moneyflow] = Moneyflow


class MoneyFlowHSGTSpider(DailySpider):

    __model__: type[MoneyflowHsgt] = MoneyflowHsgt


class MoneyFlowDCSpider(DailySpider):

    __model__: type[MoneyflowDc] = MoneyflowDc


class MoneyFlowIndDCSpider(DailySpider):

    __model__: type[MoneyflowIndDc] = MoneyflowIndDc


class MoneyFlowIndTHSSpider(DailySpider):

    __model__: type[MoneyflowIndThs] = MoneyflowIndThs


class MoneyFlowMktDCSpider(DailySpider):

    __model__: type[MoneyflowMktDc] = MoneyflowMktDc


class MoneyFlowTHSSpider(DailySpider):

    __model__: type[MoneyflowThs] = MoneyflowThs
