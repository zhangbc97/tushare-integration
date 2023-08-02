from tushare_integration.spiders.tushare import DailySpider, TushareSpider, FinancialReportSpider, TSCodeSpider


class MarginSpider(DailySpider):
    name = "stock/market/margin"
    api_name = "margin"
    custom_settings = {"TABLE_NAME": "margin", 'MIN_CAL_DATE': '2010-01-01'}


class MarginDetailSpider(DailySpider):
    name = "stock/market/margin_detail"
    api_name = "margin_detail"
    custom_settings = {"TABLE_NAME": "margin_detail", 'MIN_CAL_DATE': '2010-01-01'}


class MarginTargetSpider(TSCodeSpider):
    name = "stock/market/margin_target"
    api_name = "margin_target"
    custom_settings = {"TABLE_NAME": "margin_detail", "BASIC_TABLE": "stock_basic"}


class Top10HoldersSpider(FinancialReportSpider):
    name = "stock/market/top10_holders"
    api_name = "top10_holders"
    custom_settings = {"TABLE_NAME": "top10_holders", "HAS_VIP": False}


class Top10FloatHoldersSpider(FinancialReportSpider):
    name = "stock/market/top10_floatholders"
    api_name = "top10_floatholders"
    custom_settings = {"TABLE_NAME": "top10_floatholders", "HAS_VIP": False}


class TopListSpider(DailySpider):
    name = "stock/market/top_list"
    api_name = "top_list"
    custom_settings = {"TABLE_NAME": "top_list", 'MIN_CAL_DATE': '2005-01-01'}


class TopInstSpider(DailySpider):
    name = "stock/market/top_inst"
    api_name = "top_inst"
    custom_settings = {"TABLE_NAME": "top_inst", 'MIN_CAL_DATE': '2005-01-01'}


class PledgeStatSpider(TSCodeSpider):
    name = "stock/market/pledge_stat"
    api_name = "pledge_stat"
    custom_settings = {"TABLE_NAME": "pledge_stat", "BASIC_TABLE": "stock_basic"}


class PledgeDetailSpider(TSCodeSpider):
    name = "stock/market/pledge_detail"
    api_name = "pledge_detail"
    custom_settings = {"TABLE_NAME": "pledge_detail", "BASIC_TABLE": "stock_basic"}


class RepurchaseSpider(TSCodeSpider):
    name = "stock/market/repurchase"
    api_name = "repurchase"
    custom_settings = {"TABLE_NAME": "repurchase", "BASIC_TABLE": "stock_basic"}


class ConceptSpider(TushareSpider):
    name = "stock/market/concept"
    api_name = "concept"
    custom_settings = {"TABLE_NAME": "concept"}


class ConceptDetailSpider(TSCodeSpider):
    name = "stock/market/concept_detail"
    api_name = "concept_detail"
    custom_settings = {"TABLE_NAME": "concept_detail"}

    def start_requests(self):
        conn = self.get_db_engine()

        for code in conn.query_df('SELECT code FROM concept')['code']:
            yield self.get_scrapy_request(
                params={'id': code}
            )


class BlockTradeSpider(DailySpider):
    name = "stock/market/block_trade"
    api_name = "block_trade"
    custom_settings = {"TABLE_NAME": "block_trade"}


class StkHoldernumberSpider(DailySpider):
    name = "stock/market/stk_holdernumber"
    api_name = "stk_holdernumber"
    custom_settings = {"TABLE_NAME": "stk_holdernumber", "TRADE_DATE_FIELD": "ann_date"}


class StkHoldertradeSpider(DailySpider):
    name = "stock/market/stk_holdertrade"
    api_name = "stk_holdertrade"
    custom_settings = {"TABLE_NAME": "stk_holdertrade", "TRADE_DATE_FIELD": "ann_date"}
