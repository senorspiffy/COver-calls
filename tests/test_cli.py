from ccbot.__main__ import main
from conftest import SAMPLE


def test_backtest_quick(tmp_path):
    assert main(["backtest", "--quick", "--asof", "2026-10-30", "--out", str(tmp_path)]) == 0
    assert (tmp_path / "backtest_SYNTH_A_2026-10-30.md").exists()
    assert (tmp_path / "backtest_SYNTH_A_2026-10-30.csv").exists()


def test_scan_and_report(tmp_path):
    args = ["--date", "2026-10-30", "--state-dir", str(tmp_path / "s"), "--out", str(tmp_path / "r")]
    assert main(["scan", "--broker", "sim", "--snapshots", str(SAMPLE / "SYNTH_SNAPSHOTS.csv"), *args]) == 0
    assert (tmp_path / "r" / "daily_2026-10-30.md").exists() and (tmp_path / "r" / "weekly_2026-10-30.md").exists()
    (tmp_path / "r" / "daily_2026-10-30.md").unlink()
    assert main(["report", *args]) == 0 and (tmp_path / "r" / "daily_2026-10-30.md").exists()
    assert main(["report", "--date", "2026-10-29", "--state-dir", str(tmp_path / "s")]) == 2


def test_live_refused(tmp_path, capsys):
    assert main(["scan", "--date", "2026-10-30", "--live", "--state-dir", str(tmp_path)]) == 3
    assert "Live trading is not built" in capsys.readouterr().err


def test_webull_without_env_refused(tmp_path, monkeypatch, capsys):
    for k in ("WEBULL_ENV", "WEBULL_APP_KEY", "WEBULL_APP_SECRET"):
        monkeypatch.delenv(k, raising=False)
    assert main(["scan", "--date", "2026-10-30", "--broker", "webull-sandbox", "--state-dir", str(tmp_path)]) == 3
    assert "WEBULL_ENV must be 'sandbox'" in capsys.readouterr().err


def test_bad_data_path(tmp_path):
    assert main(["backtest", "--quick", "--data", str(tmp_path / "missing.csv"), "--out", str(tmp_path)]) == 2


def test_short_csv_reports_pbo_na_without_warnings(tmp_path, recwarn):
    """Regression guardrail (002, I3 re-verification): a 1-year CSV (every year held out)
    must print PBO as n/a with its reason, never 0.000, and raise no numpy RuntimeWarning."""
    import datetime as dt
    import warnings
    d, rows = dt.date(2025, 1, 2), []
    while d.year == 2025:
        if d.weekday() < 5:
            rows.append(f"{d},{24 + 0.3 * (-1) ** len(rows):.2f}")
        d += dt.timedelta(days=1)
    p = tmp_path / "SHORT.csv"
    p.write_text("date,close\n" + "\n".join(rows) + "\n")
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        assert main(["backtest", "--data", str(p), "--quick", "--asof", "2026-10-30", "--out", str(tmp_path)]) == 0
    md = (tmp_path / "backtest_SHORT_2026-10-30.md").read_text()
    pbo = next(line for line in md.splitlines() if line.startswith("- PBO"))
    assert "n/a (needs >= 8 non-held-out months" in pbo and "0.000" not in pbo
    assert "not selected (no train years)" in md
    assert not [w for w in recwarn if issubclass(w.category, RuntimeWarning)]
