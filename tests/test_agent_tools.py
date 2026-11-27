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
before `#` and no value (`a\t#b:`); a column-0 item
after the indented content of an earlier column-0 item; text split by
`str.splitlines()` at \x0b, \x0c, \x1c, \x1d, \x1e, \x85, U+2028 or U+2029.

Item 104: a plain value (after a key or `- `, not quoted, not `[`/`{`, not a
block header) may not hold `:` followed by a space, a tab or its end,
outside a ` #` comment. An indented line indented past a scalar-valued
parent's node column is a continuation of that value and gets the same
check. A key (any indent) may not be longer than 1024 characters from its
first character to its colon. A value starting with `|` or `>` must be a
block header (style, optional chomping `-`/`+` and indent digit 1-9 in
either order, optional ` #` comment); the lines indented past the header
line's node column (and blank lines) are content, skipped by these checks
only. A key whose value is only a comment counts as empty-valued.
`tools:`/`disallowedTools:` lines are left to `_field`. This says nothing
about what Claude Code does with such a file. Known fail-closed false
errors: `tools: # c` followed by a column-0 item (`_field`). Not checked
(YAML's reading not checked): text after a closed quote or flow value on a
continuation line; a continuation that starts with `- ` outside
`tools:`/`disallowedTools:`; plain values starting with `@`, `%` or the
grave accent.

Item 106: a tab on a frontmatter line is an error unless it is inside the
quoted value that starts the value, after the first ` #` (a space, then
`#`) outside that quote or flow collection, on a block-scalar content line
or on a comment line; the pure-Python and libyaml PyYAML loaders disagree
on such tabs (measured on PyYAML 6.0.1, 6.0.3 and 6.0.4). A structure
line indented less than the line before must land on a level still open above
it (an earlier line's indent, an item's dash column or a node column). In
a `tools:`/`disallowedTools:` block list, every `- ` item has the first
item's indent. Inside a `tools:`/`disallowedTools:` field (up to the line
where `_field` stops), a continuation line is left to `_field`. This says
nothing about what Claude Code does with such a file. Known fail-closed
false errors: tabs that YAML 1.2 allows as separation white space
(`a\tb`, a trailing tab, `|\t# c`, `tools: Read,\tWrite`, a tab
in a key) and a tab inside a quoted item of a flow collection.

Item 111: after a `- ` item whose value on its line is a closed scalar
(plain, quoted or flow; no key, not empty, not a block header), a later line
indented past the item's last dash is a continuation line and gets the item
104 check. For a plain value not ended by ` #` this is how YAML reads the
line. After a quoted, flow or ` #`-ended value YAML starts no continuation,
and a colon there is refused all the same. A structure line that lands on an
open level first opened by a `- ` dash must be a `- ` item. A `- ` item that
lands on an open level first opened by a key must follow an empty-valued key
or another item at that level. This says nothing about what Claude Code does
with such a file. Known passes of files PyYAML rejects (both loaders raise,
measured on PyYAML 6.0.1 and 6.0.3, item 111): a line with no `: ` indented
past the dash of a quoted or ` #`-ended scalar item (`- "a"` / `  b`,
`- a # c` / `  b`); a `- ` item at a key's indent after that key's indented
value (`  a:` / `    b: c` / `  - x`); a key at the indent of a plain line
under an empty-valued key (`a:` / `  b` / `  c: d`). Not checked (YAML's
reading not checked): the same no-colon line after a flow scalar item.
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
BLOCK_RE = re.compile(r"[|>](?:[1-9][-+]?|[-+][1-9]?)?(?:[ \t]+#.*)?[ \t]*")
ITEMS_RE = re.compile(r"(?:-(?:[ \t]+|$))*")
COMMENT_CUT_RE = re.compile(r"[ \t]#")
COLON_RE = re.compile(r":(?:[ \t]|$)")
KEY_MAX = 1024
FLOW_KEYS = ("tools:", "disallowedTools:")
AFTER_CLOSE_RE = re.compile(r"( +#.*)? *")


def _is_item(s):
    return s == "-" or s.startswith("- ")


def _ends_field(line):
    """True if a frontmatter line ends a `tools:`/`disallowedTools:` field (item 106)."""
    return line[:1] not in ("", " ", "\t") and not _is_item(line.strip())


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
    first = None
    for line in lines[i + 1:]:
        s = line.strip()
        if not s or s.startswith("#"):
            gap = True
            continue
        if _ends_field(line):
            break
        if value:
            return False, [], f"unparsed {key}: line '{s}' (item 075)"
        if not _is_item(s):
            return False, [], f"unparsed {key}: line '{s}' (item 075)"
        if gap:
            return False, [], f"blank or comment line inside {key}: list (item 075)"
        lead = len(line) - len(line.lstrip(" "))
        if first is None:
            first = lead
        elif lead != first:
            return False, [], f"{key}: list items at different indents (item 106)"
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


