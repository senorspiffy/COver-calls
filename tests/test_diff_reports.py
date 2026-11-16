"""scripts/diff_reports.py: whole-output diff of two realtest report dirs (item 067, RI-013)."""
import json
import subprocess
import sys

from conftest import REPO

SCRIPT = REPO / "scripts" / "diff_reports.py"


def _run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)


def _dirs(tmp_path, before, after):
    """before/after: {name: text or obj}. A dict/list value is written as JSON."""
    out = []
    for side, files in (("before", before), ("after", after)):
        d = tmp_path / side
        d.mkdir()
        for name, body in files.items():
            if not isinstance(body, str):
                body = json.dumps(body, indent=1)
            (d / name).write_text(body, encoding="utf-8")
        out.append(d)
    return out


def _picks(picked1):
    return [{"test_from": "2022-01-06", "picked": "x"}, {"test_from": "2022-07-06", "picked": picked1}]


def test_a_nested_key_and_list_in_dict(tmp_path):
    b, a = _dirs(tmp_path,
                 {"summary.json": {"monte_carlo_2_stocks_1yr": {"cc_ret": {"50": 0.0689}},
                                   "walkforward_picks": _picks("d0.150_roll")}},
                 {"summary.json": {"monte_carlo_2_stocks_1yr": {"cc_ret": {"50": 0.0686}},
                                   "walkforward_picks": _picks("d0.450_take50")}})
    r = _run(b, a)
    assert r.returncode == 1, r.stderr
    lines = r.stdout.splitlines()
    assert "monte_carlo_2_stocks_1yr.cc_ret.50: 0.0689 -> 0.0686" in lines
    assert "walkforward_picks[1].picked: 'd0.150_roll' -> 'd0.450_take50'" in lines
    assert "json changes 2" in lines[-1]


def test_b_identical_with_nan_and_empty_cells(tmp_path):
    js = '{"walkforward_picks": [{"train_excess_logret": NaN}], "x": 1}'
    csv_text = "ticker,excess_cagr\nAAL,\nBAC,0.1\n"
    b, a = _dirs(tmp_path, {"summary.json": js, "walkforward_by_ticker.csv": csv_text},
                 {"summary.json": js, "walkforward_by_ticker.csv": csv_text})
    r = _run(b, a)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "NaN tokens: before 1, after 1" in r.stdout
    assert r.stdout.splitlines()[-1] == "no change"


def test_c_type_changes(tmp_path):
    b, a = _dirs(tmp_path, {"summary.json": {"i": 1, "b": True, "n": None}},
                 {"summary.json": {"i": 1.0, "b": 1, "n": 0}})
    r = _run(b, a)
    assert r.returncode == 1
    lines = r.stdout.splitlines()
    assert "TYPE i: int 1 -> float 1.0" in lines
    assert "TYPE b: bool True -> int 1" in lines
    assert "TYPE n: NoneType None -> int 0" in lines


def test_d_file_only_in_after(tmp_path):
    b, a = _dirs(tmp_path, {"summary.json": {}},
                 {"summary.json": {}, "trades_XYZ.csv": "open_date,pnl\n2024-01-02,1\n2024-02-02,2\n"})
    r = _run(b, a)
    assert r.returncode == 1
    assert "ONLY IN AFTER: trades_XYZ.csv (2 rows)" in r.stdout.splitlines()
    assert "only-after 1" in r.stdout


def test_e_added_ticker_matched_by_key(tmp_path):
    h = "ticker,excess_cagr\n"
    b, a = _dirs(tmp_path, {"walkforward_by_ticker.csv": h + "AAL,1\nBAC,2\nCSX,3\n"},
                 {"walkforward_by_ticker.csv": h + "AAL,1\nABC,9\nBAC,2\nCSX,3\n"})
    r = _run(b, a)
    assert r.returncode == 1
    assert ("CSV walkforward_by_ticker.csv: match key, rows 3 -> 4, matched 3, added 1, removed 0, "
            "changed 0; by column: none") in r.stdout.splitlines()
    assert "  ADDED ABC" in r.stdout.splitlines()


def _grid(n, val):
    return "ticker,config,cagr\n" + "".join(f"T{i:02d},c,{val}\n" for i in range(n))


def test_f_row_cap(tmp_path):
    b, a = _dirs(tmp_path, {"grid_in_sample.csv": _grid(25, "0.1")}, {"grid_in_sample.csv": _grid(25, "0.2")})
    r = _run(b, a)
    rows = [ln for ln in r.stdout.splitlines() if ln.startswith("  (T")]
    assert len(rows) == 20
    assert "  ... 5 more" in r.stdout.splitlines()
    assert "changed 25; by column: cagr=25" in r.stdout
    r0 = _run(b, a, "--max-rows", "0")
    rows0 = [ln for ln in r0.stdout.splitlines() if ln.startswith("  (T")]
    assert len(rows0) == 25
    assert "more" not in r0.stdout


def test_g_duplicate_key_exits_2(tmp_path):
    t = "open_date,pnl\n2024-01-02,1\n2024-01-02,2\n"
    b, a = _dirs(tmp_path, {"trades_AAL.csv": t}, {"trades_AAL.csv": t})
    r = _run(b, a)
    assert r.returncode == 2
    assert "DUPLICATE KEY trades_AAL.csv: 2024-01-02 (2 rows)" in r.stderr
    assert r.stdout == ""


