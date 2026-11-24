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

Item 087: a frontmatter line is also an error when its value starts with
`&`, `!`, `*`, `?` or `:` (anchor, tag, alias, explicit key), when a tab
comes before the value, when a `[` or `{` value is not closed on its own
line or is followed by text other than spaces or ` #...`, or when the line
is a YAML document marker (`...`, or `---` followed by a space or tab).
`tools:` and `disallowedTools:` lines are left to `_field`. This says
nothing about what Claude Code does with such a file. Known fail-closed
false errors: valid properties, aliases and explicit keys, plain values
starting with `?` or `:`, a tab after `-` or `key:`, a quote or apostrophe
inside a plain scalar inside a flow collection (`[it's]`), valid multi-line
flow collections, and block-scalar content lines that start with one of
these characters.

Item 096: a column-0 frontmatter line must be blank, a `#` comment, a `key:`
(followed by a space, a tab or the end of the line; the key does not start
with a YAML indicator, except `-` followed by a non-space; the key also
may not hold a `#` right after a space or tab, because YAML starts a comment
there (`a #b: c` has no key; `a#b: c` is the key `a#b`)), or a `- ` item
directly after a column-0 empty-valued key or another column-0 item. Blank
and comment lines (at any indent) are skipped. `tools:` and
`disallowedTools:` lines are left to `_field`. Anything else is an error.
This says nothing about what Claude Code does with such a file. Known
fail-closed false errors: a key with an inner colon not followed by a space
(`a:b: c`). Also rejected (YAML's reading not checked): a key with a tab
before `#` and no value (`a\t#b:`); a column-0 item after
an empty-valued key that carries a comment (`hooks: # c`); a column-0 item
after the indented content of an earlier column-0 item; text split by
`str.splitlines()` at \x0b, \x0c, \x1c, \x1d, \x1e, \x85, U+2028 or U+2029.
"""
import re

import pytest

from conftest import REPO

NO_SHELL = {"r1-researcher", "r2-improver", "r3-fact-checker", "i1-reviewer"}
NO_SHELL_ALLOWED = {"Read", "Write", "Glob", "Grep", "WebSearch", "WebFetch"}
ENTRY_RE = re.compile(r"[A-Za-z]+(\([^()]*\))?")
VALUE_START_RE = re.compile(r"""[ ]*(?:-[ \t]+)*(?:[^\s"'#&!*\[{?:][^:]*:[ \t]+)?(\S)""")
DOC_MARKER_RE = re.compile(r"(?:---|\.\.\.)(?:[ \t]|$)")
KEY_RE = re.compile(r"""(?:[^\s"'#&!*\[\]{},|>%@`?:-]|-(?=\S))(?:[^: \t]|[ \t](?!#))*:(?=[ \t]|$)""")
FLOW_KEYS = ("tools:", "disallowedTools:")
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


def _flow_end(line, start):
    """Return the index just past the closer matching the `[` or `{` at `start`, or None."""
    want = []
    i = start
    while i < len(line):
        ch = line[i]
        if ch in "\"'":
            i = _quote_end(line, i)
            if i is None:
                return None
            continue
        if ch == "#" and line[i - 1] in " \t":
            return None
        if ch in "[{":
            want.append("]" if ch == "[" else "}")
        elif ch in "]}":
            if want.pop() != ch:
                return None
            if not want:
                return i + 1
        i += 1
    return None


def _frontmatter_error(front):
    """Return the first frontmatter line the test cannot read on its own (items 080, 087, 096)."""
    prev_open = False
    for i, line in enumerate(front):
        n = i + 2
        if DOC_MARKER_RE.match(line):
            return DOC.format(n)
        lead = line[:len(line) - len(line.lstrip(" \t"))]
        if "\t" in lead:
            return f"tab in indentation on frontmatter line {n} (item 080)"
        m = VALUE_START_RE.match(line)
        if m:
            s, c = m.start(1), m.group(1)
            if "\t" in line[:s]:
                return TAB_BEFORE.format(n)
            if c in "&!*?:":
                return START.format(c, n)
            if c in "\"'":
                end = _quote_end(line, s)
                if end is None:
                    return f"unclosed quoted value on frontmatter line {n} (item 080)"
                if not AFTER_CLOSE_RE.fullmatch(line[end:]):
                    return f"text after closing quote on frontmatter line {n} (item 080)"
            elif c in "[{" and not line.startswith(FLOW_KEYS):
                end = _flow_end(line, s)
                if end is None:
                    return FLOW_OPEN.format(n)
                if not AFTER_CLOSE_RE.fullmatch(line[end:]):
                    return FLOW_AFTER.format(n)
        if line[:1] not in ("", " ", "\t", "#") and not line.startswith(FLOW_KEYS):
            if _is_item(line):
                if not prev_open:
                    return NO_KEY.format(n)
            elif not KEY_RE.match(line):
                return NO_KEY.format(n)
        t = line.strip()
        if t and not t.startswith("#"):
            k = KEY_RE.match(line)
            prev_open = line[0] != " " and (_is_item(line) or bool(k and not line[k.end():].strip()))
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
START = "value starts with '{}' on frontmatter line {} (item 087)"
FLOW_OPEN = "unclosed flow collection on frontmatter line {} (item 087)"
FLOW_AFTER = "text after closing bracket on frontmatter line {} (item 087)"
TAB_BEFORE = "tab before the value on frontmatter line {} (item 087)"
DOC = "document marker on frontmatter line {} (item 087)"
NO_KEY = "no key on frontmatter line {} (item 096)"
TOOLS = "tools: Read, Write"

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
    "p11_tab_after_colon": (_fm("tools:\tRead, Write"), None, TAB_BEFORE.format(2)),
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
    "q1_anchor_dq": (_fm('description: &d "Research team,', TOOLS, 'end"'),
                     None, START.format("&", 2)),
    "q2_tag_dq": (_fm('description: !!str "Research team,', TOOLS, 'end"'),
                  None, START.format("!", 2)),
    "q3_tag_sq": (_fm("description: !!str 'Research team,", TOOLS, "end'"),
                  None, START.format("!", 2)),
    "q4_anchor_tag_dq": (_fm('description: &a !!str "Research team,', TOOLS, 'end"'),
                         None, START.format("&", 2)),
    "q5_item_anchor": (_fm("hooks:", '  - &a "x,', TOOLS, 'y"'), None, START.format("&", 3)),
    "q6_item_open_quote": (_fm("hooks:", '  - "x,', TOOLS, 'y"'), None, UNCLOSED.format(3)),
    "q7_open_seq": (_fm("description: [a,", TOOLS, "]"), None, FLOW_OPEN.format(2)),
    "q8_open_map": (_fm("description: {a: b,", TOOLS, "}"), None, FLOW_OPEN.format(2)),
    "q9_quoted_closer": (_fm('description: ["]",', TOOLS, "]"), None, FLOW_OPEN.format(2)),
    "q10_comment_closer": (_fm("description: [a, # ]", TOOLS, "]"), None, FLOW_OPEN.format(2)),
    "q11_wrong_closer": (_fm("description: [a}", TOOLS), None, FLOW_OPEN.format(2)),
    "q12_text_after_flow": (_fm('description: [a] "x,', TOOLS, 'y"'),
                            None, FLOW_AFTER.format(2)),
    "q13_flow_next_line": (_fm("description:", "  [a,", TOOLS, "]"), None, FLOW_OPEN.format(3)),
    "q14_anchor_alone": (_fm("description: &d", '  "x,', TOOLS, 'y"'),
                         None, START.format("&", 2)),
    "q15_item_open_map": (_fm("hooks:", "  - {a: b,", TOOLS, "}"), None, FLOW_OPEN.format(3)),
    "q16_explicit_key": (_fm("? description", ': "Research team,', TOOLS, 'end"'),
                         None, START.format("?", 2)),
    "q17_colon_start": (_fm(': "Research team,', TOOLS, 'end"'), None, START.format(":", 2)),
    "q18_dash_tab": (_fm("hooks:", '  -\t"x,', TOOLS, 'y"'), None, TAB_BEFORE.format(3)),
    "q19_alias": (_fm("description: *d", TOOLS), None, START.format("*", 2)),
    "q20_tag_on_tools": (_fm("tools: !!str Read"), None, START.format("!", 2)),
    "q21_mid_value_amp": (_fm("description: Audit & Efficiency team", TOOLS),
                          {"Read", "Write"}, None),
    "q22_quoted_amp": (_fm('description: "&x"', TOOLS), {"Read", "Write"}, None),
    "q23_doc_mcp_example": (_fm("name: browser-tester",
                                "description: Tests features in a real browser using Playwright",
                                "tools: Read",
                                "mcpServers:",
                                "  # Inline definition: scoped to this subagent only",
                                "  - playwright:",
                                "      type: stdio",
                                "      command: npx",
                                '      args: ["-y", "@playwright/mcp@latest"]',
                                "  # Reference by name: reuses an already-configured server",
                                "  - github"),
                            {"Read"}, None),
    "q24_closed_flow_comment": (_fm('description: [a, "b]"] # c', TOOLS), {"Read", "Write"}, None),
    "q25_open_flow_last_line": (_fm(TOOLS, "description: [a,"), None, FLOW_OPEN.format(3)),
    "q26_disallowed_open": (_fm("tools: Read, Bash", "disallowedTools: [Bash,"), None,
                            "unclosed [ in disallowedTools: (item 075)"),
    "q27_doc_end_marker": (_fm("name: x", "...", TOOLS), None, DOC.format(3)),
    "q28_doc_start_marker": (_fm("name: x", "--- # c", TOOLS), None, DOC.format(3)),
    "q29_mid_value_markers": (_fm("description: Wait... then --- more", TOOLS), {"Read", "Write"}, None),
    "q30_marker_prefix_text": (_fm("name: x", "...x: y", "---x: z", TOOLS), {"Read", "Write"}, None),
    "q31_mid_value_bracket": (_fm("description: see [a and {b", TOOLS), {"Read", "Write"}, None),
    "nk1_plain_word": (_fm("name: x", "foo", TOOLS), None, NO_KEY.format(3)),
    "nk2_plain_word_last": (_fm("name: x", TOOLS, "foo"), None, NO_KEY.format(4)),
    "nk3_item_after_scalar": (_fm("name: x", "- a", "tools: Read"), None, NO_KEY.format(3)),
    "nk4_map_item_after_scalar": (_fm("name: x", "- a: b", TOOLS), None, NO_KEY.format(3)),
    "nk5_indicator_key": (_fm("name: x", "%x: y", TOOLS), None, NO_KEY.format(3)),
    "nk6_tools_col0_list": (_fm("name: x", "tools:", "- Read", "- Write"), {"Read", "Write"}, None),
    "nk7_item_after_empty_key": (_fm("description:", "- a", TOOLS), {"Read", "Write"}, None),
    "nk8_item_after_nested_map": (_fm("hooks:", "  a: b", "- c", TOOLS), None, NO_KEY.format(4)),
    "nk9_tools_blank_then_item": (_fm("tools:", "", "- Read"), None,
                                  "blank or comment line inside tools: list (item 075)"),
    "nk10_inner_colon_key": (_fm("a:b: c", TOOLS), None, NO_KEY.format(2)),
    "nk11_item_first_line": (_fm("- a", TOOLS), None, NO_KEY.format(2)),
    "nk12_indented_comment_then_item": (_fm("hooks:", "  # c", "- a", TOOLS), {"Read", "Write"}, None),
    "nk13_space_hash_in_key": (_fm("name: x", "a #b: c", TOOLS), None, NO_KEY.format(3)),
    "nk14_space_hash_empty_key_then_item": (_fm("a #b:", "- x", TOOLS), None, NO_KEY.format(2)),
    "nk15_hash_inside_key": (_fm("a#b: c", TOOLS), {"Read", "Write"}, None),
    "nk16_tab_hash_empty_key_then_item": (_fm("a\t#b:", "- x", TOOLS), None, NO_KEY.format(2)),
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
    "n10_anchor_description": ({"r1-researcher": f'---\ndescription: &d "Research team,\n'
                                                  f'tools: {SIX}\nend"\n---\n'},
                               None, [f"{R1}: {START.format('&', 2)}"],
                               NO_SHELL - {"r1-researcher"}),
    "n11_open_flow": ({"r1-researcher": f"---\ndescription: [a,\ntools: {SIX}\n]\n---\n"},
                      None, [f"{R1}: {FLOW_OPEN.format(2)}"], NO_SHELL - {"r1-researcher"}),
    "n12_no_key_line": ({"r1-researcher": f"---\nfoo\ntools: {SIX}\n---\n"}, None,
                        [f"{R1}: {NO_KEY.format(2)}"], NO_SHELL - {"r1-researcher"}),
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