def _is_open(rest):
    """True if the text after a key or `- ` is empty or only a comment (item 104)."""
    t = rest.strip(" \t")
    return not t or t.startswith("#")


def _plain_colon(text):
    """True if a plain value holds `:` before a space, a tab or its end, outside ` #` (item 104)."""
    m = COMMENT_CUT_RE.search(text)
    if m:
        text = text[:m.start()]
    return bool(COLON_RE.search(text.rstrip(" \t")))


def _node(line, n, check):
    """Return (error, node column, is open, starts a block) for a structure line (item 104)."""
    t = line.lstrip(" ")
    pos = len(line) - len(t)
    e = ITEMS_RE.match(t).end()
    col = pos + e
    t = t[e:]
    if _is_open(t):
        return None, col, True, False
    k = KEY_RE.match(t)
    if k:
        if check and k.end() - 1 > KEY_MAX:
            return KEY_LONG.format(n), col, False, False
        rest = t[k.end():]
        if _is_open(rest):
            return None, col, True, False
        t = rest.lstrip(" \t")
    if not check or t[0] in "\"'[{":
        return None, col, False, False
    if t[0] in "|>":
        if not BLOCK_RE.fullmatch(t):
            return BLOCK.format(n), col, False, False
        return None, col, False, True
    if _plain_colon(t):
        return VALUE.format(n), col, False, False
    return None, col, False, False


