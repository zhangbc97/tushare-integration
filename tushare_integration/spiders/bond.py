# 导入基础 Spider 类
import itertools

from sqlalchemy import select

from tushare_integration.models.bc_bestotcqt import BcBestotcqt
from tushare_integration.models.bc_otcqt import BcOtcqt
from tushare_integration.models.bond_blk import BondBlk
from tushare_integration.models.bond_blk_detail import BondBlkDetail

# 导入债券相关的数据模型
from tushare_integration.models.cb_basic import CbBasic
from tushare_integration.models.cb_call import CbCall
from tushare_integration.models.cb_daily import CbDaily
from tushare_integration.models.cb_issue import CbIssue
from tushare_integration.models.cb_price_chg import CbPriceChg
from tushare_integration.models.cb_rate import CbRate
from tushare_integration.models.cb_share import CbShare
from tushare_integration.models.eco_cal import EcoCal
from tushare_integration.models.repo_daily import RepoDaily
from tushare_integration.models.yc_cb import YcCb
from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TSCodeSpider, TushareSpider


class CbBasicSpider(TushareSpider):
    __model__: type[CbBasic] = CbBasic


class CbIssueSpider(TushareSpider):
    __model__: type[CbIssue] = CbIssue


class CbCallSpider(LimitOffsetSpider):
    __model__: type[CbCall] = CbCall
    __basic_table__ = CbBasic


class CbRateSpider(TSCodeSpider):
    __model__: type[CbRate] = CbRate
    __basic_table__ = CbBasic


class CbDailySpider(TimeSeriesSpider):
    __model__: type[CbDaily] = CbDaily


class CbPriceChgSpider(TSCodeSpider):
    __model__: type[CbPriceChg] = CbPriceChg
    __basic_table__ = CbBasic

    def start_requests(self):
        conn = self.get_db_engine()
        query = select(getattr(self.__basic_table__, 'ts_code')).distinct()
        ts_codes = conn.query_df(query)['ts_code'].tolist()
        codes_iter = iter(ts_codes)
        yield from map(
            lambda group: self.get_httpx_request(params={"ts_code": ",".join(group)}),
            iter(lambda: tuple(itertools.islice(codes_iter, 10)), ()),
        )


class CbShareSpider(TSCodeSpider):
    __model__: type[CbShare] = CbShare
    __basic_table__: type[CbBasic] = CbBasic

    def start_requests(self):
        conn = self.get_db_engine()
        query = select(getattr(self.__basic_table__, 'ts_code')).distinct()
        ts_codes = conn.query_df(query)['ts_code'].tolist()
        codes_iter = iter(ts_codes)
        yield from map(
            lambda group: self.get_httpx_request(params={"ts_code": ",".join(group)}),
            iter(lambda: tuple(itertools.islice(codes_iter, 10)), ()),
        )


class RepoDailySpider(TimeSeriesSpider):
    __model__: type[RepoDaily] = RepoDaily


class BcOtcqtSpider(LimitOffsetSpider):
    __model__: type[BcOtcqt] = BcOtcqt


class BcBestotcqtSpider(LimitOffsetSpider):
    __model__: type[BcBestotcqt] = BcBestotcqt


class BondBlkSpider(TimeSeriesSpider):
    __model__: type[BondBlk] = BondBlk


class BondBlkDetailSpider(TimeSeriesSpider):
    __model__: type[BondBlkDetail] = BondBlkDetail


class YcCbSpider(TimeSeriesSpider):
    __model__: type[YcCb] = YcCb


class EcoCalSpider(TimeSeriesSpider):
    __model__: type[EcoCal] = EcoCal
