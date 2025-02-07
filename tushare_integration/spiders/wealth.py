import datetime  # 新增：用于获取当前日期和计算季度

from tushare_integration.models.fund_sales_ratio import FundSalesRatio
from tushare_integration.models.fund_sales_vol import FundSalesVol
from tushare_integration.spiders.tushare import TimeSeriesSpider, TushareSpider


class FundSalesRatioSpider(TushareSpider):
    __model__: type[FundSalesRatio] = FundSalesRatio


class FundSalesVolSpider(TimeSeriesSpider):
    __model__: type[FundSalesVol] = FundSalesVol

    def start_requests(self):
        start_year = 2021
        start_quarter = 1
        today = datetime.date.today()
        current_year = today.year
        current_quarter = (today.month - 1) // 3 + 1

        for year in range(start_year, current_year + 1):
            # 如果是起始年份，则从 Q1 开始，否则从1季度开始
            quarter_start = start_quarter if year == start_year else 1
            # 如果是当前年份，则遍历到当前季度，否则遍历 4 个季度
            quarter_end = current_quarter if year == current_year else 4

            for quarter in range(quarter_start, quarter_end + 1):
                params = {"year": str(year), "quarter": f"Q{quarter}"}
                yield self.get_httpx_request(params=params)