def test_h_column_added(tmp_path):
    b, a = _dirs(tmp_path, {"trades_AAL.csv": "open_date,pnl\n2024-01-02,1\n"},
                 {"trades_AAL.csv": "open_date,pnl,fee\n2024-01-02,1,0.65\n"})
    r = _run(b, a)
    assert r.returncode == 1
    assert "COLUMNS trades_AAL.csv: added ['fee'] removed []" in r.stdout.splitlines()
    assert "columns changed 1" in r.stdout


def test_i_missing_and_empty_dir(tmp_path):
    good = tmp_path / "good"
    good.mkdir()
    (good / "summary.json").write_text("{}", encoding="utf-8")
    r = _run(tmp_path / "nope", good)
    assert r.returncode == 2
    assert "MISSING DIR:" in r.stderr and r.stdout == ""
    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / "run.log").write_text("Traceback\n", encoding="utf-8")
    r = _run(good, empty)
    assert r.returncode == 2
    assert "EMPTY DIR:" in r.stderr and r.stdout == ""


def test_j_list_length(tmp_path):
    b, a = _dirs(tmp_path, {"summary.json": {"w": list(range(10))}}, {"summary.json": {"w": list(range(9))}})
    r = _run(b, a)
    assert r.returncode == 1
    assert "LENGTH w: 10 -> 9" in r.stdout.splitlines()
    assert "REMOVED w[9] = 9" in r.stdout.splitlines()


def test_k_no_tolerance_on_csv_cells(tmp_path):
    h = "ticker,excess_cagr\n"
    b, a = _dirs(tmp_path, {"walkforward_by_ticker.csv": h + "AAL,0.0689\n"},
                 {"walkforward_by_ticker.csv": h + "AAL,0.0686\n"})
    r = _run(b, a)
    assert r.returncode == 1
    assert "changed 1; by column: excess_cagr=1" in r.stdout
    assert "  AAL: excess_cagr: '0.0689' -> '0.0686'" in r.stdout.splitlines()


def test_l_zero_trade_files(tmp_path):
    # '\n' is what `pd.DataFrame([]).to_csv(index=False)` printed (measured, work/067/05).
    b, a = _dirs(tmp_path, {"trades_ZZZ.csv": "", "trades_YYY.csv": "\n"},
                 {"trades_ZZZ.csv": "", "trades_YYY.csv": "\n"})
    r = _run(b, a)
    assert r.returncode == 0, r.stdout + r.stderr
    lines = r.stdout.splitlines()
    for f in ("trades_YYY.csv", "trades_ZZZ.csv"):
        assert f"MATCH {f}: index (columns [] in before)" in lines
        assert any(ln.startswith(f"CSV {f}: match index, rows 0 -> 0") for ln in lines)
    assert lines[-1] == "no change"


def test_m_bad_json(tmp_path):
    b, a = _dirs(tmp_path, {"summary.json": "{\"a\": "}, {"summary.json": "{}"})
    r = _run(b, a)
    assert r.returncode == 2
    assert r.stderr.startswith("BAD JSON summary.json:")
    assert r.stdout == ""


def test_n_key_column_one_side(tmp_path):
    b, a = _dirs(tmp_path, {"walkforward_by_ticker.csv": "name,excess_cagr\nAAL,1\n"},
                 {"walkforward_by_ticker.csv": "ticker,name,excess_cagr\nAAL,AAL,1\n"})
    r = _run(b, a)
    assert r.returncode == 1
    lines = r.stdout.splitlines()
    assert "COLUMNS walkforward_by_ticker.csv: added ['ticker'] removed []" in lines
    assert "MATCH walkforward_by_ticker.csv: index (key column ticker missing in before)" in lines


def test_o_ragged_row(tmp_path):
    b, a = _dirs(tmp_path, {"trades_AAL.csv": "open_date,pnl\n2024-01-02,1,9\n"},
                 {"trades_AAL.csv": "open_date,pnl\n2024-01-02,1\n"})
    r = _run(b, a)
    assert r.returncode == 2
    assert r.stderr.startswith("BAD ROW trades_AAL.csv line 2")


def test_committed_reports_self_diff():
    real = REPO / "reports" / "real"
    r = _run(real, real)
    assert r.returncode == 0, r.stdout + r.stderr
    lines = r.stdout.splitlines()
    assert lines[-1] == "no change"
    csv_names = sorted(p.name for p in real.glob("*.csv"))
    assert "grid_in_sample.csv" in csv_names and any(n.startswith("trades_") for n in csv_names)
    for n in csv_names:
        if n in ("walkforward_picks.csv", "walkforward_by_ticker.csv", "bot_rule_by_ticker.csv",
                 "grid_in_sample.csv") or n.startswith("trades_"):
            assert any(ln.startswith(f"CSV {n}: match key,") for ln in lines), n


def test_diff_dirs_importable(tmp_path):
    sys.path.insert(0, str(REPO / "scripts"))
    import diff_reports
    b, a = _dirs(tmp_path, {"summary.json": {"x": 1}}, {"summary.json": {"x": 2}})
    lines, totals = diff_reports.diff_dirs(b, a)
    assert "x: 1 -> 2" in lines and totals["json_changes"] == 1
