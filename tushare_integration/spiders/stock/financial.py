from tushare_integration.spiders.tushare import FinancialReportSpider, TSCodeSpider
from tushare_integration.models.balancesheet import Balancesheet
from tushare_integration.models.cashflow import Cashflow
from tushare_integration.models.income import Income
from tushare_integration.models.express import Express
from tushare_integration.models.forecast import Forecast
from tushare_integration.models.dividend import Dividend
from tushare_integration.models.fina_indicator import FinaIndicator
from tushare_integration.models.fina_audit import FinaAudit
from tushare_integration.models.fina_mainbz import FinaMainbz
from tushare_integration.models.disclosure_date import DisclosureDate


class BalanceSheetSpider(FinancialReportSpider):
    name = "stock/financial/balancesheet"
    __model__: type[Balancesheet] = Balancesheet


class CashFlowSpider(FinancialReportSpider):
    name = "stock/financial/cashflow"
    __model__: type[Cashflow] = Cashflow


class IncomeSpider(FinancialReportSpider):
    name = "stock/financial/income"
    __model__: type[Income] = Income


class ExpressSpider(FinancialReportSpider):
    name = "stock/financial/express"
    __model__: type[Express] = Express


class ForeCastSpider(FinancialReportSpider):
    name = "stock/financial/forecast"
    __model__: type[Forecast] = Forecast


class DividendSpider(TSCodeSpider):
    name = "stock/financial/dividend"
    __model__: type[Dividend] = Dividend
    custom_settings = {'BASIC_TABLE': 'stock_basic'}


class FinaIndicatorSpider(FinancialReportSpider):
    name = "stock/financial/fina_indicator"
    __model__: type[FinaIndicator] = FinaIndicator


class FinaAuditSpider(TSCodeSpider):
    name = "stock/financial/fina_audit"
    __model__: type[FinaAudit] = FinaAudit
    custom_settings = {'BASIC_TABLE': 'stock_basic'}


class FinaMainBZSpider(FinancialReportSpider):
    name = "stock/financial/fina_mainbz"
    __model__: type[FinaMainbz] = FinaMainbz


class DisclosureDateSpider(FinancialReportSpider):
    name = "stock/financial/disclosure_date"
    __model__: type[DisclosureDate] = DisclosureDate

    def start_requests(self):
        periods = self.get_all_period()
        for period in periods:
            yield self.get_scrapy_request(params={"end_date": period})
