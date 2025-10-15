import json, feedparser, datetime, hashlib, requests

print("【脚本开始】")

HF_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HF_HEADERS = {"Authorization": "Bearer hf_PublicDemoDoNotRateLimit"}

def shorten(text: str) -> str:
    print("【进入 shorten】", text)
    if len(text) <= 25:
        return text
    try:
        payload = {"inputs": text, "parameters": {"max_length": 20, "min_length": 8}}
        r = requests.post(HF_URL, headers=HF_HEADERS, json=payload, timeout=15)
        r.raise_for_status()
        out = r.json()[0]["summary_text"]
        print("【LLM 返回】", out)
        return out
    except Exception as e:
        print("【LLM 失败】", e)
        return text[:22] + "…"

KEYWORDS = ["中美", "关税", "trade war", "Trump", "Biden", "China US", "tariff"]
FEEDS = [
    "https://news.google.com/rss/search?q=china+tariff+site:ustr.gov+OR+site:mofcom.gov.cn+before:2025-06-01+after:2018-01-01&ceid=US:en&hl=en-US&gl=US",
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
    seen = set()
    for url in FEEDS:
        feed = feedparser.parse(url)
        print("【抓取】", url, "条目数", len(feed.entries))
        for entry in feed.entries:
            title = entry.title
            if not any(k in title for k in KEYWORDS):
                continue
            pub = entry.published_parsed
            date = datetime.date(pub[0], pub[1], pub[2]).strftime("%Y-%m-%d")
            short_title = shorten(title)
            key = f"{date}|{short_title}"
            if key in seen:
                continue
            seen.add(key)
            nodes.append({
                "date": date,
                "title": short_title,
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
    merged = {(n["date"], n["title"]): n for n in old + new}.values()
    merged = sorted(merged, key=lambda x: x["date"])
    json.dump(merged, open("event.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

if __name__ == "__main__":
    merge()
    # 调试：看看抓到了多少条
        try:
            with open("event.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"✅ 当前 event.json 共有 {len(data)} 条节点")
            for n in data[-3:]:  # 显示最后 3 条
                print(f"- {n['date']} | {n['title']}")
        except FileNotFoundError:
            print("❌ event.json 不存在，可能是没抓到任何节点")
