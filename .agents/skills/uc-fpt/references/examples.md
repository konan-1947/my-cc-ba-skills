# UC examples

## A. Good UC in FPT format (adapted from the `use-case` pharmacy example)

### 2.3.1 Fill Prescription

| **Primary Actors** | Pharmacist | **Secondary Actors** | Drug Interaction Service |
|---|---|---|---|
| **Description** | As a pharmacist, I want to fill a patient prescription, so that the patient receives the correct medication and inventory stays accurate. |
| **Preconditions** | The pharmacist is signed in with an active license.<br>The prescription is in Ready to Fill status.<br>Inventory data was synced within the last 15 minutes. |
| **Postconditions** | The prescription status is Filled.<br>Inventory is decremented by the dispensed quantity.<br>A fill record with pharmacist, timestamp and lot is stored.<br>For a controlled substance, the DEA log is updated (BR-07). |
| **Normal Flow** | **Fill Prescription**<br>1. The pharmacist selects a prescription from the Ready to Fill queue.<br>2. The system displays the prescription details.<br>3. The pharmacist verifies the patient identity.<br>4. The system checks drug interactions against the active medication list.<br>5. The system reports no interactions.<br>6. The pharmacist selects the medication lot.<br>7. The system verifies sufficient inventory (BR-15).<br>8. The pharmacist confirms the fill.<br>9. The system records the fill, decrements inventory and prints the label.<br>10. The pharmacist applies the label and moves the prescription to pickup. |
| **Alternative Flow** | **Step 3_Patient information changed**<br>The pharmacist updates the patient profile and saves.<br>The flow resumes at Step 3 with the updated information.<br><br>**Step 4_Interaction detected**<br>The system shows the warning with its severity (MSG31). For Critical severity the system blocks the fill and requires prescriber authorization.<br>The pharmacist records the authorization code and overrides; the flow resumes at Step 6.<br><br>**Step 7_Insufficient inventory**<br>The system shows available versus prescribed quantity (MSG32).<br>The pharmacist selects Partial Fill; the system creates a back-order for the remainder.<br>The flow resumes at Step 8 with the partial quantity.<br><br>**Step 9_Label printer unavailable**<br>The system stores the fill record and shows MSG33.<br>The pharmacist selects another printer or queues manual printing. The use case ends; the label is deferred. |

Why it works: one named role, 10 steps, variants and failures anchored to real steps, every one has a resume point or end, postconditions are verifiable, rules and messages cited by ID.

## B. Same UC in Company format (shape only)

- **Actor**: Primary: Pharmacist. Secondary: Drug Interaction Service.
- **Priority**: High. **Frequency**: 200-300 per day.
- **Normal Course of Events**: the 10 steps above.
- **Alternative Courses**: `UC-03.AC.1` patient information changed (step 3); `UC-03.AC.2` multiple lots available, choose earliest expiry (step 6).
- **Exceptions**: `UC-03.EX.1` interaction detected (Trigger: step 4 finds an interaction; Response: block Critical, require authorization; Final state: fill continues at step 6 or ends rejected); `UC-03.EX.2` insufficient inventory; `UC-03.EX.3` printer unavailable.
- **Special Requirements / Assumptions**: state rules BR-07, BR-15 in words; interaction check is real-time.

## C. Weak UC (anti-pattern)

```
Use Case: Fill Prescription
Actor: User
1. User opens the system
2. User clicks on prescription
3. User fills it
4. System saves
```

Fails because: generic actor, no pre/postconditions, no trigger, vague steps ("fills it"), no alternatives or exceptions, no rule references, no error handling.

## D. Logout, derived by analysis (subject rule)

| **Primary Actors** | User | **Secondary Actors** | None |
|---|---|---|---|
| **Description** | As a user, I want to log out of my account, so that nobody else can use my session on this device. |
| **Preconditions** | The user is signed in. |
| **Postconditions** | The current session is terminated and the user is on the public landing page. |
| **Normal Flow** | **Logout**<br>1. The user opens the account menu.<br>2. The system displays the available account actions.<br>3. The user selects Log out.<br>4. The system terminates the current user session.<br>5. The system redirects the user to the public landing page. |
| **Alternative Flow** | **Step 3_User dismisses the account menu**<br>The user closes the account menu without selecting an action.<br>The system keeps the current session.<br>The use case ends without logging out.<br><br>**Step 3_Server cannot be reached**<br>The system cannot send the log-out request and displays MSG07.<br>The system keeps the user signed in.<br>The user may retry from Step 3 of the Normal Flow.<br><br>**Step 4_Session already expired**<br>The system treats the request as completed and displays MSG04.<br>The use case continues at Step 5 of the Normal Flow. |

Why it is right: step 1 is the actor's action; every step names its subject; secondary actors are `None` because the session is internal to the product. The alternative flows come from the derivation walk: a cancellation (step 3), a failure with retry (step 3, system unreachable) and a recoverable state difference that rejoins the Normal Flow (step 4); each block is anchored to a step, shows a message and ends with exactly one ending.
