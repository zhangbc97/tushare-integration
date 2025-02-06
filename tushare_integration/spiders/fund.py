import datetime

from tushare_integration.models.fund_adj import FundAdj
from tushare_integration.models.fund_basic import FundBasic
from tushare_integration.models.fund_company import FundCompany
from tushare_integration.models.fund_daily import FundDaily
from tushare_integration.models.fund_div import FundDiv
from tushare_integration.models.fund_factor_pro import FundFactorPro
from tushare_integration.models.fund_manager import FundManager
from tushare_integration.models.fund_nav import FundNav
from tushare_integration.models.fund_portfolio import FundPortfolio
from tushare_integration.models.fund_share import FundShare
from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TSCodeSpider, TushareSpider


# 基金基础数据 Spider，静态信息接口
class FundBasicSpider(TushareSpider):
    __model__: type[FundBasic] = FundBasic

    def start_requests(self):
        for market in ['E', 'O']:
            for status in ['D', 'I', 'L']:
                yield self.get_httpx_request(params={'market': market, 'status': status})


# 基金管理人信息 Spider，静态信息接口
class FundCompanySpider(TushareSpider):
    __model__: type[FundCompany] = FundCompany


# 基金经理信息 Spider，静态信息接口
class FundManagerSpider(TushareSpider):
    __model__: type[FundManager] = FundManager


# 基金份额数据 Spider，时序数据接口
class FundShareSpider(TimeSeriesSpider):
    __model__: type[FundShare] = FundShare


# 基金净值数据 Spider，时序数据接口
class FundNavSpider(TimeSeriesSpider):
    __model__: type[FundNav] = FundNav
    __trade_date_field__: str = 'nav_date'


# 基金分红数据 Spider，时序数据接口
class FundDivSpider(TSCodeSpider):
    __model__: type[FundDiv] = FundDiv
    __basic_table__: type[FundBasic] = FundBasic


# 基金持仓数据 Spider，时序数据接口
class FundPortfolioSpider(LimitOffsetSpider):
    __model__: type[FundPortfolio] = FundPortfolio
    __limit__: int = 4000

    @staticmethod
    def get_all_period():
        periods = []
        for year in range(1990, datetime.datetime.now().year + 1):
            for end_date in [f"{year}0331", f"{year}0630", f"{year}0930", f"{year}1231"]:
                periods.append(end_date)
        return periods

    def start_requests(self):
        for period in self.get_all_period():
            yield self.get_httpx_request(params={"period": period})


# 基金行情数据 Spider，时序数据接口
class FundDailySpider(TimeSeriesSpider):
    __model__: type[FundDaily] = FundDaily


# 基金复权因子 Spider，时序数据接口
class FundAdjSpider(TimeSeriesSpider):
    __model__: type[FundAdj] = FundAdj


# 基金技术面因子(专业版) Spider，时序数据接口
class FundFactorProSpider(TimeSeriesSpider):
    __model__: type[FundFactorPro] = FundFactorPro
