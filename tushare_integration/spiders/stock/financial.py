from tushare_integration.models.balancesheet import Balancesheet
from tushare_integration.models.cashflow import Cashflow
from tushare_integration.models.disclosure_date import DisclosureDate
from tushare_integration.models.dividend import Dividend
from tushare_integration.models.express import Express
from tushare_integration.models.fina_audit import FinaAudit
from tushare_integration.models.fina_indicator import FinaIndicator
from tushare_integration.models.fina_mainbz import FinaMainbz
from tushare_integration.models.forecast import Forecast
from tushare_integration.models.income import Income
from tushare_integration.spiders.tushare import FinancialReportSpider


class IncomeSpider(FinancialReportSpider):
    __model__: type[Income] = Income


class BalanceSheetSpider(FinancialReportSpider):
    __model__: type[Balancesheet] = Balancesheet


class CashFlowSpider(FinancialReportSpider):
    __model__: type[Cashflow] = Cashflow


class ForeCastSpider(FinancialReportSpider):
    __model__: type[Forecast] = Forecast


class ExpressSpider(FinancialReportSpider):
    __model__: type[Express] = Express


class DividendSpider(FinancialReportSpider):
    __model__: type[Dividend] = Dividend


class FinaIndicatorSpider(FinancialReportSpider):
    __model__: type[FinaIndicator] = FinaIndicator


class FinaAuditSpider(FinancialReportSpider):
    __model__: type[FinaAudit] = FinaAudit


class FinaMainBZSpider(FinancialReportSpider):
    __model__: type[FinaMainbz] = FinaMainbz


class DisclosureDateSpider(FinancialReportSpider):
    __model__: type[DisclosureDate] = DisclosureDate

    def start_requests(self):
        periods = self.get_all_period()
        for period in periods:
            yield self.get_httpx_request(params={"end_date": period})
