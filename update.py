import json, feedparser, datetime, hashlib

# 1. 关键词池
KEYWORDS = ["中美", "关税", "trade war", "Trump", "Biden", "China US", "tariff"]

# 2. 数据源
FEEDS = [
    # 官方 2018-2025 骨架
    "https://news.google.com/rss/search?q=china+tariff+site:ustr.gov+OR+site:mofcom.gov.cn+before:2025-06-01+after:2018-01-01&ceid=US:en&hl=en-US&gl=US",
    # 当天增量
    "https://news.google.com/rss/search?q=china+tariff+site:ustr.gov+OR+site:mofcom.gov.cn&ceid=US:en&hl=en-US&gl=US"
]

def color_of(title):
    if any(w in title for w in ["加征", "制裁", "提高", "上调", "惩罚"]):
        return "red"
    if any(w in title for w in ["谈判", "缓和", "取消", "暂停", "协商"]):
        return "blue"
    return "gray"

def fetch_nodes():
    nodes = []
    # ① 不再需要 today
    seen = set()
    for url in FEEDS:
        for entry in feedparser.parse(url).entries:
            title = entry.title
            if not any(k in title for k in KEYWORDS):
                continue

            # ② 用 RSS 原文发布日期
            pub = entry.published_parsed          # struct_time
            date = datetime.date(pub[0], pub[1], pub[2]).strftime("%Y-%m-%d")

            # ③ 去重键改成「原文日期+标题」
            key = f"{date}|{title}"
            if key in seen:
                continue
            seen.add(key)

            nodes.append({
                "date": date,                     # 原文日期
                "title": title,
                "type": color_of(title),
                "source": entry.link
            })
    return nodes

def merge():
    try:
        old = json.load(open("event.json"))
    except:
        old = []
    new = fetch_nodes()
    # 合并+去重
    merged = {(n["date"], n["title"]): n for n in old + new}.values()
    merged = sorted(merged, key=lambda x: x["date"])
    json.dump(merged, open("event.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

if __name__ == "__main__":
    merge()
