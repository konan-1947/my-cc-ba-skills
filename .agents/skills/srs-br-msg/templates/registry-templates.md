# Register templates (SRS section 5)

Keep each register in its own file (`br-registry.md`, `msg-registry.md`) so `scripts/check-refs.py` can read it.

## 5.1 Business Rules

| ID | Rule Definition |
|---|---|
| BR-01 | <one rule, one sentence, testable: who may / must / may not do what, under which condition> |
| BR-02 | ... |

Rules from the EDUA sample (style reference):
- BR-04 Each subject may have only one active Moderator at a time.
- BR-08 A Moderator appointment cannot be removed until a replacement has been assigned.
- BR-17 A student may submit a class-resource response after its deadline; the system accepts it and tags it Late instead of blocking it.

## 5.2 System Messages

| # | Message code | Message Type | Context | Content |
|---|---|---|---|---|
| 1 | MSG01 | Inline | No search/listing result is found | <UI text> |
| 2 | MSG02 | Inline, in red under the field | A required input field is empty | <UI text> |
| 164 | MSG164 | Toast (error) | Regenerate lesson-plan section fails | <UI text> |
| 14 | MSG14 | Button state | AI is generating a lesson plan | <UI text> |

- `#` equals the numeric part of the code.
- **Message Type** starts with one of: Inline, Toast (and Toast (error)), Popup, Confirmation popup, Dialog, Banner, Button state, Status label, Email, Notification; placement may follow ("Inline, in red under the field").
- **Context** states the trigger in the third person, matching the UC step or alternative flow that cites it.
- **Content** is the exact UI text in the product language (the EDUA SRS keeps Vietnamese UI text in an English document); placeholders in brackets: `[email]`.
