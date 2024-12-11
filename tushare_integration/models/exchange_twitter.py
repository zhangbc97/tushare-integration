# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class ExchangeTwitter(Base):
    """交易所Twitter数据"""

    __tablename__: str = 'exchange_twitter'
    __api_id__: ClassVar[int] = 92
    __api_name__: ClassVar[str] = 'exchange_twitter'
    __api_title__: ClassVar[str] = '交易所Twitter数据'
    __api_info_title__: ClassVar[str] = '数字货币交易所Twitter'
    __api_path__: ClassVar[List[str]] = ['另类数据', '资讯公告', '交易所Twitter数据']
    __api_path_ids__: ClassVar[List[int]] = [41, 69, 92]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'start_date': {'type': 'datetime', 'required': True, 'description': '开始时间'}, 'end_date': {'type': 'datetime', 'required': True, 'description': '结束时间'}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '交易所Twitter数据',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    id = Column('id', Integer, nullable=False, default=0, server_default=text("'0'"), comment='记录ID')
    account_id = Column('account_id', Integer, nullable=False, default=0, server_default=text("'0'"), comment='交易所账号ID')
    account = Column('account', String(), nullable=False, default="", server_default=text("''"), comment='交易所账号')
    nickname = Column('nickname', String(), nullable=False, default="", server_default=text("''"), comment='交易所昵称')
    avatar = Column('avatar', String(), nullable=False, default="", server_default=text("''"), comment='头像')
    content_id = Column('content_id', Integer, nullable=False, default=0, server_default=text("'0'"), comment='类容ID')
    content = Column('content', String(), nullable=False, default="", server_default=text("''"), comment='内容')
    is_retweet = Column('is_retweet', Integer, nullable=False, default=0, server_default=text("'0'"), comment='是否转发')
    retweet_content = Column('retweet_content', String(), nullable=False, default="{}", server_default=text("'{}'"), comment='转发内容')
    media = Column('media', String(), nullable=False, default="{}", server_default=text("'{}'"), comment='附件')
    posted_at = Column('posted_at', Integer, nullable=False, default=0, server_default=text("'0'"), comment='发布时间戳')
    content_translation = Column('content_translation', String(), nullable=False, default="", server_default=text("''"), comment='内容翻译')
    str_posted_at = Column('str_posted_at', String(), nullable=False, default="", server_default=text("''"), comment='发布时间，根据posted_at转换而来')
    create_at = Column('create_at', String(), nullable=False, default="", server_default=text("''"), comment='采集时间')