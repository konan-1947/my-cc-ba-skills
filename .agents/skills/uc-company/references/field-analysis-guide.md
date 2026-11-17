# Field analysis guide: derive each UC field, never copy it

A UC field is the result of analysing the function, not text to copy from another document. A sample SRS (including the EDUA Word file) shows one team's output; it is evidence of the structure, never the source of the answer. For every field below: apply the analysis, then write.

## 1. Primary actor (who starts it)

Question: who triggers this function to reach their own goal?

- A role (Teacher, Moderator, Student) or a state of a role (Visitor = not signed in, Signed-in user). One UC has **one** primary actor.
- Several roles can do it:
  - the capability is identical -> use the generalized actor defined in the actors table (for example `User`, if the document defines it as "any person using the system"),
  - the behavior differs by role -> one UC per role (or a UC with the role differences in Alternative Flow). Never write "Teacher or Moderator".
- Who is not a primary actor: someone who only receives a result (that is another UC, for example View Notifications), internal components, the system itself.

## 2. Secondary actors (what outside the product it touches)

Secondary actors are **objects outside the system boundary that take part in this function**: external services, other systems, devices. They are **not additional human users**.

Analysis procedure, per function:

1. Walk the Normal Flow. At each step ask: does the system send something to, or get something from, anything that is **not** the primary actor and **not** part of our product?
2. List what you find. Typical candidates: identity provider (Google OAuth), AI/LLM service, object/file storage, email/SMS/push service, payment gateway, map/geocoding, analytics, third-party content API, another school system (LMS, student information system, timetable), a device (printer, camera, scanner, sensor).
3. Keep an object only if the function really depends on it. The system's own database, modules, cache, queue and "document converter" library are internal: not actors.
4. If nothing is left, write `None`.

Another **person** is never a secondary actor:
- A human who acts later (Moderator approves what the Teacher submitted) is the **primary actor of a different UC**; connect the two through the postcondition/status, not through the actors row.
- A human who merely gets notified: the interaction is with a messaging service (secondary: Email Service) or a separate "View Notifications" UC.

Worked examples:

| Function | Primary | Secondary | Why |
|---|---|---|---|
| View the public homepage | Visitor | None | pure display; no external object |
| Sign in with Google | Visitor | Google Identity Provider | the system exchanges tokens with it |
| Generate a lesson plan with AI | Teacher | AI/LLM Service | prompt out, content back |
| Upload a profile avatar | User | Object Storage | file stored outside the application |
| Export a lesson plan to PDF | Teacher | None | conversion is an internal component (if it were a third-party service, list the service) |
| Approve a lesson plan | Moderator | None | the Teacher is not an actor here; Teacher's UC "Submit for review" is separate |
| Send a weekly task reminder | Scheduler / Moderator | Email Service | the mail gateway participates |

## 3. Description: `As a <role>, I want to <goal>, so that <benefit>`

Structure to derive and check:

- **As a** `<role>`: the primary actor from section 1, same name as in the actors table. Not a person's name, not "the system".
- **I want to** `<goal>`: one verb phrase, the goal at user-goal level (verb + object), in the actor's words, with no UI mechanics ("click", "tab", "button"). It restates the UC name in a sentence, never a technology.
- **so that** `<benefit>`: the value to the actor or the business that the goal produces. It must **add** information: if the benefit only repeats the goal ("I want to view the homepage so that I can see the homepage") it fails; answer "what does the actor get or decide because of this?".

Derivation questions: who? -> what are they trying to achieve in this one session? -> why do they care (what happens next because of it)?

Example (function: public homepage): `As a visitor, I want to view the public homepage to learn about the platform, its features and available teaching tools, so that I can decide whether to sign in or explore further.` Role = visitor (primary actor), goal = view the homepage (verb + object, purpose "to learn..."), benefit = a decision.

Weak forms to rewrite: "As a user, I want a page", "I want to be able to ...", "so that I can use the system", a goal that names a component ("call the OAuth API").

## 4. Preconditions and postconditions

Examples in this guide **illustrate** the analysis; they are not templates. The method and the fill-in structure below apply to any product and any domain.

### Definitions

- **Precondition**: something that must **already be true before** the use case can start, because an earlier action, setup or configuration made it true. It is assumed by this UC, not produced or tested by it. Typical case: the previous UC in the user's journey has been completed (to sign in successfully, the account must already be registered).
- **Postcondition**: what is **true after the use case succeeds**: the result the actor obtains and the state the system is left in. It is the observable output of the goal (creating a lesson plan succeeds when the plan exists and is saved in the library).

They chain: the postcondition of one UC is (part of) the precondition of the next: `Register account` ends with "the account exists and is active", which is the precondition of `Log in`. When you write a precondition, name the UC or setup that makes it true; when you write a postcondition, ask which UCs depend on it.

