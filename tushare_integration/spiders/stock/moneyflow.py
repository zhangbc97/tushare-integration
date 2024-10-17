from tushare_integration.spiders.tushare import DailySpider


class MoneyFlowSpider(DailySpider):
    name = "stock/moneyflow/moneyflow"
    custom_settings = {"TABLE_NAME": "moneyflow"}


class MoneyFlowHSGTSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_hsgt"
    custom_settings = {"TABLE_NAME": "moneyflow_hsgt", "MIN_CAL_DATE": "2014-11-17"}


class MoneyFlowDCSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_dc"
    custom_settings = {"TABLE_NAME": "moneyflow_dc", "MIN_CAL_DATE": "2023-09-11"}


class MoneyFlowIndDCSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_ind_dc"
    custom_settings = {"TABLE_NAME": "moneyflow_ind_dc", "MIN_CAL_DATE": "2023-09-12"}


class MoneyFlowIndTHSSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_ind_ths"
    custom_settings = {"TABLE_NAME": "moneyflow_ind_ths", "MIN_CAL_DATE": "2024-09-10"}


class MoneyFlowMktDCSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_mkt_dc"
    custom_settings = {"TABLE_NAME": "moneyflow_mkt_dc", "MIN_CAL_DATE": "2023-04-17"}


class MoneyFlowTHSSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_ths"
    custom_settings = {"TABLE_NAME": "moneyflow_ths", "MIN_CAL_DATE": "2019-07-26"}
