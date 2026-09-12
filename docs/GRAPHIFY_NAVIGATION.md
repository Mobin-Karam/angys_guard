# Graphify-first repository navigation

This is the canonical repository navigation policy for Laptop Guard.

The goal is to reduce unnecessary source reads and AI context/token usage while
making cross-file relationships easier to discover. Graphify is the **navigation
index**; current source, tests, configuration, and canonical documentation remain
the final authority.

## The rule

For any task that asks **what exists, where something lives, what calls what,
what depends on what, what will be affected, or how a part of the project works**:

```text
Graphify first
    -> identify the smallest relevant graph neighborhood
    -> open only the returned source/docs/tests
    -> confirm current behavior in authoritative files
    -> act or answer
```

Do not begin repository discovery by reading large files, recursively listing the
whole tree, opening `graphify-out/graph.json`, or grepping every directory when a
fresh Graphify graph can answer the navigation question first.

## 1. Check graph availability and freshness

The normal outputs are:

```text
graphify-out/GRAPH_REPORT.md   high-level graph summary and freshness metadata
graphify-out/graph.json        machine-readable graph; query through Graphify
graphify-out/graph.html        human interactive visualization
```

`GRAPH_REPORT.md` records the commit used to build the graph. Compare it with the
working repository before relying on graph coverage:

```bash
git rev-parse --short HEAD
grep -m1 'Built from commit:' graphify-out/GRAPH_REPORT.md
```

A graph is operationally fresh when the recorded build commit represents the
current code/docs state. A common clean workflow is:

1. make/commit the source or documentation change;
2. run `graphify update .` (or `/graphify . --update` in a supported assistant);
3. review the generated graph changes;
4. commit the refreshed `graphify-out/` outputs separately.

If Graphify is installed for an assistant, its native integration may perform
this check/navigation automatically. The repository policy still applies.

## 2. Query before reading files

Use the narrowest command that answers the navigation question:

```bash
graphify query "where is owner authorization enforced?"
graphify explain "LaptopGuard"
graphify path "InputMonitor" "EventStore"
```

Typical uses:

| Need | Start with |
|---|---|
| Find the owner of a behavior | `graphify query "where is <behavior> implemented?"` |
| Understand one class/function/concept | `graphify explain "<name>"` |
| Trace dependency/call relationship | `graphify path "<A>" "<B>"` |
| Estimate change impact | `graphify query "what depends on <symbol/feature>?"` |
| Locate tests | `graphify query "what tests cover <symbol/behavior>?"` |
| Find config/state/storage relationships | `graphify query "what connects <feature> to configuration/state/storage?"` |
| High-level orientation | skim `graphify-out/GRAPH_REPORT.md` |

Use names returned by one query as inputs to `explain` or `path` rather than
broadening immediately to repository-wide text search.

## 3. Confirm with authoritative files

Graphify narrows context; it does not replace source verification.

After the graph identifies likely paths/symbols:

- open only the relevant source ranges and nearest tests;
- read the applicable nested `AGENTS.md` before editing;
- use canonical docs for policy/architecture decisions;
- verify `EXTRACTED` vs `INFERRED` graph relationships when the distinction
  matters;
- treat direct current source as authoritative when graph output disagrees.

For a security-sensitive conclusion, migration, deletion, or refactor, confirm
all important edges/callers in source/tests before changing behavior.

## Token/context discipline

For AI agents:

- never load the complete `graph.json` into conversation context;
- prefer one or two targeted Graphify queries over broad file reads;
- use `GRAPH_REPORT.md` only for orientation, not as a substitute for source;
- open the smallest source ranges returned by graph navigation;
- avoid repeatedly reopening files already summarized unless exact lines changed;
- hand off paths/symbols/graph relationships between subagents instead of large
  copied source blocks;
- when delegating, tell subagents the relevant graph nodes/paths already found.

A good investigation normally has a small context shape:

```text
question
  -> 1-3 Graphify queries
  -> a few returned nodes/edges
  -> 1-4 relevant files/ranges
  -> focused tests/docs
```

## When direct search is allowed first

Graphify-first is the default, not a reason to use stale information.

Use targeted direct search/read first only when one of these is true:

1. `graphify-out/` does not exist;
2. the graph is stale and Graphify cannot be refreshed in the current environment;
3. the task concerns uncommitted/new files that are not indexed yet;
4. you need an exact literal/value/error string rather than relationship discovery;
5. you already know the exact file/symbol from the user's request and no repository
   discovery is needed;
6. Graphify returns no useful result after a small number of targeted queries.

When falling back, keep the search narrow and mention that Graphify was unavailable,
stale, or insufficient.

## Updating the graph

Install/register Graphify using its official instructions when needed. The local
CLI package is `graphifyy`; the command is `graphify`.

Useful update/install commands include:

```bash
uv tool install graphifyy
graphify install
graphify update .
graphify hook install
```

Supported assistants can also use `/graphify . --update` (Codex installations may
surface the skill with their native invocation syntax).

Do not add Graphify as a Laptop Guard runtime dependency. It is developer/agent
navigation tooling only.

## Human workflow

Humans can use the same path:

1. open `graphify-out/graph.html` for visual exploration;
2. use `GRAPH_REPORT.md` for hubs/communities/current hotspots;
3. use `graphify query/path/explain` for a precise question;
4. then inspect the returned source and tests.

`docs/FILE_REFERENCE.md` remains the curated ownership map, but Graphify should be
used first for live connection/call/dependency discovery.

## AI workflow

Every repository-aware AI tool should follow this order:

```text
AGENTS.md / tool compatibility instructions
        -> Graphify freshness
        -> graphify query/path/explain
        -> applicable canonical docs
        -> minimal source/tests
        -> plan/edit/review
```

The repo-local `navigator` agent and `$graphify-navigation` skill exist for tasks
where discovery itself is the main work.

## Security and privacy

Graph navigation must not be used to bypass normal repository safety rules.
Never use Graphify or fallback search to reveal `.env`, `secrets.json`, stop-PIN
material, tokens, private keys, or captured evidence. Query structural names and
relationships, then inspect only safe required sources.

## Maintenance rule

When files, symbols, architecture, tests, or important docs materially change,
refresh Graphify as part of repository maintenance. Do not manually edit generated
Graphify graph data to make it appear fresh; regenerate it with Graphify.

When this policy changes, update `AGENTS.md`, `docs/AI_AGENT_WORKFLOW.md`, and the
repo-local agent/skill compatibility surfaces in the same change.
