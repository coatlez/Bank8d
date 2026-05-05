#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
银行股数据抓取脚本
每天自动抓取42家银行的实时行情，生成 data.json
由 GitHub Actions 定时执行
"""

import requests
import json
import time
from datetime import datetime

# 42家银行股票代码
BANKS = [
    ("工商银行", "601398"), ("农业银行", "601288"), ("建设银行", "601939"),
    ("中国银行", "601988"), ("邮储银行", "601658"), ("交通银行", "601328"),
    ("招商银行", "600036"), ("兴业银行", "601166"), ("中信银行", "601998"),
    ("浦发银行", "600000"), ("光大银行", "601818"), ("平安银行", "000001"),
    ("华夏银行", "600015"), ("民生银行", "600016"), ("浙商银行", "601916"),
    ("北京银行", "601169"), ("上海银行", "601229"), ("江苏银行", "600919"),
    ("宁波银行", "002142"), ("南京银行", "601009"), ("杭州银行", "600926"),
    ("成都银行", "601838"), ("苏州银行", "601860"), ("长沙银行", "601577"),
    ("贵阳银行", "601997"), ("齐鲁银行", "601665"), ("青岛银行", "002948"),
    ("重庆银行", "601963"), ("西安银行", "600928"), ("厦门银行", "601187"),
    ("兰州银行", "001227"), ("郑州银行", "002936"), ("沪农商行", "601825"),
    ("渝农商行", "601077"), ("青农商行", "002958"), ("紫金银行", "601860"),
    ("江阴银行", "002807"), ("张家港行", "002839"), ("瑞丰银行", "601528"),
    ("无锡银行", "600908"), ("苏农银行", "603323"), ("常熟银行", "601128"),
]

def fetch_quotes():
    """通过新浪财经接口抓取行情"""
    code_str = ",".join(
        ("sh" if c.startswith("6") else "sz") + c
        for _, c in BANKS
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://finance.sina.com.cn",
    }
    try:
        url = f"https://hq.sinajs.cn/list={code_str}"
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = "gbk"
        return r.text
    except Exception as e:
        print(f"新浪接口失败: {e}")
        return ""

def parse_quotes(text):
    """解析新浪行情数据"""
    result = {}
    for line in text.strip().split("\n"):
        import re
        m = re.match(r'var hq_str_([a-z]{2})(\d{6})="([^"]*)"', line)
        if not m:
            continue
        code = m.group(2)
        fields = m.group(3).split(",")
        if len(fields) < 10 or not fields[0]:
            continue
        try:
            price = float(fields[3])
            prev_close = float(fields[2])
            if price > 0 and prev_close > 0:
                chg_pct = round((price - prev_close) / prev_close * 100, 2)
                chg_amt = round(price - prev_close, 3)
                result[code] = {
                    "price": price,
                    "chg": chg_pct,
                    "chgA": chg_amt,
                    "high": float(fields[4]),
                    "low": float(fields[5]),
                    "vol": int(fields[8]) if fields[8] else 0,
                }
        except (ValueError, IndexError):
            continue
    return result

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始抓取行情...")

    # 抓行情
    raw = fetch_quotes()
    quotes = parse_quotes(raw)
    print(f"成功获取 {len(quotes)} 家银行行情")

    # 生成输出数据
    output = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_ts": int(time.time()),
        "quotes": quotes,
    }

    # 写入 data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"data.json 已生成，包含 {len(quotes)} 条行情")

if __name__ == "__main__":
    main()
