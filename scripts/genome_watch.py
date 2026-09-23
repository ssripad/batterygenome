#!/usr/bin/env python3
"""Genome Watch: monthly agent for batterygenome.net.
1) Extracts every supplier from index.html (segment top-5s, domain 10-lists, family 10-lists).
2) Asks Claude (with web search) to flag bankruptcies, insolvency processes, acquisitions, renames.
3) Asks Claude to check the market anchors (BNEF/IEA benchmarks + biggest segments) for >20% drift.
4) Files or updates a GitHub issue labeled 'genome-watch' with the findings. Flags only - a human merges.
Requires env: ANTHROPIC_API_KEY, GITHUB_TOKEN, GITHUB_REPOSITORY.
"""
import json, os, re, sys, time
import urllib.request

try:
    import anthropic
except ImportError:
    sys.exit("pip install anthropic")

MODEL = "claude-sonnet-4-6"
API = anthropic.Anthropic()

def gh(path, payload=None, method="GET"):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=json.dumps(payload).encode() if payload else None, method=method,
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read() or "{}")

def ask(prompt, max_searches=8):
    for attempt in range(3):
        try:
            msg = API.messages.create(
                model=MODEL, max_tokens=3000,
                tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": max_searches}],
                messages=[{"role": "user", "content": prompt}])
            text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
            m = re.search(r"\[[\s\S]*\]", text)
            return json.loads(m.group(0)) if m else []
        except Exception as e:
            print("retry", attempt, e); time.sleep(20)
    return []

def main():
    html = open("index.html", encoding="utf-8").read()
    meta = json.loads(re.search(r'<script type="application/json" id="big-meta">(.*?)</script>', html, re.S).group(1))
    doms = [json.loads(m) for m in re.findall(r'<script type="application/json" class="big-domain">(.*?)</script>', html, re.S)]

    companies = {}
    for d in doms:
        for name, cc in d.get("v10", []): companies.setdefault(name, set()).add(d["id"] + " list")
        for a in d["apps"]:
            for name, cc in a.get("v", []): companies.setdefault(name, set()).add(a["id"])
    for fam, lst in meta.get("family_vendors", {}).items():
        for name, cc in lst: companies.setdefault(name, set()).add("family:" + fam)
    names = sorted(companies)
    print(f"{len(names)} unique companies")

    vendor_flags = []
    CHUNK = 22
    for i in range(0, len(names), CHUNK):
        batch = names[i:i+CHUNK]
        prompt = (
            "You maintain a battery-industry supplier index. For each company below, search for news from the last "
            "18 months of: bankruptcy / chapter 11 / insolvency or restructuring process, ceasing battery operations, "
            "acquisition, or a rename. Battery-industry context only. Respond with ONLY a JSON array; include an entry "
            "ONLY for companies with a confirmed, sourced event: "
            '[{"name":"<exact name from list>","event":"bankruptcy|insolvency_process|ceased|acquired|renamed",'
            '"detail":"one line","source":"url","date":"YYYY-MM"}]\n'
            "If none in this batch, return []. Companies: " + "; ".join(batch))
        vendor_flags += ask(prompt)
        time.sleep(3)

    anchors = []
    big = sorted((a for d in doms for a in d["apps"]), key=lambda a: -a["m"])[:12]
    for a in big:
        anchors.append({"id": a["id"], "name": a["n"], "usd_b": a["m"], "gwh": a.get("gwh")})
    mkt_prompt = (
        "You audit a 2025 pack-level battery market map. Benchmarks used: BNEF 2025 pack avg $108/kWh, BEV $99, "
        "stationary $70, 2/3-wheeler $133; IEA 2025 EV deployment ~1.2 TWh. Search for the CURRENT successor figures "
        "(latest BNEF price survey, IEA outlook) and for major 2026 revisions to these segments: "
        + json.dumps(anchors) +
        ". Respond with ONLY a JSON array of material findings (>20% implied change or a benchmark update): "
        '[{"scope":"benchmark|segment","id":"...","finding":"one line with numbers","source":"url"}] or [].')
    market_flags = ask(mkt_prompt, max_searches=10)

    if not vendor_flags and not market_flags:
        print("all clear - no issue filed"); return

    lines = [f"Automated monthly watch over `index.html` ({meta.get('version','?')}). Flags only; verify before editing.\n"]
    if vendor_flags:
        lines.append("## Supplier flags")
        for f in vendor_flags:
            segs = ", ".join(sorted(companies.get(f.get("name",""), []))) or "?"
            lines.append(f"- **{f.get('name')}** - {f.get('event')} ({f.get('date','?')}): {f.get('detail','')} "
                         f"[source]({f.get('source','')}) · appears in: {segs}")
    if market_flags:
        lines.append("\n## Market anchor flags")
        for f in market_flags:
            lines.append(f"- `{f.get('id','-')}` ({f.get('scope')}): {f.get('finding')} [source]({f.get('source','')})")
    body = "\n".join(lines)

    repo = os.environ["GITHUB_REPOSITORY"]
    issues = gh(f"/repos/{repo}/issues?labels=genome-watch&state=open")
    title = f"Genome watch: {time.strftime('%Y-%m')} - {len(vendor_flags)} supplier / {len(market_flags)} market flags"
    if issues:
        gh(f"/repos/{repo}/issues/{issues[0]['number']}/comments", {"body": f"### {title}\n\n{body}"}, "POST")
        print("commented on existing issue", issues[0]["number"])
    else:
        gh(f"/repos/{repo}/issues", {"title": title, "body": body, "labels": ["genome-watch"]}, "POST")
        print("issue filed")

if __name__ == "__main__":
    main()
