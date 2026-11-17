## 4. Non-Functional Requirements

This section defines the measurable quality requirements of the sample platform, Release 1.0: availability, performance, reliability, robustness, security, integrity and usability. Unless a requirement states otherwise, it applies to all roles and to all supported browsers. Attributes that do not apply are declared with the reason. External interfaces are described in the functional requirements.

### 4.1 Availability

AVL-01: The system shall be available at least 99% of each calendar month, measured over 30 days.

### 4.2 Performance

PER-01: Opening the class list shall complete within 2 seconds for 95% of requests with 200 concurrent users.

### 4.3 Reliability

REL-01: Saving a document shall succeed for at least 99.5% of attempts over 30 days.

### 4.4 Robustness

ROB-01: If the connection drops while a document is edited, the system shall recover the content as of at most 60 seconds earlier at the next sign-in.

### 4.5 Security

SEC-01: A user shall access only the classes permitted for their role and ownership, verified on every request.

### 4.6 Integrity

INT-01: The system shall keep the last valid version of a document when a change fails.

### 4.7 Usability

USE-01: 90% of new teachers shall create a lesson plan correctly within 15 minutes after a 10-minute orientation.

### 4.8 Not applicable

SAF: Not applicable - the product cannot cause physical harm.
INS: Not applicable - the product is delivered as an online service.
