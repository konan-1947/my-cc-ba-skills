## 2. Use Case Specifications

### 2.2 Lesson Plan

#### 2.2.1 Create Lesson Plan

| **Primary Actors** | Teacher | **Secondary Actors** | AI/LLM Service |
|---|---|---|---|
| **Description** | As a teacher, I want to generate a lesson plan from selected textbook content, so that I can prepare a MOET-5512 lesson efficiently. |
| **Preconditions** | The teacher is signed in.<br>The teacher can select a supported subject, textbook, chapter and lesson (BR-10). |
| **Postconditions** | A lesson plan following MOET Official Dispatch No. 5512/BGDDT-GDTrH is generated (BR-11).<br>The plan is saved to the teacher's Personal Library as Draft (BR-12). |
| **Normal Flow** | **Create Lesson Plan**<br>1. The teacher opens the lesson-plan creation screen.<br>2. The teacher selects the Subject, Grade and Lesson.<br>3. The teacher requests lesson-plan generation.<br>4. The system validates that the selection belongs to the supported KNTT catalog (BR-10).<br>5. The system sends the generation request to the AI/LLM Service.<br>6. The AI/LLM Service returns the generated content.<br>7. The system saves the plan to the Personal Library as Draft. |
| **Alternative Flow** | **Step 4_Required content target is missing**<br>The system highlights the missing selection and does not send an AI request.<br>The system shows MSG02.<br>The teacher may complete the target and retry from Step 3 of the Normal Flow.<br><br>**Step 4_AI/LLM Service is unavailable**<br>The system does not create a lesson plan and displays MSG163.<br>The teacher may retry from Step 3 of the Normal Flow.<br><br>**Step 5_Generation stream fails**<br>The system retains any content already received and displays MSG164.<br>The teacher may retry from Step 3 of the Normal Flow. |
