# Design

## Context

See `proposal.md` - Why. The repo is greenfield: no application code, no `package.json`, no durable stack decision exists yet. `docs/backend-standards.md` prescribes Node.js/TypeScript/Express/Prisma, but it is inherited from another project and not yet validated against this one. The only tooling confirmed installed in this environment is Python 3.14 and Node 26 (Node's own framework is not scaffolded). `.apkg` generation (a later ticket) favors Python (`genanki`).

## Goals / Non-Goals

**Goals:**
- Implement the `text-input` capability (see `specs/text-input/spec.md`) as a reversible, thin slice.
- Keep the AC-1/AC-2/AC-3 logic framework-free so it can be ported to another stack without rewriting the behavior.

**Non-Goals:**
- Choosing the durable application stack. This slice uses Python + FastAPI + pytest for this capability only; it does not commit the project to that stack.
- Persistence design. An in-memory store is sufficient for this capability; a real datastore is a later concern.
- Real model/provider integration. A fake `GenerationPort` stands in for the real provider.
- Empty/whitespace-only UX (owned by AUTK-7/FR-3) beyond the minimal non-empty guard required by the spec.

## Decisions

### Framework-free core + thin HTTP shell
`src/autokards/input/policy.py` implements the AC-1/AC-2/AC-3 behavior (size check, integrity invariant, error construction) with no FastAPI imports. `src/autokards/api/app.py` is a thin adapter that parses the HTTP request and calls the core. Rationale: if the durable stack decision later moves away from FastAPI, `policy.py` ports with no behavior changes, only the adapter is rewritten. Alternative considered: put the logic directly in the FastAPI route — rejected because it couples the untested stack decision to the business rule the ticket actually requires.

### Limit expressed in bytes, not characters
The infrastructure ceiling is measured in bytes (`AUTOKARDS_MAX_INPUT_BYTES` env var), because the real constraint is transport/memory, not an editorial length rule. Rationale: AC-3 explicitly forbids a "character/word limit as product rule" — using characters would quietly reintroduce exactly that. Alternative considered: character count — rejected as it conflates a technical ceiling with a product rule.

### Reject before full buffering
The API layer enforces the byte ceiling while reading the request body (streaming check), returning `413 INPUT_TOO_LARGE` with `{limit_bytes, received_bytes}` before anything is persisted. Rationale: AC-2 requires no partial/truncated storage; checking after full buffering risks holding a partial object in memory that could leak into the store on a race. Alternative considered: buffer fully then check length — simpler, but allows a code path where a partially-read buffer could be mistaken for valid input.

### Provider errors are a distinct error family
Provider/model rejection (`422 INPUT_EXCEEDS_PROVIDER_LIMIT`) is modeled separately from the infra ceiling (`413 INPUT_TOO_LARGE`), via a `GenerationPort` interface with a fake implementation for this slice. Rationale: these are different failure sources (our infra vs. the provider's), and conflating them would hide which constraint actually fired, undermining AC-2's "explicit error" requirement.

### In-memory store
A simple dict-backed store holds accepted submissions. Rationale: no persistence requirement exists in the ticket; introducing a database now would be an unrequested architectural decision. Alternative considered: SQLite file — rejected as unnecessary for this slice's acceptance criteria.

## Risks / Trade-offs

- [Two stacks may eventually coexist if a later ticket picks Node/TS] → `policy.py` has no framework dependency, so porting it is a mechanical translation with the existing test suite as the acceptance check.
- [In-memory store loses data on restart] → Acceptable for AC-1..AC-3, which only require correctness of a single request/response cycle; no scenario requires durability across restarts.
- [Stack deviation from `docs/backend-standards.md` could be mistaken for a silent decision] → Proposal explicitly states this does not supersede the standard; a follow-up Jira chore will track the durable stack decision separately.
- [Byte-based limit may surprise contributors expecting a character limit] → Documented inline at the constant definition and in `docs/api/submissions.md`.

## Open Questions

- None. The stack choice, persistence approach, and provider integration are deliberately deferred as stated above, and none of them change this capability's specs or task breakdown.
