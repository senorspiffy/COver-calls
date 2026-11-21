"""Agent files without a shell leave their commands to the orchestrator (item 072).

R1, R2, R3 and I1 have no Bash on their `tools:` line, so they cannot run
`python3 scripts/...` themselves. Every line of such a file that names a
script command must say the orchestrator runs it. A missing or empty
`tools:` line is an error, never "no Bash": a sub-agent with no `tools:`
line inherits every tool, Bash included.

Item 075: any `tools:` or `disallowedTools:` line or entry the parser cannot
read (an unclosed flow list, a quote, unbalanced parens, a continuation
line, a blank or comment line inside a block list, a missing space after
the colon, a duplicate key) is an error, never "not Bash". The four no-shell
agents may list only the names in NO_SHELL_ALLOWED.

Item 080: a frontmatter line the test cannot read on its own is an error,
because the test cannot tell which tools that file grants. The three cases
are a tab in the leading whitespace, a quoted value (at line start, after
`- `, or after `key: `) not closed on its line, and text after the closing
quote other than spaces or ` #...`. This says nothing about what Claude Code
does with such a file. Known fail-closed false errors: a tab at the start of
block-scalar content and a whitespace-only line containing a tab.
"""
import re

import pytest

from conftest import REPO

NO_SHELL = {"r1-researcher", "r2-improver", "r3-fact-checker", "i1-reviewer"}
NO_SHELL_ALLOWED = {"Read", "Write", "Glob", "Grep", "WebSearch", "WebFetch"}
ENTRY_RE = re.compile(r"[A-Za-z]+(\([^()]*\))?")
QUOTE_START_RE = re.compile(r"""[ ]*(?:-[ ]+)*(?:[^\s"'#][^:]*:[ \t]+)?(["'])""")
AFTER_CLOSE_RE = re.compile(r"( +#.*)? *")


def _is_item(s):
    return s == "-" or s.startswith("- ")


def _field(lines, key):
    """Return (found, entries, error) for `key:` in frontmatter lines.

    The value is a comma string, a one-line `[...]` flow list, or, if empty,
    the following `- X` lines. Anything else is an error (item 075).
    """
    starts = [i for i, line in enumerate(lines) if line.startswith(key + ":")]
    for i in starts:
        line = lines[i]
        if not (line == key + ":" or line.startswith(key + ": ") or line.startswith(key + ":\t")):
            return False, [], f"{key}: needs a space after the colon (item 075)"
    if len(starts) > 1:
        return False, [], f"duplicate {key}: line (item 075)"
    if not starts:
        return False, [], None
    i = starts[0]
    value = lines[i][len(key) + 1:].strip()
    items = []
    gap = False
    for line in lines[i + 1:]:
        s = line.strip()
        if not s or s.startswith("#"):
            gap = True
            continue
        if line[0] not in " \t" and not _is_item(s):
            break
        if value:
            return False, [], f"unparsed {key}: line '{s}' (item 075)"
        if not _is_item(s):
            return False, [], f"unparsed {key}: line '{s}' (item 075)"
        if gap:
            return False, [], f"blank or comment line inside {key}: list (item 075)"
        items.append(s[1:].strip())
    if value:
        if value.startswith("["):
            if not value.endswith("]"):
                return False, [], f"unclosed [ in {key}: (item 075)"
            value = value[1:-1].strip()
        raw = []
        if value:
            depth = 0
            cur = ""
            for ch in value:
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    if depth == 0:
                        return False, [], f"unbalanced ( ) in {key}: (item 075)"
                    depth -= 1
                if ch == "," and depth == 0:
                    raw.append(cur)
                    cur = ""
                else:
                    cur += ch
            if depth:
                return False, [], f"unbalanced ( ) in {key}: (item 075)"
            raw.append(cur)
    else:
        raw = items
    entries = []
    for x in raw:
        x = x.strip()
        if len(x) >= 2 and x[0] == x[-1] and x[0] in "\"'":
            x = x[1:-1]
        if not ENTRY_RE.fullmatch(x):
            return False, [], f"unparsed {key}: entry '{x}' (item 075)"
        entries.append(x)
    return True, entries, None


def _quote_end(line, start):
    """Return the index just past the quote closing the one at `start`, or None."""
    q = line[start]
    i = start + 1
    while i < len(line):
        ch = line[i]
        if q == '"':
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                return i + 1
        elif ch == "'":
            if line[i + 1:i + 2] == "'":
                i += 2
                continue
            return i + 1
        i += 1
    return None


