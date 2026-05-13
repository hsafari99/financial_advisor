# Financial Advisor — Canadian Retirement Planning System

## Purpose

This project produces a one-shot, comprehensive retirement plan for a Canadian (Quebec resident) using 14 specialized Claude Code subagents. The agents run in a pipeline with a targeted debate round on contested decisions. It is **not** a day-to-day tool — it runs once to produce an actionable plan, then re-runs annually (or after a major life event).

**This system does not provide financial advice.** Every output document opens with the disclaimer:

> ⚠️ Not professional financial advice. Verify with a fee-only Quebec-licensed planner before acting.

## How a planning session works

When the user starts a session in this directory and asks for a plan (e.g., "build my retirement plan"), the **lead-planner** agent (Opus 4.7) takes over and runs:

1. **Intake** — reads `profile.md`, validates completeness, asks targeted gap-check questions before proceeding.
2. **Analysis Wave 1** (parallel) — dispatches 11 specialists: tax-strategist, registered-accounts, cpp-oas-specialist, risk-insurance, real-estate-mortgage, brokerage-selector, fixed-income, canadian-equities, us-equities, international-equities, investment-style. Each writes to `analysis/<name>.md`.
3. **Analysis Wave 2** — `portfolio-constructor` reads Wave 1 outputs to build target allocation in `analysis/portfolio.md`.
4. **Analysis Wave 3** — `projections-accountant` reads everything to produce a year-by-year projection in `analysis/projections.md`.
5. **Identify contested decisions** — lead reads all `analysis/*.md` and selects 2–4 high-stakes calls where specialists conflict or where the call is non-obvious.
6. **Targeted debate** — for each contested decision, lead writes `debate/<topic>.md` framing, dispatches the 2–3 most relevant specialists for opening + rebuttal, then records the final call and rationale.
7. **Synthesis** — lead writes the 9 plan documents in `plan/`.
8. **Hand-off** — points the user to `plan/00-executive-summary.md`.

If `profile.md` is missing, the lead points the user to `templates/profile.template.md` and stops.

## File contracts

| File / dir | Read by | Written by |
|---|---|---|
| `profile.md` | every agent | user (and lead, during gap-fill only) |
| `analysis/<name>.md` | lead-planner; downstream specialists in later waves | the specialist named `<name>` only |
| `debate/<topic>.md` | lead-planner | lead-planner only |
| `plan/*.md` | user | lead-planner only |
| `templates/profile.template.md` | user | only updated when template structure changes |

**Hard rules:**
- A specialist writes only to its own `analysis/<name>.md`. Never to `profile.md`, never to another specialist's file, never to `plan/` or `debate/`.
- Only the lead-planner writes to `plan/` and `debate/`.
- Specialists do not dispatch other agents. Only the lead-planner orchestrates.
- Specialists must not request user input directly. If a gap is found mid-analysis, write it under `## Open questions for debate` in the analysis file; the lead surfaces it.

## Jurisdiction defaults

- Canadian federal tax + Quebec provincial tax.
- Quebec residents pay into **QPP** (Régime de rentes du Québec), not CPP. Where this distinction matters, use QPP. Use "CPP/QPP" only as a generic label.
- Quebec-specific tax credits and forms apply (T1 + TP-1).
- Default to Quebec rules; never silently apply Ontario or federal-only defaults.
- **Exception:** if `profile.md` indicates the user may leave Canada in retirement, agents flag departure-tax exposure to the lead, who escalates.

## Citation policy

Any **time-sensitive fact** MUST be cited with both a source URL and a retrieval date in ISO format. Time-sensitive facts include:

- Tax brackets (federal and Quebec)
- RRSP / TFSA / FHSA contribution limits and the user's CRA-stated room
- Brokerage fee schedules and commission/FX rates
- Bond yields, GIC rates, BoC overnight rate
- Specific share/ETF prices, P/E ratios, expense ratios, distribution yields
- CPP/QPP and OAS payment amounts and clawback thresholds

