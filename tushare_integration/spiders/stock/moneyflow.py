from tushare_integration.spiders.tushare import DailySpider


class MoneyFlowSpider(DailySpider):
    name = "stock/moneyflow/moneyflow"
    custom_settings = {"TABLE_NAME": "moneyflow"}


class MoneyFlowHSGTSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_hsgt"
    custom_settings = {"TABLE_NAME": "moneyflow_hsgt", "MIN_CAL_DATE": "2014-11-17"}


class MoneyFlowDCSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_dc"
    custom_settings = {
        "TABLE_NAME": "moneyflow_dc",
    }


class MoneyFlowIndDCSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_ind_dc"
    custom_settings = {
        "TABLE_NAME": "moneyflow_ind_dc",
    }


class MoneyFlowIndTHSSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_ind_ths"
    custom_settings = {
        "TABLE_NAME": "moneyflow_ind_ths",
    }


class MoneyFlowMktDCSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_mkt_dc"
    custom_settings = {
        "TABLE_NAME": "moneyflow_mkt_dc",
    }


class MoneyFlowTHSSpider(DailySpider):
    name = "stock/moneyflow/moneyflow_ths"
    custom_settings = {
        "TABLE_NAME": "moneyflow_ths",
    }
