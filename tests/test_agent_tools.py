"""Agent files without a shell leave their commands to the orchestrator (item 072).

R1, R2, R3 and I1 have no Bash on their `tools:` line, so they cannot run
`python3 scripts/...` themselves. Every line of such a file that names a
script command must say the orchestrator runs it. A missing or empty
`tools:` line is an error, never "no Bash": a sub-agent with no `tools:`
line inherits every tool, Bash included.
"""
import pytest

from conftest import REPO

NO_SHELL = {"r1-researcher", "r2-improver", "r3-fact-checker", "i1-reviewer"}


def _field(lines, key):
    """Return (found, entries) for `key:` in frontmatter lines.

    The value is a comma string, or, if empty, the following `- X` lines.
    """
    for i, line in enumerate(lines):
        if line.startswith(key + ":"):
            value = line[len(key) + 1:].strip()
            if value:
                return True, [v.strip() for v in value.split(",") if v.strip()]
            items = []
            for nxt in lines[i + 1:]:
                s = nxt.strip()
                if s.startswith("- "):
                    items.append(s[2:].strip())
                elif s == "-":
                    continue
                else:
                    break
            return True, items
    return False, []


def agent_tools(text):
    """Return (tool names, error). Bash is removed if `disallowedTools` lists it."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return set(), "no frontmatter"
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return set(), "no frontmatter"
    front = lines[1:end]
    found, entries = _field(front, "tools")
    if not found:
        return set(), "no tools: line (inherits every tool incl. Bash, item 072)"
    if not entries:
        return set(), "empty tools: (item 072)"
    tools = {e.split("(")[0].strip() for e in entries}
    _, denied = _field(front, "disallowedTools")
    tools -= {d.split("(")[0].strip() for d in denied}
    return tools, None


CASES = {
    "a_no_frontmatter": ("tools: Read\nbody\n", None, "no frontmatter"),
    "b_no_tools_line": ("---\nname: x\n---\nbody\n", None,
                        "no tools: line (inherits every tool incl. Bash, item 072)"),
    "c_empty_tools": ("---\nname: x\ntools:\n---\nbody\n", None, "empty tools: (item 072)"),
    "d_yaml_list": ("---\nname: x\ntools:\n  - Read\n  - Write\n---\nbody\n",
                    {"Read", "Write"}, None),
    "e_disallowed_bash": ("---\ntools: Read, Bash\ndisallowedTools: Bash(git push *)\n---\n",
                          {"Read"}, None),
    "f_bash_specifier": ("---\ntools: Read, Bash(git *)\n---\n", {"Read", "Bash"}, None),
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


def test_no_shell_agents_leave_commands_to_orchestrator():
    problems = []
    no_bash = set()
    files = sorted((REPO / ".claude" / "agents").glob("*.md"))
    assert files, "no agent files under .claude/agents"
    for path in files:
        rel = path.relative_to(REPO)
        text = path.read_text()
        tools, error = agent_tools(text)
        if error:
            problems.append(f"{rel}: {error}")
            continue
        if "Bash" in tools:
            continue
        no_bash.add(path.stem)
        lines = text.splitlines()
        body_start = next(i for i in range(1, len(lines)) if lines[i].strip() == "---") + 1
        for n, line in enumerate(lines[body_start:], body_start + 1):
            if "python3 scripts/" in line and "orchestrator" not in line:
                problems.append(f"{rel}:{n}: runs a script with no shell (item 072)")
    assert not problems, "\n".join(problems)
    assert no_bash == NO_SHELL, f"no-shell agents changed (RULES decision, item 072): {sorted(no_bash)}"
    run_item = (REPO / ".claude" / "commands" / "run-item.md").read_text()
    for s in ("the orchestrator runs their commands", "never writes to logs/"):
        assert s in run_item, f"run-item.md lacks {s!r} (item 072)"
