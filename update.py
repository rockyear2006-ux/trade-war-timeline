import json, feedparser, datetime, hashlib

# 1. 关键词池
KEYWORDS = ["中美贸易战", "中美关税", "特朗普 关税", "拜登 关税",
            "加征关税", "取消关税", "贸易谈判", "贸易缓和"]

# 2. 数据源
FEEDS = [
    "https://rsshub.app/baidu/top",
    "https://rsshub.app/zhihu/hot",
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "https://feeds.reuters.com/reuters/businessNews"
]

def color_of(title):
    if any(w in title for w in ["加征", "制裁", "提高", "上调", "惩罚"]):
        return "red"
    if any(w in title for w in ["谈判", "缓和", "取消", "暂停", "协商"]):
        return "blue"
    return "gray"

def fetch_nodes():
    nodes = []
    today = datetime.date.today().strftime("%Y-%m-%d")
    seen = set()
    for url in FEEDS:
        for entry in feedparser.parse(url).entries:
            title = entry.title
            if not any(k in title for k in KEYWORDS):
                continue
            # 简单去重：同一天同一标题
            key = f"{today}|{title}"
            if key in seen:
                continue
            seen.add(key)
            nodes.append({
                "date": today,
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
