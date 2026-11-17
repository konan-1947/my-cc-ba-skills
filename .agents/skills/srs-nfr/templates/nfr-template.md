## 4. Non-Functional Requirements

This section defines the measurable quality requirements of <product> Release <x.y>: <list the quality attributes that apply>. Unless a requirement states otherwise, it applies to all roles and to all supported browsers/devices. Attributes that do not apply are declared with the reason. External interfaces are described in the functional requirements, not here.

### 4.1 Availability
AVL-01: The system shall be available at least <X>% of <time window>, measured over <period>.

### 4.2 Performance
PER-01: <Operation> shall complete within <T> seconds for <P>% of requests under <load>.

### 4.3 Reliability
REL-01: <Operation> shall succeed for at least <P>% of attempts over <period>.

### 4.4 Robustness
ROB-01: If <unexpected condition>, the system shall <recover / degrade> by <behavior> within <T> minutes, losing at most <amount of data>.

### 4.5 Security
SEC-01: A user shall access only the <data / functions> permitted for their <role / ownership>, verified on every request.

### 4.6 Integrity
INT-01: The system shall apply a change to <data> entirely or not at all, and shall keep the last valid version when a change fails.

### 4.7 Usability
USE-01: <P>% of <user group> with <experience> shall be able to <task> correctly within <T> minutes after <orientation>.

### 4.8 Scalability
SCA-01: The system shall support growth from <A> to <B> <users / records / transactions> within <T> without degrading PER-01.

### 4.9 Interoperability
IOP-01: The system shall <import / export / exchange> <data> with <system> in <format and version>.

### 4.10 Not applicable
SAF: Not applicable - <reason, for example the product cannot cause physical harm>.
INS: Not applicable - <reason, for example the product is delivered as an online service>.

<!-- Rules
- Sub-sections follow the catalog in references/quality-attributes.md; keep only the attributes that apply, renumber 4.x, and declare the rest in "Not applicable" with a reason.
- One requirement per id: CODE-NN, "shall", one verifiable obligation, a number with a unit where the attribute needs one (AVL, PER, REL, ROB, SCA, SAF as errors; INS, EFF, USE as warnings).
- Do not write external-interface requirements here (no INT-UI / INT-SW); the need for data exchange is Interoperability (IOP).
- Placeholders in angle brackets are filled by analysis of the product using the catalog's questions, never copied from an example.
-->
