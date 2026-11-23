#!/usr/bin/env python3
"""Vote analyzer: python app.py  ->  http://127.0.0.1:8765   (standard library only)
Low-impact by design: low CPU priority, streamed upload/parse (no whole-file RAM load),
votes pre-aggregated into a small pair-count table, short sleeps inside the heavy loops."""
import csv, json, math, os, sys, tempfile, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
try: os.nice(15)                                   # Linux / macOS
except Exception:
    try:                                             # Windows: below-normal priority so the PC stays responsive
        import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception: pass
HERE = os.path.dirname(os.path.abspath(__file__))
S = {"agg": {}, "rows": 0, "dupes": 0, "bad": 0}

def ingest(path):
    agg, seen, rows, dupes, bad = {}, set(), 0, 0, 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        r.fieldnames = [h.strip().lower() for h in r.fieldnames or []]
        for n, row in enumerate(r):
            w, l = (row.get("winner") or "").strip(), (row.get("loser") or "").strip()
            if not w or not l or w == l: bad += 1; continue
            vid = (row.get("vote_id") or "").strip()
            if vid:
                h = hash(vid)
                if h in seen: dupes += 1; continue
                seen.add(h)
            k = ((row.get("page") or "").strip(), (row.get("country") or "").strip(), w, l)
            agg[k] = agg.get(k, 0) + 1; rows += 1
            if n % 20000 == 0: time.sleep(0.01)
    S.update(agg=agg, rows=rows, dupes=dupes, bad=bad)

def bradley_terry(names, W, prior=0.5, iters=1000, tol=1e-10):
    """MM algorithm (Hunter 2004) on the win-count matrix only, so vote order cannot matter.
    `prior` = pseudo-wins each way per pair: keeps 0-win / unbeaten characters finite."""
    n = len(names); ix = {c: i for i, c in enumerate(names)}
    w = [[0 if i == j else prior for j in range(n)] for i in range(n)]
    for (a, b), c in W.items(): w[ix[a]][ix[b]] += c
    tot = [sum(r) for r in w]; p = [1.0] * n; it = 0
    for it in range(1, iters + 1):
        new = [tot[i] / sum((w[i][j] + w[j][i]) / (p[i] + p[j]) for j in range(n) if j != i) for i in range(n)]
        g = math.exp(sum(map(math.log, new)) / n); new = [x / g for x in new]
        d = max(abs(math.log(a / b)) for a, b in zip(new, p)); p = new
        if d < tol: break
        time.sleep(0.0005)
    k = 400 / math.log(10)
    ci = []
    for i in range(n):
        info = sum((w[i][j] + w[j][i]) * p[i] * p[j] / (p[i] + p[j]) ** 2 for j in range(n) if j != i)
        ci.append(1.96 * k / math.sqrt(info))
    return [1500 + k * math.log(x) for x in p], ci, it

def analyze(page, country):
    W = {}
    for (pg, co, a, b), c in S["agg"].items():
        if (page and pg != page) or (country and co != country): continue
        W[(a, b)] = W.get((a, b), 0) + c
    names = sorted({x for k in W for x in k})
    if not names: return {"names": []}
    ix = {c: i for i, c in enumerate(names)}
    M = [[0] * len(names) for _ in names]
    for (a, b), c in W.items(): M[ix[a]][ix[b]] = c
    rating, ci, it = bradley_terry(names, W)
    return {"names": names, "rating": rating, "ci": ci, "iters": it, "matrix": M, "votes": sum(W.values())}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, obj, code=200, ctype="application/json"):
        b = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urlparse(self.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path == "/api/meta":
            ks = S["agg"].keys()
            return self.send({"rows": S["rows"], "dupes": S["dupes"], "bad": S["bad"],
                              "pages": sorted({k[0] for k in ks if k[0]}), "countries": sorted({k[1] for k in ks if k[1]})})
        if u.path == "/api/analyze": return self.send(analyze(q.get("page", ""), q.get("country", "")))
        with open(os.path.join(HERE, "index.html"), "rb") as f: self.send(f.read(), ctype="text/html; charset=utf-8")
    def do_POST(self):
        left = int(self.headers.get("Content-Length", 0))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as t:
            while left > 0:
                chunk = self.rfile.read(min(1 << 20, left)); left -= len(chunk); t.write(chunk)
        try: ingest(t.name); self.send({"ok": True})
        except Exception as e: self.send({"ok": False, "error": str(e)}, 400)
        finally: os.unlink(t.name)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"Vote Analyzer running at http://localhost:{port}  (close this window to stop)")
    HTTPServer(("127.0.0.1", port), H).serve_forever()
