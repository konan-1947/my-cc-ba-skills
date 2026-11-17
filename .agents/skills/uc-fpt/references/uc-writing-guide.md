# UC writing guide

Applies to both templates (FPT and Company). Merged from the `use-case` skill (jdm4pku/re-skills, based on Cockburn and Wiegers & Beatty) and adapted. For scope analysis and the 20-point checklist of the company engine, also use `use-case-writer`.

## 1. Use case or user story?

| | User story | Use case |
|---|---|---|
| Detail | 1-3 sentences | Full flow |
| Exceptions | Minimal | Comprehensive |
| Best for | Agile backlog, conversation starter | Complex flows, regulated systems, SRS deliverables |

Rule of thumb: start with a user story; write a use case when the interaction has **3 or more alternative flows** or needs detailed exception handling. An SRS deliverable (FPT template) is always use cases.

## 2. Levels

- Summary (kite): business process over several sessions ("Manage Chemical Inventory"): do not write as one UC; split.
- **User goal (sea level): one goal, one session ("Add Chemical to Inventory"): write UCs at this level.**
- Subfunction (fish): reusable step shared by UCs ("Authenticate User"): extract as a shared UC and reference it from the Normal Flow (Company template: Includes).

## 3. Step 1 - Identify UCs

For each user class list its goals; each sea-level goal is a candidate UC named with a verb phrase ("Place Order", "Generate Report"). Sources:
- user stories (one complex story may expand into one UC)
- event list (each business, signal or temporal event)
- context diagram (each data flow implies an interaction)
- ask users: "What do you come to the system to accomplish?"

Actors are people (roles) or external systems with goals. Internal components are not actors.

## 4. Step 2 - Normal flow

- One actor-system exchange per step; alternate Actor / System; active voice ("The system displays...").
- Same abstraction level for all steps; technology-neutral (no "click the blue button").
- **7-12 steps.** Beyond that, find natural breakpoints and split, or extract a shared subfunction.
- Optional **Trigger**: the event that starts the UC (for example "Pharmacist selects a prescription from the Ready to Fill queue"). Both templates carry it as an optional row; if omitted, step 1 states the trigger.

## 5. Step 3 and 4 - Alternatives and exceptions

At every step ask: What else could happen? What if the user chooses differently? What if the data is different? What could go wrong? What if the system or an external service is unavailable? What if input is invalid or missing?

- Alternative = valid variation. Exception = error condition.
- Name each one and anchor it to the Normal Flow step: FPT `Step N_<name>`, Company `UC-XX-YY.AC.n` / `.EX.n` with "At step N, if ...".
- Every one ends with where the flow resumes or that the UC ends.
- Document at least 2-3 exceptions per UC; no "TBD" for error handling. Failure paths state what data is kept or not stored.

## 6. Step 5 - Pre and postconditions

- Preconditions: assumed true, not tested by the UC (signed in, role, data exists).
- Postconditions: guaranteed after success and verifiable (status, stored data, log entry, ownership).

## 7. Anti-patterns

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Mega use case | 25+ steps covering everything | Split at user-goal level; shared steps become a subfunction UC |
| Implementation in disguise | Steps name widgets and positions | Keep steps neutral; layout belongs to the screen spec |
| Missing exceptions | Sunny day only | Run the "what could go wrong" question per step |
| System as actor | "The API calls the service" | Actors are roles or external systems with goals |
| Generic actor | "User" | Name the role (Teacher, Moderator) |

## 8. Review checklist

- [ ] Every step has a clear actor (user or system)
- [ ] Normal flow achieves the stated goal in 7-12 steps
- [ ] "What else?" asked at every step; alternatives explored
- [ ] Every exception has defined system behavior and a resume point
- [ ] Preconditions are assumptions, postconditions are verifiable
- [ ] Steps technology-neutral
- [ ] User-goal level, one goal per UC
- [ ] Rules and messages referenced by ID, not inlined (FPT: `BR-xx`, `MSGnn`)

## 9. Using the `use-case-writer` engine with the FPT template

`use-case-writer` (BA Zone, Phuc NT) is written for the 13-field Company template. Reuse its method for FPT work, with these adjustments:

| use-case-writer rule | For the FPT template |
|---|---|
| Step 1 modes A-D (write new, split into UC list, review, single section) | Reuse as is |
| Step 2 scoping: coffee-break test, 3 goal levels, one actor / one goal / one session, system boundary | Reuse as is |
| Identification techniques: goal-driven, event-driven, **CRUD-driven** | Reuse; CRUD-driven fits SRS groups such as Blog, Class, Community Hub (View / Create / Edit / Delete are separate UCs in the EDUA SRS) |
| Sequential mode: 5 groups, stop and confirm after each | Too slow for ~100 UCs. For SRS batches, write one whole UC (or one feature group) per confirmation |
| UC id `UC-<module>-<seq>` | FPT uses global ids `UC-NN` plus heading number `2.x.y` |
| Alternative Courses = still succeed; Exceptions = goal fails | FPT has no Exceptions field: both go into Alternative Flow blocks `Step N_<name>` |
| 20-point checklist C1-C7, C9-C19 | Apply |
| C8 (Frequency quantified), C19 (Includes), C20 (Special Requirements) | Not applicable to FPT; replace with the cross-reference ledger (BR / MSG ids) in the FPT template |
| Writing style: active voice, present tense, explicit subject, one step = one action, no embedded if/else in the Normal Flow | Apply fully |
| Output language English, artifact `.md` | Matches the SRS (English) |

Note: its own scope line says "DO NOT use for PRD/URD/SRS". Use it for the UC content only; the SRS structure, screens, messages and rules come from the other skills in `references/skill-gap.md`.

## 10. User stories upstream (`ba-zone-user-story-ac-writer`)

Optional step before UCs when requirements are still stories: INVEST check, at least 3 Given-When-Then AC (happy, edge, negative), split patterns (by CRUD, persona, business rule, data type). A story with 3+ alternative flows or heavy exception handling is escalated to a UC (section 1). The AC become the checklist for the UC's Alternative Flow coverage.
