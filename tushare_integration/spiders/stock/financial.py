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


# class DividendSpider(FinancialReportSpider):
#     name = "stock/financial/dividend"
#     api_name = "dividend"
#     custom_settings = {
#         "TABLE_NAME": "dividend",
#     }


class FinaIndicatorSpider(FinancialReportSpider):
    name = "stock/financial/fina_indicator"
    api_name = "fina_indicator"
    custom_settings = {
        "TABLE_NAME": "fina_indicator",
    }


# class FinaAuditSpider(FinancialReportSpider):
#     name = "stock/financial/fina_audit"
#     api_name = "fina_audit"
#     custom_settings = {
#         "TABLE_NAME": "fina_audit",
#     }


class FinaMainBZSpider(FinancialReportSpider):
    name = "stock/financial/fina_mainbz"
    api_name = "fina_mainbz"
    custom_settings = {
        "TABLE_NAME": "fina_mainbz",
    }


# class DisclosureDateSpider(FinancialReportSpider):
#     name = "stock/financial/disclosure_date"
#     api_name = "disclosure_date"
#     custom_settings = {
#         "TABLE_NAME": "disclosure_date",
#     }
