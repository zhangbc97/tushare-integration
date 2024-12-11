import re
from pathlib import Path

# 硬编码所有的开始日期配置
START_DATES = {
    # 特色数据
    'cyq_perf': '2018-01-02',
    'cyq_chips': '2010-01-01',
    'ccass_hold': '2020-11-11',
    'ccass_hold_detail': '2016-12-05',
    'hk_hold': '2016-06-29',
    # 行情数据
    'suspend_d': '1999-05-04',
    'hsgt_top10': '2014-11-17',
    'stk_limit': '2007-01-01',
    'ggt_top10': '2014-11-17',
    'ggt_daily': '2014-11-17',
    'bak_daily': '2017-06-14',
    # 资金流向
    'moneyflow_hsgt': '2014-11-17',
    'moneyflow_dc': '2023-09-11',
    'moneyflow_ind_dc': '2023-09-12',
    'moneyflow_ind_ths': '2024-09-10',
    'moneyflow_mkt_dc': '2023-04-17',
    'moneyflow_ths': '2019-07-26',
    # 市场数据
    'top_list': '2005-01-01',
    'top_inst': '2005-01-01',
    # 融资融券
    'margin': '2010-01-01',
    'margin_detail': '2010-01-01',
    'slb_len_mm': '2022-11-14',
    'slb_sec_detail': '2019-07-22',
    'slb_sec': '2013-02-28',
    # 涨跌停数据
    'dc_hot': '2024-03-20',
    'hm_detail': '2022-08-01',
    'ths_hot': '2020-01-01',
    # 基础数据
    'bak_basic': '2016-08-01',
    # 指数数据
    'sz_daily_info': '2008-01-02',
    # 期货数据
    'fut_settle': '2012-01-04',
    'fut_mapping': '1995-04-17',
    'fut_wsr': '2006-01-06',
}


def update_model_start_date(model_file: Path, start_date: str) -> None:
    """更新模型文件中的 start_date

    Args:
        model_file: 模型文件路径
        start_date: 开始日期
    """
    if not model_file.exists():
        print(f"Model file not found: {model_file}")
        return

    content = model_file.read_text(encoding='utf-8')

    # 查找 __start_date__ 的行
    start_date_pattern = r'__start_date__: ClassVar\[str \| None\] = .*'

    # 替换 start_date
    new_content = re.sub(start_date_pattern, f'__start_date__: ClassVar[str | None] = "{start_date}"', content)

    # 如果内容有变化，写入文件
    if new_content != content:
        model_file.write_text(new_content, encoding='utf-8')
        print(f"Updated {model_file.name} with start_date: {start_date}")
    else:
        print(f"No changes needed for {model_file.name}")


def main():
    # 模型文件目录
    models_dir = Path('tushare_integration/models')

    if not models_dir.exists():
        print(f"Models directory not found: {models_dir}")
        return

    # 处理每个配置
    for model_name, start_date in START_DATES.items():
        model_file = models_dir / f"{model_name}.py"
        try:
            update_model_start_date(model_file, start_date)
        except Exception as e:
            print(f"Error processing {model_name}: {str(e)}")


if __name__ == '__main__':
    main()
