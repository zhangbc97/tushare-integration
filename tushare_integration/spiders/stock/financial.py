from tushare_integration.spiders.tushare import FinancialReportSpider


class BalanceSheetSpider(FinancialReportSpider):
    name = "stock/financial/balancesheet"
    api_name = "balancesheet"
    custom_settings = {
        "TABLE_NAME": "balancesheet",
    }


class CashFlowSpider(FinancialReportSpider):
    name = "stock/financial/cashflow"
    api_name = "cashflow"
    custom_settings = {
        "TABLE_NAME": "cashflow",
    }


class IncomeSpider(FinancialReportSpider):
    name = "stock/financial/income"
    api_name = "income"
    custom_settings = {
        "TABLE_NAME": "income",
    }


class ExpressSpider(FinancialReportSpider):
    name = "stock/financial/express"
    api_name = "express"
    custom_settings = {
        "TABLE_NAME": "express",
    }


class ForeCastSpider(FinancialReportSpider):
    name = "stock/financial/forecast"
    api_name = "forecast"
    custom_settings = {
        "TABLE_NAME": "forecast",
    }
