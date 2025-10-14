import json, feedparser, os, datetime, openai
openai.api_key = os.getenv("OPENAI_API_KEY")

KEYWORDS = ["中美贸易战", "中美关税", "Trump tariff", "Biden tariff"]
FEEDS = [
    "https://rsshub.app/baidu/top",
    "https://rsshub.app/zhihu/hot",
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"
]

def fetch_nodes():
    nodes = []
    for url in FEEDS:
        for entry in feedparser.parse(url).entries:
            text = entry.title + " " + (entry.summary or "")
            if not any(k in text for k in KEYWORDS):
                continue
            prompt = f"""
            请判断以下文本是否关于“中美贸易战”的**新进展**：
            文本：{text}
            如果相关，返回 JSON：
            {{"date":"{datetime.date.today().strftime('%Y-%m-%d')}","title":"一句话标题","type":"red|blue|gray","source":"{entry.link}"}}
            不相关返回 null
            """
            res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role":"user","content":prompt}])
            try:
                node = json.loads(res.choices[0].message.content)
                if node:
                    nodes.append(node)
            except:
                continue
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