### Kinds of preconditions (check each kind; keep the ones that apply)

| Kind | Question | Generic form |
|---|---|---|
| Prerequisite action done | which earlier UC or setup must have succeeded? | `<Object> <exists / is registered / is configured>` (produced by UC-xx) |
| Actor state | what must be true about the actor? | `The <actor> is <authenticated / authorized for ... / the owner of ...>` |
| Data state | which object does the UC work on, and in which status may it be used? | `The <object> exists and has status <S>` |
| Environment | what outside the UC must be available? | `<Service / catalog / configuration> is available` |

Rules: a precondition is a **fact about the world before step 1**, written as a state ("is", "has", "exists"), never as an action ("the user opens ..."). If the use case itself **checks** the fact and handles the failure (for example "balance is sufficient" is verified in the flow), it is not a precondition: it belongs to the Normal Flow and an Alternative Flow. Use `None` only when nothing needs to be true first (a public page).

### Kinds of postconditions (check each kind; keep the ones that apply)

| Kind | Question | Generic form |
|---|---|---|
| Outcome / output | what does the actor obtain? | `The <result> is <displayed / issued / available> ...` |
| State change | what data was created, changed, deleted, moved? | `The <object> is <created / updated / deleted> in <place> with status <S>, owned by <actor>` |
| Side effect | what else happened as a consequence? | `A <notification / log entry / balance update> is <sent / written / applied>` |

Rules: **success only** (failure outcomes live in the Alternative Flow that causes them); each item must be **verifiable** by a tester after the run; each item must be **produced by a step** of the Normal Flow; together they must express the goal in the Description. A read-only UC (view, search) has an outcome ("the list is displayed") and usually no state change; a write UC always has a state change.

### Fill-in structure (any domain)