def _frontmatter_error(front):
    """Return the first frontmatter line the test cannot read on its own (items 080, 087, 096, 104, 106, 111)."""
    prev_open = False
    prev = None
    block = None
    stack = []
    in_flow = False
    kind = {}
    last_open = {}
    for i, line in enumerate(front):
        n = i + 2
        if DOC_MARKER_RE.match(line):
            return DOC.format(n)
        lead = line[:len(line) - len(line.lstrip(" \t"))]
        if "\t" in lead:
            return f"tab in indentation on frontmatter line {n} (item 080)"
        keep = cut = 0
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
                keep, cut = s, end
            elif c in "[{" and not line.startswith(FLOW_KEYS):
                end = _flow_end(line, s)
                if end is None:
                    return FLOW_OPEN.format(n)
                if not AFTER_CLOSE_RE.fullmatch(line[end:]):
                    return FLOW_AFTER.format(n)
                keep = cut = end
        if line[:1] not in ("", " ", "\t", "#") and not line.startswith(FLOW_KEYS):
            if _is_item(line):
                if not prev_open:
                    return NO_KEY.format(n)
            elif not KEY_RE.match(line):
                return NO_KEY.format(n)
        t = line.strip()
        if block is not None:
            if not t or len(line) - len(line.lstrip(" ")) > block:
                continue
            block = None
        if t and not t.startswith("#"):
            if "\t" in line[:keep] + line[cut:].split(" #", 1)[0]:
                return TAB_PLAIN.format(n)
            if line.startswith(FLOW_KEYS):
                in_flow = True
            elif _ends_field(line):
                in_flow = False
            ind = len(line) - len(line.lstrip(" "))
            if prev and not prev[1] and ind > prev[0]:
                if not in_flow and _plain_colon(t):
                    return VALUE.format(n)
            else:
                error, col, op, sb = _node(line, n, not line.startswith(FLOW_KEYS))
                if error:
                    return error
                popped = False
                while stack and stack[-1] > ind:
                    stack.pop()
                    popped = True
                if popped and (not stack or stack[-1] != ind):
                    return INDENT.format(n)
                dash = [ind + j for j, ch in enumerate(line[ind:col]) if ch == "-"]
                is_key = bool(KEY_RE.match(line[col:]))
                landed = bool(stack) and stack[-1] == ind
                if landed and not dash and kind[ind] == "seq":
                    return SEQ_LEVEL.format(n)
                if landed and dash and kind[ind] == "map" and not last_open[ind]:
                    return MAP_ITEM.format(n)
                if landed:
                    stack.pop()
                    last_open[ind] = True if dash else op
                levels = sorted({ind, col} | set(dash))
                for lv in levels:
                    if not (landed and lv == ind):
                        kind[lv] = "seq" if lv in dash else ("map" if lv == col and is_key else None)
                        last_open[lv] = op
                stack.extend(levels)
                if dash and not op and not sb and not is_key:
                    prev = (dash[-1], False)
                else:
                    prev = (col, op)
                if sb:
                    block = col
            k = KEY_RE.match(line)
            prev_open = line[0] != " " and (_is_item(line) or bool(k and _is_open(line[k.end():])))
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
VALUE = "colon in unquoted value on frontmatter line {} (item 104; quote the value)"
KEY_LONG = "key longer than 1024 characters on frontmatter line {} (item 104)"
BLOCK = "unreadable block scalar header on frontmatter line {} (item 104)"
TAB_PLAIN = "tab outside quotes and comments on frontmatter line {} (item 106)"
INDENT = "indent matches no open level on frontmatter line {} (item 106)"
SEQ_LEVEL = "non-item line at a list's dash column on frontmatter line {} (item 111)"
MAP_ITEM = "list item at the indent of a key with a value on frontmatter line {} (item 111)"
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
    "v1_value_colon": (_fm("name: x: y", TOOLS), None, VALUE.format(2)),
    "v2_value_colon_end": (_fm("name: x:", TOOLS), None, VALUE.format(2)),
    "v3_nested_value_colon": (_fm("hooks:", "  a: b: c", TOOLS), None, VALUE.format(3)),
    "v4_colon_in_comment": (_fm("description: a # see: b", TOOLS), {"Read", "Write"}, None),
    "v5_url_colon": (_fm("description: see https://x", TOOLS), {"Read", "Write"}, None),
    "v6_continuation_colon": (_fm("name: x", "  foo: bar", TOOLS), None, VALUE.format(3)),
    "v7_continuation_plain": (_fm("description: x", "  more text", TOOLS), {"Read", "Write"}, None),
    "v8_open_parent_plain": (_fm("description:", "  plain text", TOOLS), {"Read", "Write"}, None),
    "v9_block_literal": (_fm("description: |", "  a: b", TOOLS), {"Read", "Write"}, None),
    "v10_block_folded_indicators": (_fm("description: >-2 # c", "  x: y", TOOLS),
                                    {"Read", "Write"}, None),
    "v11_block_header_text": (_fm("description: > foo", TOOLS), None, BLOCK.format(2)),
    "v12_block_ends": (_fm("description: |", "  a: b", "name: x: y", TOOLS), None, VALUE.format(4)),
    "v13_key_1025": (_fm("k" * 1025 + ": v", TOOLS), None, KEY_LONG.format(2)),
    "v14_key_1024": (_fm("k" * 1024 + ": v", TOOLS), {"Read", "Write"}, None),
    "v15_key_1025_after_key": (_fm("name: x", "k" * 1025 + ": v", TOOLS), None, KEY_LONG.format(3)),
    "v16_key_1025_indented": (_fm("hooks:", "  " + "k" * 1025 + ": v", TOOLS),
                              None, KEY_LONG.format(3)),
    "v17_key_1024_indented": (_fm("hooks:", "  " + "k" * 1024 + ": v", TOOLS), {"Read", "Write"}, None),
    "v18_comment_key_then_item": (_fm("hooks: # c", "- a", TOOLS), {"Read", "Write"}, None),
    "v19_spec_two_comments": (_fm("hr: # 1998 hr ranking", "- Mark McGwire", "- Sammy Sosa",
                                  "# 1998 rbi ranking", "rbi:", "- Sammy Sosa", "- Ken Griffey",
                                  TOOLS), {"Read", "Write"}, None),
    "v20_comment_key_then_map": (_fm("hooks: # c", "  a: b", TOOLS), {"Read", "Write"}, None),
    "v21_tools_comment_then_item": (_fm("tools: # c", "- Read"), None,
                                    "unparsed tools: line '- Read' (item 075)"),
    "v22_tools_entry_colon": (_fm("tools: Read, Bash: x"), None,
                              "unparsed tools: entry 'Bash: x' (item 075)"),
    "v23_hash_in_word_colon": (_fm("name: a#b: c", TOOLS), None, VALUE.format(2)),
    "v24_gt_inside_value": (_fm("description: a > b", TOOLS), {"Read", "Write"}, None),
    "v25_bar_inside_value": (_fm("description: a | b", TOOLS), {"Read", "Write"}, None),
    "v26_dash_key_continuation": (_fm("-a: b", " c: d", TOOLS), None, VALUE.format(3)),
    "w1_tab_before_hash_colon": (_fm("description: a\t# see: b", TOOLS), None, TAB_PLAIN.format(2)),
    "w2_tab_before_hash": (_fm("description: a\t# c", TOOLS), None, TAB_PLAIN.format(2)),
    "w3_tab_in_plain": (_fm("description: a\tb", TOOLS), None, TAB_PLAIN.format(2)),
    "w4_tab_in_continuation": (_fm("description: x", "  more\t# c", TOOLS), None, TAB_PLAIN.format(3)),
    "w5_tab_in_item": (_fm("hooks:", "  - a\t# c", TOOLS), None, TAB_PLAIN.format(3)),
    "w6_tab_in_block_header": (_fm("description: |\t# c", "  a", TOOLS), None, TAB_PLAIN.format(2)),
    "w7_tab_in_quote": (_fm('description: "a\t# b"', TOOLS), {"Read", "Write"}, None),
    "w8_tab_in_comment": (_fm("description: a # x\ty", TOOLS), {"Read", "Write"}, None),
    "w9_tab_after_bare_hash": (_fm("description: a#\tb", TOOLS), None, TAB_PLAIN.format(2)),
    "w10_tab_in_empty_key": (_fm("a\tb:", "  c: d", TOOLS), None, TAB_PLAIN.format(2)),
    "w11_tab_in_block_content": (_fm("description: |", "  a\tb", TOOLS), {"Read", "Write"}, None),
    "w12_tab_in_comment_line": (_fm("# a\tb", TOOLS), {"Read", "Write"}, None),
    "w13_tab_in_flow_after_quoted_hash": (_fm('description: ["a #", b\tc]', TOOLS), None,
                                          TAB_PLAIN.format(2)),
    "tb1_tools_comma_tab": (_fm("tools: Read,\tWrite"), None, TAB_PLAIN.format(2)),
    "tb2_tools_trailing_tab": (_fm("tools:\t", "  - Read"), None, TAB_PLAIN.format(2)),
    "tb3_tools_flow_tab": (_fm("tools: [Read,\tWrite]"), None, TAB_PLAIN.format(2)),
    "s1_map_dedent_between": (_fm("hooks:", "    a: b", "  c: d", TOOLS), None, INDENT.format(4)),
    "s2_tools_list_dedent": (_fm("tools:", "    - Read", "  - Write"), None, INDENT.format(4)),
    "s3_compact_map_in_list": (_fm("hooks:", "  - a: b", "    c: d", "  - e: f", TOOLS),
                               {"Read", "Write"}, None),
    "s4_dedent_off_level": (_fm("hooks:", "  - a: b", " c: d", TOOLS), None, INDENT.format(4)),
    "s5_indented_first_line": (_fm("  name: x", TOOLS), None, INDENT.format(3)),
    "s6_list_at_key_indent": (_fm("hooks:", "  a:", "  - x", "  b: c", TOOLS), {"Read", "Write"}, None),
    "s7_nested_dash_levels": (_fm("hooks:", "  - - a", "    - b", TOOLS), {"Read", "Write"}, None),
    "c1_tools_continuation_key": (_fm("tools: Read, Write", "  Bash: x"), None,
                                  "unparsed tools: line 'Bash: x' (item 075)"),
    "c2_tools_item_continuation_key": (_fm("tools:", "  - Read", "      Bash: x"), None,
                                       "unparsed tools: line 'Bash: x' (item 075)"),
    "c3_disallowed_continuation_key": (_fm("tools: Read, Bash", "disallowedTools: Bash", "  Read: x"),
                                       None, "unparsed disallowedTools: line 'Read: x' (item 075)"),
    "c4_flag_cleared_by_key": (_fm("tools: Read, Write", "name: x", "  foo: bar"), None, VALUE.format(4)),
    "c5_tools_col0_item_continuation": (_fm("tools:", "- Read", "      Bash: x"), None,
                                        "unparsed tools: line 'Bash: x' (item 075)"),
    "f1_tools_item_indents": (_fm("tools:", "  - Read", "      - Bash"), None,
                              "tools: list items at different indents (item 106)"),
    "g1_item_scalar_then_key": (_fm("hooks:", "- a", "  b: c", "tools: Read"), None, VALUE.format(4)),
    "g2_indented_item_scalar_then_key": (_fm("hooks:", "  - a", "    b: c", "tools: Read"), None,
                                         VALUE.format(4)),
    "g3_item_scalar_continuation": (_fm("hooks:", "- a", "  b", TOOLS), {"Read", "Write"}, None),
    "g4_quoted_item_then_key": (_fm("hooks:", '- "a"', "  b: c", TOOLS), None, VALUE.format(4)),
    "er1_key_at_item_dash": (_fm("hooks:", "  - x", "  a: v", TOOLS), None, SEQ_LEVEL.format(4)),
    "d3_item_after_scalar_key": (_fm("hooks:", "  a: v", "  - x", TOOLS), None, MAP_ITEM.format(4)),
    "k2_item_after_reset_key": (_fm("hooks:", "  a:", "  - x", "  b: v", "  - y", TOOLS), None,
                                MAP_ITEM.format(6)),
    "k4_reopened_level_map": (_fm("hooks:", "  - x", "name:", "  a: b", "  c: d", TOOLS),
                              {"Read", "Write"}, None),
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
    "n13_value_colon": ({"r1-researcher": f"---\nname: x: y\ntools: {SIX}\n---\n"}, None,
                        [f"{R1}: {VALUE.format(2)}"], NO_SHELL - {"r1-researcher"}),
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
