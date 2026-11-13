"""애프터플레이 일일 문화예술 이슈 수집기 (표준 라이브러리만 사용)."""
import os, json, html, datetime, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

CATS = {
    "음악": ["콘서트 공연 음악", "가요 앨범 컴백"],
    "미술·전시": ["전시 미술관", "아트페어 미술"],
    "영화·공연": ["영화 개봉", "뮤지컬 연극 공연"],
    "문화 이슈": ["문화예술 화제"],
}
PER_CAT = 8


def fetch(q):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": q + " when:1d", "hl": "ko", "gl": "KR", "ceid": "KR:ko"})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")


def parse(xml_text):
    out = []
    for it in ET.fromstring(xml_text).iter("item"):
        s = it.find("source")
        out.append({
            "title": (it.findtext("title") or "").strip(),
            "link": (it.findtext("link") or "").strip(),
            "source": (s.text if s is not None and s.text else ""),
        })
    return out


def collect():
    data = {}
    for cat, queries in CATS.items():
        seen, items = set(), []
        for q in queries:
            try:
                for it in parse(fetch(q)):
                    if it["title"] and it["title"] not in seen:
                        seen.add(it["title"])
                        items.append(it)
            except Exception as e:
                print("수집 실패:", cat, q, e)
        data[cat] = items[:PER_CAT]
    return data


def ai_brief(cat, items):
    """ANTHROPIC_API_KEY가 있을 때만 카드뉴스 아이디어·후킹 제목·캡션을 작성."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key or not items:
        return ""
    heads = "\n".join("- " + i["title"] for i in items)
    prompt = (f"문화예술 뉴스 인스타 계정 '애프터플레이' 편집팀({cat})입니다. 오늘 헤드라인:\n{heads}\n\n"
              "1) 카드뉴스로 만들 만한 주제 2개와 장별 구성\n2) 릴스 후킹 제목 3개\n3) 캡션 1개(해시태그 포함)\n"
              "한국어로 간결하게. 헤드라인에 없는 사실은 지어내지 마세요.")
    body = json.dumps({"model": "claude-sonnet-5-5", "max_tokens": 900,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers={
        "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return "".join(b.get("text", "") for b in json.load(r)["content"])
    except Exception as e:
        print("AI 작성 실패:", cat, e)
        return ""


def render(data, briefs, today):
    e = html.escape
    parts = []
    for cat, items in data.items():
        lis = "".join(f'<li><a href="{e(i["link"])}">{e(i["title"])}</a></li>' for i in items) or "<li>수집된 소식이 없어요</li>"
        b = f'<div class="b">{e(briefs[cat])}</div>' if briefs.get(cat) else ""
        parts.append(f"<section><h2>{e(cat)}</h2><ul>{lis}</ul>{b}</section>")
    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>애프터플레이 오늘의 이슈</title>
<style>body{{font-family:system-ui,sans-serif;max-width:720px;margin:0 auto;padding:20px;line-height:1.6;color:#161616}}
h1{{font-size:24px}}h2{{font-size:17px;margin-top:28px}}li{{margin-bottom:6px}}a{{color:#2f4bff}}
.b{{background:#f3f3ef;border-radius:8px;padding:12px;white-space:pre-wrap;font-size:14px}}
@media(prefers-color-scheme:dark){{body{{background:#121212;color:#f1f1ec}}.b{{background:#1d1d1b}}a{{color:#8ea0ff}}}}</style></head>
<body><h1>애프터플레이 오늘의 이슈</h1><p>{today} 수집 · 제목과 링크만 모았어요. 기사 원문은 링크에서 확인하세요.</p>{''.join(parts)}</body></html>"""


if __name__ == "__main__":
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
    data = collect()
    briefs = {c: ai_brief(c, it) for c, it in data.items()}
    os.makedirs("docs", exist_ok=True)
    with open("docs/data.json", "w", encoding="utf-8") as f:
        json.dump({"date": today, "items": data, "briefs": briefs}, f, ensure_ascii=False, indent=1)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(render(data, briefs, today))
    print("완료:", {c: len(v) for c, v in data.items()})
