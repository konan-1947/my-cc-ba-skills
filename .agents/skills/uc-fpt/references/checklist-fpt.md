# FPT UC checklist (18 points + cross-references)

Adapted from the 20-point checklist of `uc-company` (BA Zone, Phuc NT): C8, C19, C20 removed (the FPT template has no Frequency, Includes or Special Requirements rows); FPT-specific checks added. Run `python scripts/validate-uc-fpt.py <file>` first for the mechanical items (marked M), then check the rest by reading.

## Scope and identification
- [ ] F1 Name is Verb + Object, active voice (heading `2.x.y <name>`)
- [ ] F2 User-goal level, passes the coffee-break test
- [ ] F3 UC-NN id unique, listed in the catalog with its Feature group
- [ ] F4 One primary actor, one goal, one session
- [ ] F5 System boundary clear; no overlap with another UC

## Actors and description
- [ ] F6 (M) Primary actor is one specific role (generic "User" only if defined in the actors table); secondary actors are external systems/services/devices or `None`, never a human role (heuristic)
- [ ] F6b Every secondary actor appears in at least one flow step, and every external call in the flow has its actor
- [ ] F7 (M) Description is "As a <primary actor>, I want to <goal>, so that <benefit>"; role equals Primary Actor; benefit adds information

## Conditions
- [ ] F8 (M, heuristic) Preconditions are states true before step 1 (prerequisite UC done, actor state, data state, environment), not actions, not vague ("system is ready"), not facts the UC checks itself; `None` only when nothing is required
- [ ] F9 (M, heuristic) Postconditions are verifiable results of success: outcome, state change (object, place, status, owner) for write UCs, side effects; no failure outcomes; each produced by a Normal Flow step
- [ ] F9b Chain: each precondition is made true by an earlier UC or an explicit setup; each state a postcondition creates is used by a later UC or ends the journey
- [ ] F10 Business rules cited by `BR-xx` where they constrain the UC

## Normal Flow
- [ ] F11 (M) First line is the UC name; numbered steps; 7-12 steps (warning above 12)
- [ ] F12 (M) Every step (Normal Flow; Alternative Flow lines as warning) starts with its subject: the primary actor, a secondary actor or the system; no bare verbs, no passive; step 1 is the primary actor's action; one action per step
- [ ] F13 (M, heuristic) No embedded if/else or loops
- [ ] F14 Flow runs from trigger to postcondition

## Alternative Flow (variants, failures and cancellations)
- [ ] F15 (M) Every block is titled `Step N_<condition>` with N a real Normal Flow step, blocks in ascending N, no repeated block, 1-8 lines
- [ ] F16 (M) Every block ends with exactly one ending: continues at Step M (M exists) or the use case ends
- [ ] F17 (M) Every line has a subject (actor, secondary actor, system, "The use case"); every failure cites a message id; failure blocks say whether data is kept or not stored
- [ ] F18 Derived by the walk (guide section 5): every step questioned by who performs it; invalid or missing input, cancel, state changed, save failure covered where they apply
- [ ] F18b (M) Every secondary actor has a failure block; every violable business rule has a violation block
- [ ] F18c No normal steps written as branches; conditions are states, not questions; identical handling is merged

## Cross-references
- [ ] X1 (M with `--registry`) Every `BR-xx` and `MSGnn` cited exists in the registers (SRS 5.1 / 5.2)
- [ ] X2 No invented ids: a needed new message is written `MSG??` with its text and reported for registration
- [ ] X3 UC-NN appears in at least one screen spec ("Mapped Use Case(s)") or is marked Non-UI
