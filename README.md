# Financial Advisor

A 14-agent Claude Code system that produces a comprehensive Canadian (Quebec) retirement plan in a single, one-shot run.

## What this is

A panel of 13 specialized subagents — covering tax (federal + Quebec), registered accounts (RRSP/TFSA/FHSA/RRIF), Canadian/US/international equities, fixed income, brokerage selection, investment style, portfolio construction, CPP/QPP/OAS, risk and insurance, real estate, and projections — coordinated by a lead-planner agent. The lead reads your financial profile, dispatches the specialists in three waves, runs a targeted debate on the 2–4 most contested decisions, and writes a 9-document plan.

**This is not financial advice.** See the disclaimer that opens every output document.

## Quick start

1. Copy the profile template and fill it in (this file stays local — never committed):
   ```bash
   cp templates/profile.template.md profile.md
   ```
2. Open `profile.md` and complete every section. Sources you'll want handy: most recent CRA Notice of Assessment, brokerage statements, employer pension summary, mortgage statement, rental property records.
3. Start a Claude Code session in this directory:
   ```bash
   claude
   ```
4. Ask for a plan:
   ```
   > Build my retirement plan
   ```

The lead-planner reads `profile.md`, asks any gap-fill questions, then runs the full pipeline. When done, start with `plan/00-executive-summary.md`.

## What gets created

```
profile.md           ← your input (gitignored)
analysis/            ← raw per-specialist analyses (gitignored)
debate/              ← debate transcripts on contested decisions (gitignored)
plan/                ← final deliverable, 9 documents (gitignored)
  00-executive-summary.md       ← 1-page TL;DR + numbered action checklist
  01-strategy.md                ← narrative: why this approach
  02-portfolio.md               ← target allocation, holdings, rebalance rules
  03-accounts-and-contributions.md   ← what to fund in what order, $/year
  04-tax-strategy.md            ← yearly tax moves
  05-rental-property.md         ← keep/sell/refinance call + rationale
  06-projections.md             ← year-by-year projection, retirement number, scenarios
  07-risks-and-insurance.md     ← emergency fund, insurance gaps, hedging
  08-decision-log.md            ← contested decisions, what was argued, what was chosen
plan-archive/<YYYY-MM-DD>/  ← prior plan versions (gitignored)
```

Only project infrastructure (`CLAUDE.md`, `templates/`, `.claude/agents/`, `README.md`, `.gitignore`) is tracked in git. Personal financial data never is.

## Yearly update

```
> Update my retirement plan
```

The lead archives the prior `plan/` to `plan-archive/<date>/`, detects which `profile.md` sections changed, and re-runs only the affected specialists.

## Architecture

See `CLAUDE.md` for file contracts, jurisdiction defaults, citation policy, and out-of-scope rules every agent follows.

The 14 agents live in `.claude/agents/`:

| Agent | Model | Role |
|---|---|---|
| `lead-planner` | Opus 4.7 | Orchestration, debate, synthesis |
| `tax-strategist` | Sonnet 4.6 | Federal + Quebec tax optimization |
| `registered-accounts` | Sonnet 4.6 | RRSP/TFSA/FHSA/RRIF/RESP sequencing |
| `canadian-equities` | Sonnet 4.6 | TSX, REITs, dividend-tax-credit holdings |
| `us-equities` | Sonnet 4.6 | S&P/Nasdaq, USD exposure, foreign withholding |
| `international-equities` | Sonnet 4.6 | EAFE + emerging markets |
| `fixed-income` | Sonnet 4.6 | Bond ETFs, GICs, ladders |
| `brokerage-selector` | Sonnet 4.6 | Wealthsimple/Questrade/IBKR/big-bank DI |
| `investment-style` | Sonnet 4.6 | Active vs passive, DIY vs managed |
| `portfolio-constructor` | Sonnet 4.6 | Asset allocation, asset location, rebalance |
| `cpp-oas-specialist` | Sonnet 4.6 | CPP/QPP + OAS modeling, clawback |
| `risk-insurance` | Sonnet 4.6 | Emergency fund, insurance gaps |
| `real-estate-mortgage` | Sonnet 4.6 | Rental property + mortgage strategy |
| `projections-accountant` | Sonnet 4.6 | Multi-year compound projection, retirement number |

## Privacy

`profile.md`, `analysis/`, `debate/`, `plan/`, and `plan-archive/` are all in `.gitignore`. Verify before committing:

```bash
git status                          # should not list any of the above
git log -- profile.md plan/         # should be empty
```
