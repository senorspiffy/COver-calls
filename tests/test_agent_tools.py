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
"""
import re

import pytest

from conftest import REPO

NO_SHELL = {"r1-researcher", "r2-improver", "r3-fact-checker", "i1-reviewer"}
NO_SHELL_ALLOWED = {"Read", "Write", "Glob", "Grep", "WebSearch", "WebFetch"}
ENTRY_RE = re.compile(r"[A-Za-z]+(\([^()]*\))?")


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