def _frontmatter_error(front):
    """Return the first frontmatter line the test cannot read on its own (item 080)."""
    for i, line in enumerate(front):
        n = i + 2
        lead = line[:len(line) - len(line.lstrip(" \t"))]
        if "\t" in lead:
            return f"tab in indentation on frontmatter line {n} (item 080)"
        m = QUOTE_START_RE.match(line)
        if m:
            end = _quote_end(line, m.start(1))
            if end is None:
                return f"unclosed quoted value on frontmatter line {n} (item 080)"
            if not AFTER_CLOSE_RE.fullmatch(line[end:]):
                return f"text after closing quote on frontmatter line {n} (item 080)"
    return None


def agent_tools(text):
    """Return (tool names, error). Names in `disallowedTools` are removed."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return set(), "no frontmatter"
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return set(), "no frontmatter"
    front = lines[1:end]
    error = _frontmatter_error(front)
    if error:
        return set(), error
    found, entries, error = _field(front, "tools")
    if error:
        return set(), error
    if not found:
        return set(), "no tools: line (inherits every tool incl. Bash, item 072)"
    if not entries:
        return set(), "empty tools: (item 072)"
    tools = {e.split("(")[0] for e in entries}
    _, denied, error = _field(front, "disallowedTools")
    if error:
        return set(), error
    tools -= {d.split("(")[0] for d in denied}
    return tools, None


def tree_problems(texts):
    """Return (problems, no-Bash stems) for agent file texts keyed by stem."""
    if not texts:
        return ["no agent files under .claude/agents"], set()
    problems = []
    no_bash = set()
    for stem in sorted(texts):
        text = texts[stem]
        label = f".claude/agents/{stem}.md"
        tools, error = agent_tools(text)
        if error:
            problems.append(f"{label}: {error}")
            continue
        extras = tools - NO_SHELL_ALLOWED
        if stem in NO_SHELL and extras:
            problems.append(f"{label}: tools beyond the no-shell allow-list: "
                            f"{', '.join(sorted(extras))} (RULES decision, item 075)")
        if "Bash" in tools:
            continue
        no_bash.add(stem)
        lines = text.splitlines()
        body_start = next(i for i in range(1, len(lines)) if lines[i].strip() == "---") + 1
        for n, line in enumerate(lines[body_start:], body_start + 1):
            if "python3 scripts/" in line and "orchestrator" not in line:
                problems.append(f"{label}:{n}: runs a script with no shell (item 072)")
    return problems, no_bash


def _fm(*lines):
    return "---\n" + "\n".join(lines) + "\n---\nbody\n"


NO_TOOLS = "no tools: line (inherits every tool incl. Bash, item 072)"
UNCLOSED = "unclosed quoted value on frontmatter line {} (item 080)"
TAB = "tab in indentation on frontmatter line {} (item 080)"
AFTER = "text after closing quote on frontmatter line {} (item 080)"

CASES = {
    "a_no_frontmatter": ("tools: Read\nbody\n", None, "no frontmatter"),
    "b_no_tools_line": ("---\nname: x\n---\nbody\n", None, NO_TOOLS),
    "c_empty_tools": ("---\nname: x\ntools:\n---\nbody\n", None, "empty tools: (item 072)"),
    "d_yaml_list": ("---\nname: x\ntools:\n  - Read\n  - Write\n---\nbody\n",
                    {"Read", "Write"}, None),
    "e_disallowed_bash": ("---\ntools: Read, Bash\ndisallowedTools: Bash(git push *)\n---\n",
                          {"Read"}, None),
    "f_bash_specifier": ("---\ntools: Read, Bash(git *)\n---\n", {"Read", "Bash"}, None),
    "g_flow_list_bash": (_fm("tools: [Read, Write, Bash]"), {"Read", "Write", "Bash"}, None),
    "h_flow_list": (_fm("tools: [Read, Write]"), {"Read", "Write"}, None),
    "i1_double_quoted": (_fm('tools: Read, "Bash"'), {"Read", "Bash"}, None),
    "i2_block_single_quoted": (_fm("tools:", "  - 'Bash'"), {"Bash"}, None),
    "j1_stray_bracket": (_fm("tools: Read, Bash]"), None,
                         "unparsed tools: entry 'Bash]' (item 075)"),
    "j2_comment": (_fm("tools: Read, Write # Bash"), None,
                   "unparsed tools: entry 'Write # Bash' (item 075)"),
    "j3_unclosed": (_fm("tools: [Read, Bash"), None, "unclosed [ in tools: (item 075)"),
    "k_paren_comma": (_fm("tools: Agent(worker, researcher), Read"), {"Agent", "Read"}, None),
    "l_duplicate": (_fm("tools: Read", "tools: Bash"), None, "duplicate tools: line (item 075)"),
    "m_disallowed_flow": (_fm("tools: Read, Bash", "disallowedTools: [Bash]"), {"Read"}, None),
    "q_capital_key": (_fm("Tools: Read"), None, NO_TOOLS),
    "r_whole_quoted": (_fm("tools: 'Read, Bash'"), None,
                       "unparsed tools: entry ''Read' (item 075)"),
    "s_no_space": (_fm("tools:Read"), None, "tools: needs a space after the colon (item 075)"),
    "t1_unbalanced": (_fm("tools: Bash) (x"), None, "unbalanced ( ) in tools: (item 075)"),
    "t2_two_parens": (_fm("tools: Bash(a)(b)"), None,
                      "unparsed tools: entry 'Bash(a)(b)' (item 075)"),
    "u_empty_entry": (_fm("tools: Read,,Write"), None, "unparsed tools: entry '' (item 075)"),
    "v_empty_flow": (_fm("tools: []"), None, "empty tools: (item 072)"),
    "w_miscased_disallowed": (_fm("tools: Read, Bash", "disallowedtools: Bash"),
                              {"Read", "Bash"}, None),
    "x_block_scalar": (_fm("tools: >"), None, "unparsed tools: entry '>' (item 075)"),
    "y1_continuation": (_fm("tools: Read, Write", "  , Bash"), None,
                        "unparsed tools: line ', Bash' (item 075)"),
    "y2_blank_in_list": (_fm("tools:", "  - Read", "", "  - Bash"), None,
                         "blank or comment line inside tools: list (item 075)"),
    "y3_comment_first": (_fm("tools:", "  # leaders", "  - Read"), None,
                         "blank or comment line inside tools: list (item 075)"),
    "y4_indented_plain": (_fm("tools:", "  - Read", "    Bash"), None,
                          "unparsed tools: line 'Bash' (item 075)"),
    "y5_inline_then_item": (_fm("tools: Read", "  - Bash"), None,
                            "unparsed tools: line '- Bash' (item 075)"),
    "y6_blank_comment_then_key": (_fm("tools: Read, Write", "", "# c", "name: x"),
                                  {"Read", "Write"}, None),
    "y7_disallowed_blank": (_fm("tools: Read, Bash", "disallowedTools:", "  - Read", "",
                                "  - Bash"), None,
                            "blank or comment line inside disallowedTools: list (item 075)"),
    "z_space_before_colon": (_fm("tools : Read, Bash"), None, NO_TOOLS),
    "p1_dq_multiline": (_fm('description: "Research team,', "tools: Read, Write", 'end"'),
                        None, UNCLOSED.format(2)),
    "p2_sq_multiline": (_fm("description: 'Research team,", "tools: Read, Write", "end'"),
                        None, UNCLOSED.format(2)),
    "p3_tab_block_list": (_fm("tools:", "\t- Read", "\t- Write"), None, TAB.format(3)),
    "p4_bare_dash": (_fm("tools:", "  -"), None, "unparsed tools: entry '' (item 075)"),
    "p5_dq_escaped_end": (_fm('description: "abc\\"', "tools: Read", 'x"'),
                          None, UNCLOSED.format(2)),
    "p6_sq_doubled_end": (_fm("description: 'it''", "tools: Read", "x'"),
                          None, UNCLOSED.format(2)),
    "p7_open_quote_last_line": (_fm("tools: Read, Write", 'description: "abc'),
                                None, UNCLOSED.format(3)),
    "p8_text_after_close": (_fm('description: "a" "b', "tools: Read, Write"),
                            None, AFTER.format(2)),
    "p9_closed_quoted_colon": (_fm('description: "a: b"', "tools: Read, Write"),
                               {"Read", "Write"}, None),
    "p10_closed_sq_comment": (_fm("description: 'it''s' # c", "tools: Read, Write"),
                              {"Read", "Write"}, None),
    "p11_tab_after_colon": (_fm("tools:\tRead, Write"), {"Read", "Write"}, None),
    "p12_plain_inner_quote": (_fm('description: Use "this', "tools: Read, Write"),
                              {"Read", "Write"}, None),
    "p13_doc_hooks_example": (_fm("name: db-reader",
                                  "description: Execute read-only database queries",
                                  "tools: Bash",
                                  "hooks:",
                                  "  PreToolUse:",
                                  '    - matcher: "Bash"',
                                  "      hooks:",
                                  "        - type: command",
                                  '          command: "./scripts/validate-readonly-query.sh"'),
                              {"Bash"}, None),
    "p14_nested_open_quote": (_fm("hooks:", '  - matcher: "Bash', "tools: Read", 'x"'),
                              None, UNCLOSED.format(3)),
    "p15_quoted_key": (_fm('"tools": Read, Bash'), None, AFTER.format(2)),
}


@pytest.mark.parametrize("case", sorted(CASES))
def test_agent_tools_parser(case):
    text, want_tools, want_error = CASES[case]
    tools, error = agent_tools(text)
    assert error == want_error
    if want_error is None:
        assert tools == want_tools
        if case in ("d_yaml_list", "e_disallowed_bash"):
            assert "Bash" not in tools
        if case == "f_bash_specifier":
            assert "Bash" in tools


SIX = "Read, Write, Glob, Grep, WebSearch, WebFetch"
BASE = {stem: f"---\ntools: {SIX}\n---\n" for stem in NO_SHELL}
BASE.update({stem: "---\ntools: Read, Bash\n---\n"
             for stem in ("a1-auditor", "i2-builder", "i3-verifier")})
R1 = ".claude/agents/r1-researcher.md"


def _allow(name):
    return f"{R1}: tools beyond the no-shell allow-list: {name} (RULES decision, item 075)"


TREE = {
    "n0_baseline": ({}, None, [], NO_SHELL),
    "n1_flow_list_bash": ({"r1-researcher": f"---\ntools: [{SIX}, Bash]\n---\n"}, None,
                          [_allow("Bash")], NO_SHELL - {"r1-researcher"}),
    "n2_quoted_bash": ({"r1-researcher": f'---\ntools: {SIX}, "Bash"\n---\n'}, None,
                       [_allow("Bash")], NO_SHELL - {"r1-researcher"}),
    "n3_monitor": ({"r1-researcher": "---\ntools: Read, Monitor\n---\n"}, None,
                   [_allow("Monitor")], NO_SHELL),
    "n4_lower_bash": ({"r1-researcher": "---\ntools: Read, bash\n---\n"}, None,
                      [_allow("bash")], NO_SHELL),
    "n5_file_missing": ({}, "r1-researcher", [], NO_SHELL - {"r1-researcher"}),
    "n7_body_line": ({"r1-researcher": BASE["r1-researcher"] + "run python3 scripts/x.py\n"},
                     None, [f"{R1}:4: runs a script with no shell (item 072)"], NO_SHELL),
    "n8_quoted_description": ({"r1-researcher": f'---\ndescription: "Research team,\n'
                                                f'tools: {SIX}\nend"\n---\n'},
                              None, [f"{R1}: {UNCLOSED.format(2)}"], NO_SHELL - {"r1-researcher"}),
    "n9_tab_list": ({"r1-researcher": "---\ntools:\n"
                     + "".join(f"\t- {t}\n" for t in SIX.split(", ")) + "---\n"},
                    None, [f"{R1}: {TAB.format(3)}"], NO_SHELL - {"r1-researcher"}),
}


@pytest.mark.parametrize("case", sorted(TREE))
def test_tree_problems(case):
    changes, drop, want_problems, want_no_bash = TREE[case]
    texts = dict(BASE, **changes)
    if drop:
        del texts[drop]
    problems, no_bash = tree_problems(texts)
    assert problems == want_problems
    assert no_bash == want_no_bash
    if case == "n5_file_missing":
        assert no_bash != NO_SHELL


def test_tree_problems_no_files():
    assert tree_problems({}) == (["no agent files under .claude/agents"], set())


def test_no_shell_agents_leave_commands_to_orchestrator():
    files = sorted((REPO / ".claude" / "agents").glob("*.md"))
    assert files, "no agent files under .claude/agents"
    problems, no_bash = tree_problems({p.stem: p.read_text() for p in files})
    assert not problems, "\n".join(problems)
    assert no_bash == NO_SHELL, f"no-shell agents changed (RULES decision, item 072): {sorted(no_bash)}"
    run_item = (REPO / ".claude" / "commands" / "run-item.md").read_text()
    for s in ("the orchestrator runs their commands", "never writes to logs/"):
        assert s in run_item, f"run-item.md lacks {s!r} (item 072)"
