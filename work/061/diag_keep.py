import sys, numpy as np, pandas as pd
from datetime import date, timedelta
sys.path.insert(0, ".")
import ccbot.realtest as rt
cfg = rt.DEFAULT_CFG
tks = ["AAL","BAC","BMY","CMCSA","CSX","F","HBAN","KEY","KMI","MDLZ","MO","OXY","PFE","PYPL","T","USB","VZ"]
data = {t: rt.load_ticker("data/real", t) for t in tks}
orig_pick, orig_known = rt._pick, rt._earnings_known
def run(label, start, floor=True, lookback=None):
    rt._pick = orig_pick if floor else (lambda g, today, rule, c, m, basis: orig_pick(g, today, rule, c, m, 0.0))
    if lookback:
        rt._earnings_known = lambda td, d: orig_known(td, d) and any(d - timedelta(days=lookback) <= e <= d for e in td.earnings) \
            if not any(e <= d for e in td.earnings) or True else True
    else:
        rt._earnings_known = orig_known
    rows, trs = [], []
    for t, td in data.items():
        df, tr = rt.simulate(td, rt.BOT_RULE, cfg, start=start)
        s = rt.summarize(td, rt.BOT_RULE, df, tr, cfg); rows.append(s)
        trs += [(x.iv - x.rv_life, x.pnl / x.spot) for x in tr]
    b = pd.DataFrame(rows); g = np.array(trs) if trs else np.zeros((0, 2))
    a4c = (b.cc_cagr / b.cc_maxdd.abs()).median(); a4h = (b.bh_cagr / b.bh_maxdd.abs()).median()
    print(f"{label:38s} calls {len(g):4d} IV>RV {np.mean(g[:,0]>0)*100:4.1f}% meanPnL {np.mean(g[:,1])*100:+.3f}% "
          f"medGap {b.excess_cagr.median()*100:+.2f} A2 {(b.excess_cagr>=-0.01).sum():2d}/17 A3 {(b.cc_maxdd>=b.bh_maxdd).sum():2d}/17 "
          f"A4 {a4c:.3f} vs {a4h:.3f} T/VZ/AAL {dict(zip(b.ticker,b.calls_sold))['T']}/{dict(zip(b.ticker,b.calls_sold))['VZ']}/{dict(zip(b.ticker,b.calls_sold))['AAL']}", flush=True)
    return b
mode = sys.argv[1]
if mode == "start":
    for st in (date(2020,1,1), date(2020,4,1), date(2021,1,4), date(2022,1,3)):
        run(f"start {st} floor on", st, True); run(f"start {st} floor off", st, False)
else:
    run("as built (start 2020-01-01)", date(2020,1,1))
    b = run("earnings lookback 120d block", date(2020,1,1), lookback=120)
    print(b[["ticker","calls_sold","excess_cagr","rej_EARNINGS_UNKNOWN"]].to_string())
