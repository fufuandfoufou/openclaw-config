#!/usr/bin/env python3
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import tushare as ts


def load_token():
    env_file = os.environ.get('TUSHARE_STOCK_ENV_FILE') or str(Path.home()/'.config/tushare-stock/skill.env')
    p = Path(env_file)
    if not p.exists():
        raise SystemExit('TUSHARE token file missing')
    for line in p.read_text().splitlines():
        if line.startswith('TUSHARE_TOKEN='):
            return line.split('=',1)[1].strip()
    raise SystemExit('TUSHARE_TOKEN missing')


def main():
    token = load_token()
    pro = ts.pro_api(token)
    trade_cal = pro.trade_cal(exchange='SSE', start_date='20260301', end_date=datetime.now().strftime('%Y%m%d'))
    trade_cal = trade_cal[trade_cal['is_open']==1].sort_values('cal_date')
    trade_date = trade_cal.iloc[-1]['cal_date']
    start_date = (pd.to_datetime(trade_date) - pd.Timedelta(days=50)).strftime('%Y%m%d')

    basic = pro.daily_basic(trade_date=trade_date, fields='ts_code,close,turnover_rate,volume_ratio,pe,pb,total_mv,circ_mv')
    daily = pro.daily(trade_date=trade_date, fields='ts_code,open,high,low,close,pre_close,change,pct_chg,vol,amount')
    mf = pro.moneyflow(trade_date=trade_date)
    limit_df = pro.limit_list_d(trade_date=trade_date)
    names = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name,industry,market')

    df = basic.merge(daily, on='ts_code', suffixes=('_basic','_daily')).merge(names, on='ts_code', how='left')
    df['close_px'] = df['close_basic']
    df = df[(df['close_px'] >= 4) & (df['amount'] >= 150000) & (df['turnover_rate'] >= 0.8)]
    df = df[~df['name'].str.contains('ST', na=False)]

    if not mf.empty:
        cols=['ts_code','buy_lg_amount','sell_lg_amount','buy_elg_amount','sell_elg_amount']
        m = mf[cols].copy()
        m['main_net'] = m['buy_lg_amount'] + m['buy_elg_amount'] - m['sell_lg_amount'] - m['sell_elg_amount']
        df = df.merge(m[['ts_code','main_net']], on='ts_code', how='left')
    else:
        df['main_net'] = 0

    if not limit_df.empty:
        df = df.merge(limit_df[['ts_code','limit','open_times']], on='ts_code', how='left')
    else:
        df['limit'] = None; df['open_times'] = None

    pre = df.copy()
    pre['score0'] = (
        pre['pct_chg'].clip(-5,10)*0.8 +
        pre['turnover_rate'].clip(0,20)*0.2 +
        pre['volume_ratio'].fillna(1).clip(0,5)*1.2 +
        (pre['main_net'].fillna(0)/1000).clip(-20,20)*0.6
    )
    pre = pre.sort_values('score0', ascending=False).head(120)

    rows = []
    for code in pre['ts_code'].tolist():
        hist = pro.daily(ts_code=code, start_date=start_date, end_date=trade_date, fields='ts_code,trade_date,open,high,low,close,pct_chg,vol,amount')
        if hist is None or hist.empty or len(hist) < 8:
            continue
        hist = hist.sort_values('trade_date')
        c = hist['close'].astype(float); h = hist['high'].astype(float); l = hist['low'].astype(float); v = hist['vol'].astype(float)
        last = float(c.iloc[-1]); ma5 = float(c.tail(5).mean()); ma10 = float(c.tail(10).mean()); ma20 = float(c.tail(20).mean()) if len(c)>=20 else float(c.mean())
        rows.append({
            'ts_code': code,
            'ma5': round(ma5,3), 'ma10': round(ma10,3), 'ma20': round(ma20,3),
            'high5': round(float(h.tail(5).max()),3), 'high10': round(float(h.tail(10).max()),3),
            'low5': round(float(l.tail(5).min()),3), 'low10': round(float(l.tail(10).min()),3),
            'ret5': round((last / float(c.iloc[-6]) - 1) * 100,2) if len(c)>=6 else 0,
            'pos30': round((last - float(l.tail(30).min()))/(float(h.tail(30).max())-float(l.tail(30).min())+1e-9),2),
            'vol_ratio_5_20': round(float(v.tail(5).mean())/(float(v.tail(20).mean())+1e-9),2),
        })
    tech = pd.DataFrame(rows)
    out = pre.merge(tech, on='ts_code', how='inner')
    out['trend_ok'] = ((out['close_px'] >= out['ma5']) & (out['ma5'] >= out['ma10']*0.985)).astype(int)
    out['main_ok'] = (out['main_net'].fillna(0) > 0).astype(int)
    out['final_score'] = out['score0'] + out['trend_ok']*3 + out['main_ok']*2

    def bucket(r):
        if pd.notna(r.get('limit')):
            return '题材池'
        if (r['total_mv'] >= 1500000 and r['amount'] >= 500000):
            return '核心池'
        if (r['turnover_rate'] >= 6 and r['ret5'] >= 5):
            return '弹性池'
        if r['pct_chg'] >= 5 and r['vol_ratio_5_20'] >= 1.2:
            return '题材池'
        return '核心池'

    out['bucket'] = out.apply(bucket, axis=1)
    out = out.sort_values('final_score', ascending=False)

    buckets = {}
    for _, r in out.iterrows():
        b = r['bucket']
        buckets.setdefault(b, [])
        if len(buckets[b]) >= 8:
            continue
        buckets[b].append({
            'ts_code': r['ts_code'], 'name': r['name'], 'industry': r['industry'],
            'close': round(float(r['close_px']),2), 'pct_chg': round(float(r['pct_chg']),2),
            'turnover_rate': round(float(r['turnover_rate']),2),
            'volume_ratio': None if pd.isna(r['volume_ratio']) else round(float(r['volume_ratio']),2),
            'main_net': None if pd.isna(r['main_net']) else round(float(r['main_net']),2),
            'ma5': r['ma5'], 'ma10': r['ma10'], 'ma20': r['ma20'],
            'high5': r['high5'], 'high10': r['high10'], 'low5': r['low5'], 'low10': r['low10'],
            'score': round(float(r['final_score']),2),
        })

    top3 = []
    seen = set()
    for b in ['核心池','弹性池','题材池']:
        for item in buckets.get(b, []):
            if item['industry'] in seen:
                continue
            top3.append(item)
            seen.add(item['industry'])
            if len(top3) >= 3:
                break
        if len(top3) >= 3:
            break

    result = {
        'trade_date': trade_date,
        'a_candidate_buckets': buckets,
        'a_top3_today': top3,
        'source': 'Tushare 日线 / 每日指标 / 资金流 / 涨跌停榜；当前以日线级与盘后数据为主。'
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
