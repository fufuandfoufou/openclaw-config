#!/usr/bin/env python3
import json
from datetime import datetime

import akshare as ak
import pandas as pd

WATCHS = [
    {"code": "07226", "name": "南方两倍做多恒生科技", "cost": 4.9, "shares": 4900, "type": "etf"},
    {"code": "03896", "name": "金山云", "cost": 9.5, "shares": 2000, "type": "stock"},
]

CANDIDATES = [
    ("00700", "腾讯控股"), ("01810", "小米集团-W"), ("09988", "阿里巴巴-W"),
    ("09888", "百度集团-SW"), ("09626", "哔哩哔哩-W"), ("09618", "京东集团-SW"),
    ("03888", "金山软件"), ("00175", "吉利汽车"), ("03690", "美团-W"),
    ("02318", "中国平安"), ("09868", "小鹏汽车-W"), ("09866", "蔚来-SW"),
    ("09863", "零跑汽车"), ("01024", "快手-W"), ("02015", "理想汽车-W"),
    ("06618", "京东健康"), ("09999", "网易-S"), ("09633", "农夫山泉"),
    ("03896", "金山云"), ("07226", "南方两倍做多恒生科技"), ("03033", "南方恒生科技")
]


def fetch_hist(symbol: str):
    df = ak.stock_hk_hist(symbol=symbol, period="daily", start_date="20250101", end_date=datetime.now().strftime("%Y%m%d"), adjust="qfq")
    if df is None or df.empty:
        return pd.DataFrame()
    return df.sort_values("日期").reset_index(drop=True)


def calc_metrics(df: pd.DataFrame):
    c = df["收盘"].astype(float)
    h = df["最高"].astype(float)
    l = df["最低"].astype(float)
    v = df["成交量"].astype(float)
    last = float(c.iloc[-1]); prev = float(c.iloc[-2]) if len(c) >= 2 else last
    ma5 = float(c.tail(5).mean()); ma10 = float(c.tail(10).mean()); ma20 = float(c.tail(20).mean()) if len(c) >= 20 else float(c.mean())
    high5 = float(h.tail(5).max()); high10 = float(h.tail(10).max()); high20 = float(h.tail(20).max())
    low5 = float(l.tail(5).min()); low10 = float(l.tail(10).min()); low20 = float(l.tail(20).min())
    ret5 = (last / float(c.iloc[-6]) - 1) * 100 if len(c) >= 6 else 0
    pos60 = (last - float(l.tail(60).min())) / (float(h.tail(60).max()) - float(l.tail(60).min()) + 1e-9)
    vol_ratio = float(v.tail(5).mean()) / (float(v.tail(20).mean()) + 1e-9)
    return {
        "last": round(last, 3), "prev": round(prev, 3), "pct": round((last / prev - 1) * 100, 2) if prev else 0,
        "ma5": round(ma5, 3), "ma10": round(ma10, 3), "ma20": round(ma20, 3),
        "high5": round(high5, 3), "high10": round(high10, 3), "high20": round(high20, 3),
        "low5": round(low5, 3), "low10": round(low10, 3), "low20": round(low20, 3),
        "ret5": round(ret5, 2), "pos60": round(pos60, 2), "vol_ratio": round(vol_ratio, 2),
    }


def score_candidate(m):
    score = 0
    score += max(min(m["pct"], 8), -5) * 0.8
    score += 2 if m["last"] >= m["ma5"] else -1
    score += 2 if m["ma5"] >= m["ma10"] else -1
    score += 1.5 if m["ma10"] >= m["ma20"] else 0
    score += min(max(m["vol_ratio"] - 1, 0), 2) * 2
    score += 1 if m["pos60"] < 0.92 else -1
    return round(score, 2)


def classify_bucket(m, code):
    if code.startswith('07') or code.startswith('03'):
        return '主题/ETF池'
    if m['last'] > 80:
        return '核心大票池'
    if m['vol_ratio'] >= 1.3 and m['ret5'] >= 5:
        return '弹性机会池'
    return '核心观察池'


def position_plan(item, m):
    cost = item['cost']; last = m['last']
    pnl_pct = round((last / cost - 1) * 100, 2)
    pnl_amt = round((last - cost) * item['shares'], 2)
    add_trigger = round(max(m['ma5'], m['high5']), 3)
    reduce_trigger = round(max(m['high10'], cost * 0.95), 3)
    stop_trigger = round(min(m['low5'], m['ma10']), 3)
    fail_trigger = round(min(m['low10'], m['ma20']), 3)

    if last >= m['ma5'] >= m['ma10']:
        action = '偏强，优先持有观察，不急着割；等回踩确认或放量突破再决策'
    elif last < m['ma10']:
        action = '偏弱，反弹减仓优先；未重新站稳前不建议贸然补仓'
    else:
        action = '中性震荡，等突破或跌破关键位后再动作'

    rules = {
        '观望条件': f"价格在 {stop_trigger} ~ {add_trigger} 区间内震荡，且没有明显放量突破，先观望。",
        '加仓条件': f"只有当价格有效站上 {add_trigger}，且最好同时站稳 MA5/短线高点，才考虑小仓位试加。",
        '减仓条件': f"若反弹到 {reduce_trigger} 附近但量能跟不上，优先考虑减仓或降成本。",
        '止弱条件': f"若回落并跌破 {stop_trigger}，说明短线走弱；若进一步跌破 {fail_trigger}，应把防守放在前面。"
    }

    return {
        'code': item['code'], 'name': item['name'], 'last': last, 'cost': cost, 'shares': item['shares'],
        'pnl_pct': pnl_pct, 'pnl_amt': pnl_amt, 'action': action,
        'levels': {
            'add_trigger': add_trigger,
            'reduce_trigger': reduce_trigger,
            'stop_trigger': stop_trigger,
            'fail_trigger': fail_trigger,
            'break_even': round(cost, 3),
        },
        'rules': rules,
        'metrics': m,
    }


def main():
    items = []
    for code, name in CANDIDATES:
        try:
            df = fetch_hist(code)
            if len(df) < 30:
                continue
            m = calc_metrics(df)
            items.append({
                'code': code,
                'name': name,
                'bucket': classify_bucket(m, code),
                'metrics': m,
                'score': score_candidate(m),
            })
        except Exception:
            continue

    items = sorted(items, key=lambda x: x['score'], reverse=True)
    buckets = {}
    for item in items:
        buckets.setdefault(item['bucket'], []).append(item)
    for k in list(buckets):
        buckets[k] = buckets[k][:5]

    watch = []
    for item in WATCHS:
        df = fetch_hist(item['code'])
        m = calc_metrics(df)
        watch.append(position_plan(item, m))

    out = {
        'generated_at': datetime.now().isoformat(),
        'hk_watch_positions': watch,
        'hk_candidate_buckets': buckets,
        'hk_top3_today': items[:3],
        'source': 'AKShare 港股历史行情与公开资料；当前以日线级观察为主，非逐笔实时行情。'
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