```
Preconditions
- <Actor/Object> <is/has/exists ...>          [kind: prerequisite | actor | data | environment]   (made true by: UC-xx / setup)
Postconditions
- <Result> <is displayed/issued/available>    [kind: outcome]
- <Object> <is created/updated/deleted> in <place>, status <S>, owner <actor>   [kind: state change]
- <Notification/log/update> <is sent/written/applied>                           [kind: side effect]
```
(The bracketed kinds and sources are analysis notes; write them in the document only if the project's template shows them.)

### Illustrations across domains (not templates)

| Domain | UC | Preconditions | Postconditions |
|---|---|---|---|
| Any app | Log in | The user's account is registered and active (from `Register account`). | An authenticated session exists for the user; the user is on the home page. |
| Teaching platform | Create lesson plan | The teacher is signed in. The selected lesson belongs to the supported catalog. | The lesson plan is created and saved in the teacher's library as Draft, owned by the teacher. |
| Banking | Transfer money | The customer is authenticated. The source account exists and is active. | The transfer is recorded; both balances are updated; a confirmation is issued. |
| E-commerce | Place order | The customer is signed in. The cart holds at least one item. | An order exists with status Placed; stock is reserved; a confirmation is sent. |
| HR | Approve leave request | A request exists with status Pending. The approver is the requester's manager. | The request has status Approved; the leave balance is reduced; the employee is notified. |
| Healthcare | Book appointment | The patient is registered. The clinic has published available slots. | An appointment exists in the chosen slot; the slot is no longer available; a reminder is scheduled. |
| Public website | View homepage | None. | The public homepage is displayed. |

How each row was derived: precondition = what the earlier journey step or setup already produced and the actor's state; postcondition = outcome + what changed + what followed. Verified-in-the-flow checks (balance sufficient, slot still free) are not preconditions.

### Quick tests

- Precondition test: "Could step 1 happen if this were false?" If not, it is a precondition; if the UC would detect it and react, it is a flow check.
- Postcondition test: "What would a tester check afterwards?" Each answer is a postcondition item.
- Chain test: every precondition is the postcondition of some UC or an explicit setup; every state a postcondition creates is used by some later UC (or is the end of the journey).

## 5. Normal flow and alternatives

### Every step starts with its subject

A step is one actor doing one thing, and the sentence says **who**: `The <actor> <verb> ...` or `The system <verb> ...` (or the secondary actor: `The AI/LLM Service returns ...`). A step that starts with a bare verb ("Opens the menu", "Displays the available account actions") is wrong, because nobody is named as doing it. Passive sentences ("The session is cleared", "The page is shown") hide the subject and are rewritten with one ("The system clears the session").

- The flow **begins with the primary actor's action** (the trigger). It begins with the system only when a system trigger starts the UC (scheduler, incoming event).
- Subjects alternate naturally: actor acts, system responds; consecutive system steps are fine when the system really does several things in a row.
- Use the same subject name everywhere (the Primary Actor's name: "The user", "The teacher"), never "he/she/they/it".
- One subject, one action per step. If a step needs "and" between two different actions, split it.

Worked example, Logout (primary actor User, secondary actors None):

| # | Wrong | Right |
|---|---|---|
| 1 | Opens the account menu. | The user opens the account menu. |
| 2 | Displays the available account actions. | The system displays the available account actions. |
| 3 | Select Log out. | The user selects Log out. |
| 4 | The session is terminated. | The system terminates the current user session. |
| 5 | Redirect to the landing page. | The system redirects the user to the public landing page. |

Derivation: goal = end my session; trigger = the user opens the account menu (actor first); the system shows the actions, the user chooses, the system ends the session, the system sends the user to the public page. Secondary actors: the session is internal, so `None`.

### Normal flow

- The shortest path to the goal, alternating actor and system, 7-12 steps.
- For each step ask: what else could the actor choose (variant)? what if the data is invalid or missing? what if an external object from section 2 fails or is slow? what if the state has changed (permission, concurrent edit)? Each answer is a named alternative anchored to a step, ending with where the flow resumes or that the UC ends.
- A secondary actor from section 2 usually creates at least one alternative (its failure): if you list `Google Identity Provider` and no step or alternative mentions it, either the actor or the flow is incomplete.

### Alternative flows, derived by analysis

An alternative flow describes what happens when, at one specific step of the Normal Flow, something differs. It is not a second story: it is a short branch that leaves the Normal Flow at a step and either comes back or ends.

Kinds (all use the same block; the ending shows the kind):
- **Variant**: another route to the same goal (the actor picks a different option). Ends by continuing the Normal Flow.
- **Failure**: the step cannot be completed (invalid input, rule violated, external object down, save fails). Ends by retrying/resuming, or by ending the use case.
- **Cancellation**: the actor abandons. Ends the use case without changing data.

Derivation walk, step by step. For every Normal Flow step ask the questions that fit **who performs it**:

| Step performed by | Ask |
|---|---|
| the actor | chooses differently or backs out? input missing, malformed or out of range? not allowed (role, ownership, status)? session expired or state changed since the previous step? |
| the system | a business rule fails (cite `BR-xx`)? nothing found (empty state)? duplicate or concurrent change? saving fails? |
| a secondary actor (external object) | unavailable or timeout? error response? invalid, partial or empty response? quota or rate limit? |

Then prune: keep a condition only if it changes behavior (different response, different data effect, different ending); merge conditions that are handled identically; drop the impossible.

Block shape:

```
**Step N_<condition>**
The system ...                      behavior, each line with its subject; what the user sees (cite MSGnn); what happens to data (kept / not stored)
The <actor> may ...                 optional recovery choice
The use case continues at Step M of the Normal Flow.     (or "The use case ends.")  exactly one ending
```

- `N` is the step where the condition is **detected**; the condition is a state ("Session already expired"), not a question and not an instruction. Several blocks may share a step; list blocks in ascending `N`.
- Every line follows the subject rule (actor, secondary actor, system, or "The use case"/"The flow" for the ending).
- 1 to 8 lines. If a branch needs a full story, it is a separate UC (or an `include`d sub-flow).
- Every failure shows the user something: cite a message id.
- Every secondary actor has at least one failure block; every business rule that can be violated in the Normal Flow has a violation block.
- A resume target `Step M` must exist in the Normal Flow.

Worked example, Logout (derived with the walk above):

| Step | Question | Block |
|---|---|---|
| 3 (actor selects Log out) | backs out? | `Step 3_User dismisses the account menu`: the user closes the menu; the system keeps the session; the use case ends |
| 3 | system unreachable when the request is sent? | `Step 3_Server cannot be reached`: the system displays the connection message, keeps the user signed in; the user may retry from Step 3 |
| 4 (system ends the session) | session already gone? | `Step 4_Session already expired`: the system treats the request as completed; the use case continues at Step 5 |
| 4 | termination fails? | optional `Step 4_Session termination fails`: the system keeps the session, displays the error; the user may retry from Step 3 |

Not alternatives: normal steps written as branches, "the user clicks the button again", anything that changes the goal.

Company template mapping: variants and cancellations become `UC-XX-YY.AC.n`, failures become `UC-XX-YY.EX.n` (Trigger = the condition, Response = the lines, Final state = the ending); the derivation walk is the same.

## 6. Consistency checks before delivery

- Role in the Description equals the Primary Actor.
- Every secondary actor appears in at least one flow step; every external call in the flow has its actor.
- No human role appears as secondary actor.
- The UC name, the goal in the Description and the first step describe the same goal.
- Every Normal Flow step starts with a subject; the first one is the primary actor's action.
- Preconditions are facts true before step 1 (made true by an earlier UC or setup); postconditions are verifiable results of success, each produced by a step; the postcondition of one UC feeds the precondition of the next.
- Every alternative flow is anchored to an existing step, shows what the user sees (message id), and ends by resuming at an existing step or ending the use case.
