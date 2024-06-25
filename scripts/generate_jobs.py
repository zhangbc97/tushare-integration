import json

spiders = [
    'future/basic/fut_basic',
    'future/quotes/fut_daily',
    'future/quotes/fut_holding',
    'future/quotes/fut_settle',
    'future/quotes/fut_mapping',
    'future/quotes/fut_wsr',
    'future/quotes/fut_weekly_detail',
    'index/basic/index_basic',
    'index/quotes/index_daily',
    'index/quotes/daily_info',
    'index/quotes/index_dailybasic',
    'index/quotes/index_global',
    'index/quotes/index_monthly',
    'index/quotes/index_weekly',
    'index/quotes/index_weight',
    'index/quotes/sz_daily_info',
    'index/sw/index_classify',
    'index/sw/index_member',
    'index/ths/ths_daily',
    'index/ths/ths_index',
    'index/ths/ths_member',
    'index/zx/ci_daily',
    'stock/basic/stock_basic',
    'stock/basic/namechange',
    'stock/basic/hs_const',
    'stock/basic/trade_cal',
    'stock/basic/stock_company',
    'stock/basic/stk_managers',
    'stock/basic/stk_rewards',
    'stock/basic/new_share',
    'stock/basic/stk_premarket',
    'stock/basic/bak_basic',
    'stock/financial/balancesheet',
    'stock/financial/cashflow',
    'stock/financial/income',
    'stock/financial/express',
    'stock/financial/forecast',
    'stock/financial/dividend',
    'stock/financial/fina_indicator',
    'stock/financial/fina_audit',
    'stock/financial/fina_mainbz',
    'stock/financial/disclosure_date',
    'stock/margin/margin',
    'stock/margin/margin_detail',
    'stock/margin/slb_len_mm',
    'stock/margin/slb_len',
    'stock/margin/slb_sec_detail',
    'stock/margin/slb_sec',
    'stock/market/margin_secs',
    'stock/market/top10_holders',
    'stock/market/top10_floatholders',
    'stock/market/top_list',
    'stock/market/top_inst',
    'stock/market/pledge_stat',
    'stock/market/pledge_detail',
    'stock/market/repurchase',
    'stock/market/share_float',
    'stock/market/concept',
    'stock/market/concept_detail',
    'stock/market/block_trade',
    'stock/market/stk_holdernumber',
    'stock/market/stk_holdertrade',
    'stock/quotes/daily',
    'stock/quotes/weekly',
    'stock/quotes/monthly',
    'stock/quotes/adj_factor',
    'stock/quotes/suspend_d',
    'stock/quotes/hsgt_top10',
    'stock/quotes/moneyflow',
    'stock/quotes/moneyflow_hsgt',
    'stock/quotes/stk_limit',
    'stock/quotes/daily_basic',
    'stock/quotes/ggt_top10',
    'stock/quotes/ggt_daily',
    'stock/quotes/bak_daily',
    'stock/quotes/stk_mins',
    'stock/special/report_rc',
    'stock/special/cyq_perf',
    'stock/special/cyq_chips',
    'stock/special/stk_factor',
    'stock/special/ccass_hold',
    'stock/special/ccass_hold_detail',
    'stock/special/hk_hold',
    'stock/special/limit_list_d',
    'stock/special/stk_surv',
    'stock/special/broker_recommend',
    'stock/special/hm_list',
    'stock/special/hm_detail',
]

# 按照/分割，前两段加起来是分组
data = {
    'cronjob': [
        # {'cron_expr':'','name':'','spiders':[{'name':''}]}
    ]
}

data_tmp = {}

# 前两段是分组，作为cronjob的name，然后spider的name作为spiders的name
for spider in spiders:
    group = spider.split('/')[0] + '/' + spider.split('/')[1]
    if group not in data_tmp:
        data_tmp[group] = []
    data_tmp[group].append({'name': spider})

for group in data_tmp:
    if group == 'cronjob':
        continue
    data['cronjob'].append({'cron_expr': 'UnSupported', 'name': group, 'spiders': data_tmp[group]})

print(json.dumps(data))