Format the citation inline:
> The 2026 TFSA limit is $XX,XXX (Source: https://www.canada.ca/..., retrieved 2026-04-27).

General-strategy reasoning ("max your TFSA before taxable investing") does **not** require citation. The lead-planner rejects un-cited time-sensitive claims during synthesis.

## Disclaimer policy

Every file in `plan/`, `analysis/`, and `debate/` opens with this exact line as the first line:

> ⚠️ Not professional financial advice. Verify with a fee-only Quebec-licensed planner before acting.

The `⚠️` emoji is the only place emojis are used in this project.

## Re-run / yearly update policy

When the user re-runs (typically yearly or after a major life event):

1. The user updates `profile.md` directly.
2. The lead-planner archives the existing `plan/` to `plan-archive/<YYYY-MM-DD>/` before regenerating.
3. The lead detects which `profile.md` sections changed and re-runs only the specialists whose inputs depend on the changed sections (e.g., income change → tax-strategist, registered-accounts, projections; rental change → real-estate-mortgage, projections).
4. The decision log lists what changed vs the prior plan and whether any prior decision is reversed.

## Out of scope

This system does **not** produce:

- Specific buy/sell timing recommendations
- Day-trading or short-term tactical calls
- Individual stock picks without an explicit "verify current fundamentals before purchase" warning
- Crypto allocation guidance beyond classifying it as a high-risk asset class
- Insurance product recommendations by issuer (only coverage-amount guidance)
- Estate or will drafting
- Tax-return preparation advice (strategy only)

## Entry point

If `profile.md` does not exist in the project root, copy `templates/profile.template.md` to `profile.md`, fill in every section, then ask the lead-planner to build the plan.

<!-- rtk-instructions v2 -->
# RTK (Rust Token Killer) - Token-Optimized Commands

## Golden Rule

**Always prefix commands with `rtk`**. If RTK has a dedicated filter, it uses it. If not, it passes through unchanged. This means RTK is always safe to use.

**Important**: Even in command chains with `&&`, use `rtk`:
```bash
# ❌ Wrong
git add . && git commit -m "msg" && git push

# ✅ Correct
rtk git add . && rtk git commit -m "msg" && rtk git push
```

## RTK Commands by Workflow

### Build & Compile (80-90% savings)
```bash
rtk cargo build         # Cargo build output
rtk cargo check         # Cargo check output
rtk cargo clippy        # Clippy warnings grouped by file (80%)
rtk tsc                 # TypeScript errors grouped by file/code (83%)
rtk lint                # ESLint/Biome violations grouped (84%)
rtk prettier --check    # Files needing format only (70%)
rtk next build          # Next.js build with route metrics (87%)
```

### Test (60-99% savings)
```bash
rtk cargo test          # Cargo test failures only (90%)
rtk go test             # Go test failures only (90%)
rtk jest                # Jest failures only (99.5%)
rtk vitest              # Vitest failures only (99.5%)
rtk playwright test     # Playwright failures only (94%)
rtk pytest              # Python test failures only (90%)
rtk rake test           # Ruby test failures only (90%)
rtk rspec               # RSpec test failures only (60%)
rtk test <cmd>          # Generic test wrapper - failures only
```

### Git (59-80% savings)
```bash
rtk git status          # Compact status
rtk git log             # Compact log (works with all git flags)
rtk git diff            # Compact diff (80%)
rtk git show            # Compact show (80%)
rtk git add             # Ultra-compact confirmations (59%)
rtk git commit          # Ultra-compact confirmations (59%)
rtk git push            # Ultra-compact confirmations
rtk git pull            # Ultra-compact confirmations
rtk git branch          # Compact branch list
rtk git fetch           # Compact fetch
rtk git stash           # Compact stash
rtk git worktree        # Compact worktree
```

Note: Git passthrough works for ALL subcommands, even those not explicitly listed.

### GitHub (26-87% savings)
```bash
rtk gh pr view <num>    # Compact PR view (87%)
rtk gh pr checks        # Compact PR checks (79%)
rtk gh run list         # Compact workflow runs (82%)
rtk gh issue list       # Compact issue list (80%)
rtk gh api              # Compact API responses (26%)
```

### JavaScript/TypeScript Tooling (70-90% savings)
```bash
rtk pnpm list           # Compact dependency tree (70%)
rtk pnpm outdated       # Compact outdated packages (80%)
rtk pnpm install        # Compact install output (90%)
rtk npm run <script>    # Compact npm script output
rtk npx <cmd>           # Compact npx command output
rtk prisma              # Prisma without ASCII art (88%)
```

### Files & Search (60-75% savings)
```bash
rtk ls <path>           # Tree format, compact (65%)
rtk read <file>         # Code reading with filtering (60%)
rtk grep <pattern>      # Search grouped by file (75%)
rtk find <pattern>      # Find grouped by directory (70%)
```

### Analysis & Debug (70-90% savings)
```bash
rtk err <cmd>           # Filter errors only from any command
rtk log <file>          # Deduplicated logs with counts
rtk json <file>         # JSON structure without values
rtk deps                # Dependency overview
rtk env                 # Environment variables compact
rtk summary <cmd>       # Smart summary of command output
rtk diff                # Ultra-compact diffs
```

### Infrastructure (85% savings)
```bash
rtk docker ps           # Compact container list
rtk docker images       # Compact image list
rtk docker logs <c>     # Deduplicated logs
rtk kubectl get         # Compact resource list
rtk kubectl logs        # Deduplicated pod logs
```

### Network (65-70% savings)
```bash
rtk curl <url>          # Compact HTTP responses (70%)
rtk wget <url>          # Compact download output (65%)
```

### Meta Commands
```bash
rtk gain                # View token savings statistics
rtk gain --history      # View command history with savings
rtk discover            # Analyze Claude Code sessions for missed RTK usage
rtk proxy <cmd>         # Run command without filtering (for debugging)
rtk init                # Add RTK instructions to CLAUDE.md
rtk init --global       # Add RTK to ~/.claude/CLAUDE.md
```

## Token Savings Overview

| Category | Commands | Typical Savings |
|----------|----------|-----------------|
| Tests | vitest, playwright, cargo test | 90-99% |
| Build | next, tsc, lint, prettier | 70-87% |
| Git | status, log, diff, add, commit | 59-80% |
| GitHub | gh pr, gh run, gh issue | 26-87% |
| Package Managers | pnpm, npm, npx | 70-90% |
| Files | ls, read, grep, find | 60-75% |
| Infrastructure | docker, kubectl | 85% |
| Network | curl, wget | 65-70% |

Overall average: **60-90% token reduction** on common development operations.
<!-- /rtk-instructions -->