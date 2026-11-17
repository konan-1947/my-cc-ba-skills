# Quality attributes catalog

Source: `Quality Attributes.xlsx` supplied by the user (16 attributes, each with a description, example requirements and, for most, questions to ask). Content marked **(source)** is taken from that file; content marked **(added)** was written by analysis to fill gaps or to turn the examples into patterns. The example requirements come from specific products (a chemical tracking system, an ATM, a text editor...): they are **illustrations of the form, not templates and not text to copy**.

## How to use it for an NFR section

1. For every attribute, ask the *Applies when* question: decide **relevant / not relevant (say why)**. Not every product needs all 16 (a web service rarely needs Installability or Safety).
2. For each relevant attribute, use the **questions** to elicit what matters for *this* product, from the stakeholders, the functional scope and the constraints.
3. Turn each answer into one requirement with the **pattern**: unique id (`CODE-NN`), `shall`, a measurable threshold where the attribute calls for one.
4. Check trade-offs between attributes (for example Performance against Security or Portability) and record the decision.

| Code | Attribute | Vietnamese (source) | Measurable | Applies when (added) |
|---|---|---|---|---|
| AVL | Availability | sẵn sàng | yes | Almost every service that people depend on at set times. |
| INS | Installability | cài đặt | yes | Only for software people install themselves. A web service delivered online usually has none: say so and skip. |
| INT | Integrity | toàn vẹn | partly (backup period, restore time) | Whenever the system stores data people rely on. |
| IOP | Interoperability | tích hợp | partly (named formats, versions, protocols) | Whenever the product exchanges data with other systems or devices. |
| PER | Performance | hiệu năng | yes | Always for operations users wait for. |
| REL | Reliability | tin cậy | yes | When failures cost something (data, money, time). |
| ROB | Robustness | bền vững | yes (time or amount of data) | Whenever input, network, services or users can misbehave: almost always. |
| SAF | Safety | an toàn | yes (threshold of the hazard) | Only products that can injure people or damage property. An office or learning web app normally has none: say so and skip. |
| SEC | Security | bảo mật | partly (limits, intervals) | Always when there are accounts, roles or personal data. |
| USE | Usability | sử dụng | yes | Always for products with human users. |
| EFF | Efficiency | hiệu suất | yes | When capacity is limited or costs scale with usage. |
| MOD | Modifiability | (none in source) | partly (time to change, structural limits) | When the product will evolve (rules, integrations, content, languages): state which changes. |
| POR | Portability | di chuyển | partly (named platforms, versions) | Whenever it must run on more than one environment (browsers, devices, operating systems). |
| REU | Reusability | tái sử dụng | partly (percentage of reuse) | Seldom a user requirement; include only when reuse is a stated goal. |
| SCA | Scalability | mở rộng | yes | When growth is expected. |
| VER | Verifiability | kiểm tra | partly | When testing needs support built into the product or environment. |

## AVL: Availability (sẵn sàng)

**Meaning (source):** is a measure of the planned up time during which the system’s services are available for use and fully operational.

**Questions to ask (source):**
1. What portions of the system are most critical for being available?
2. What are the business consequences of the system being unavailable to its users?
3. If scheduled maintenance must be performed periodically, when should it be scheduled? What is the impact on system availability? What are the minimum and maximum durations of the maintenance periods? How are user access attempts to be managed during the maintenance periods?
4. If maintenance or housekeeping activities must be performed while the system is up, what impact will they have on availability and how can that impact be minimized?
5. What user notifications are necessary if the system becomes unavailable?
6. What portions of the system have more stringent availability requirements than others?
7. What availability dependencies exist between functionality groups (such as not accepting credit card payment for purchases if the credit-card authorization function is not available)?

**Requirement pattern (added):** `The system shall be available at least <X>% of <time window>, measured over <period>[; at least <X'>% during <critical window>].`

**Measurable:** yes. **Applies when:** Almost every service that people depend on at set times.

**Illustrations in the source (specific products; not templates):**
- AVL-1. The system shall be at least 95 percent available on weekdays between 6:00 A.M. and midnight Eastern Time, and at least 99 percent available on weekdays between 3:00 P.M. and 5:00 P.M. Eastern Time.

## INS: Installability (cài đặt)

**Meaning (source):** How easy it is to correctly install, uninstall, and reinstall the application A measure of a system’s installability is the mean time to install the system

**Questions to ask (source):**
1. What installation operations must be performed without disturbing the user’s session?
2. What installation operations will require a restart of the application? Of the computer or device?
3. What should the application do upon successful, or unsuccessful, installation?
4. What operations should be performed to confirm the validity of an installation?
5. Does the user need the capability to install, uninstall, reinstall, or repair just selected portions of the application? If so, which portions?
6. What other applications need to be shut down before performing the installation?
7. What authorization or access privileges does the installer need?
8. How should the system handle an incomplete installation, such as one interrupted by a power failure or aborted by the user?

**Requirement pattern (added):** `A <user type> shall be able to <install / upgrade / uninstall> <product> in at most <T> minutes <without help>; an upgrade shall retain <data/settings>.`

**Measurable:** yes. **Applies when:** Only for software people install themselves. A web service delivered online usually has none: say so and skip.

**Illustrations in the source (specific products; not templates):**
- INS-1. An untrained user shall be able to successfully perform an initial installation of the application in an average of 10 minutes.
- INS-2. When installing an upgraded version of the application, all customizations in the user’s profile shall be retained and converted to the new version’s data format if needed.

## INT: Integrity (toàn vẹn)

**Meaning (source):** Integrity deals with preventing information loss and preserving the correctness of data entered into the system

**Questions to ask (source):**
1. Ensuring that changes in the data are made either entirely or not at all. This might mean backing out of a data change if a failure is encountered partway through the operation.
2. Ensuring the persistence of changes that are made in the data.
3. Coordinating changes made in multiple data stores, particularly when changes have to be made simultaneously (say, on multiple servers) and at a specific time (say, at 12:00 A.M. GMT on January 1 in several locations).
4. Ensuring the physical security of computers and external storage devices.
5. Performing data backups. (At what frequency? Automatically and/or on demand? Of what files or databases? To what media? With or without compression and verification?)
6. Restoring data from a backup.
7. Archiving of data: what data, when to archive, for how long, with what deletion requirements.
8. Protecting data stored or backed up in the cloud from people who aren’t supposed to access it

**Requirement pattern (added):** `The system shall <prevent / log / reject> unauthorized <add / change / delete> of <data>; changes to <data> shall be applied entirely or not at all; <data> shall be backed up every <period> and restorable within <T>.`

**Measurable:** partly (backup period, restore time). **Applies when:** Whenever the system stores data people rely on.

**Illustrations in the source (specific products; not templates):**
- INT-1. The system shall protect against the unauthorized addition, deletion, or modification of data.
- INT-2 The system shall confirm daily that the application executables have not been modified by the addition of unauthorized code.

## IOP: Interoperability (tích hợp)

**Meaning (source):** how readily the system can exchange data and services with other software systems and how easily it can integrate with external hardware devices.

**Questions to ask (source):**
1. To what other systems must this one interface? What services or data must they exchange?
2. What standard data formats are necessary for data that needs to be exchanged with other systems?
3. What specific hardware components must interconnect with the system?
4. What messages or codes must the system receive and process from other systems or devices?
5. What standard communication protocols are necessary to enable interoperability?
6. What externally mandated interoperability requirements must the system satisfy?

**Requirement pattern (added):** `The system shall <import / export / exchange> <data> with <system / device> in <format and version> [using <protocol>].`

**Measurable:** partly (named formats, versions, protocols). **Applies when:** Whenever the product exchanges data with other systems or devices.

**Illustrations in the source (specific products; not templates):**
- IOP-1. The Chemical Tracking System shall be able to import any valid chemical structure from the ChemDraw (version 13.0 or earlier) and MarvinSketch (version 5.0 or earlier) tools.

## PER: Performance (hiệu năng)

**Meaning (source):** Performance represents the responsiveness of the system to various user inquiries and actions

**Questions to ask (added; the source has none for this attribute):**
1. Which operations do users wait for, and how long is acceptable for each?
2. What response time is acceptable under normal load and at peak load?
3. How many concurrent users, requests or data volumes must the response times hold for?
4. Over what network and device conditions must the figures hold?
5. What may degrade, and in which order, when the load exceeds the plan?

**Requirement pattern (added):** `<Operation> shall complete within <T> for <P>% of requests under <load> [on <environment / connection>].`

**Measurable:** yes. **Applies when:** Always for operations users wait for.

**Illustrations in the source (specific products; not templates):**
- PER-1. Authorization of an ATM withdrawal request shall take no more than 2.0 seconds.
- PER-2. Webpages shall fully download in an average of 3 seconds or less over a 30 megabits/second Internet connection

## REL: Reliability (tin cậy)

**Meaning (source):** The probability of the software executing without failure for a specific period of time is known as reliabilitỵ Reliability problems can occur because of improper inputs, errors in the software code itself, components that are not available when needed, and hardware failures

**Questions to ask (source):**
1. How would you judge whether this system was reliable enough?
2. What would be the consequences of experiencing a failure when performing certain operations with the system?
3. What would you consider to be a critical failure, as opposed to a nuisance?
4. Under what conditions could a failure have severe repercussions on your business operations?
5. No one likes to see a system crash, but are there certain parts of the system that absolutely have to be super-reliable?
6. If the system goes down, how long could it stay offline before it significantly affects your business operations?

**Requirement pattern (added):** `The mean time between failures of <component> shall be at least <T>. / <Operation> shall succeed for <P>% of attempts over <period>.`

**Measurable:** yes. **Applies when:** When failures cost something (data, money, time).

**Illustrations in the source (specific products; not templates):**
- REL-2. The mean time between failures of the card reader component shall be at least 90 days.

## ROB: Robustness (bền vững)

**Meaning (source):** How well the system responds to unexpected operating conditions

**Questions to ask (source):**
1. ask users about error conditions the system might encounter and how the system should react.

**Requirement pattern (added):** `If <unexpected condition>, the system shall <recover / degrade / keep working> by <behavior> [within <T> / losing at most <amount of data>].`

**Measurable:** yes (time or amount of data). **Applies when:** Whenever input, network, services or users can misbehave: almost always.

**Illustrations in the source (specific products; not templates):**
- ROB-1. If the text editor fails before the user saves the file, it shall recover the contents of the file being edited as of, at most, one minute prior to the failure the next time the same user launches the application.

## SAF: Safety (an toàn)

**Meaning (source):** Safety requirements deal with the need to prevent a system from doing any injury to people or damage to property

**Questions to ask (source):**
1. Under what conditions could a human be harmed by the use of this product? How can the system detect those conditions? How should it respond?
2. What is the maximum allowed frequency of failures that have the potential to cause injury?
3. What failure modes have the potential of causing harm or property damage?
4. What operator actions have the potential of inadvertently causing harm or property damage?
5. Are there specific modes of operation that pose risks to humans or property?

**Requirement pattern (added):** `If <hazard condition>, the system shall <protective action> and <warn whom>.`

**Measurable:** yes (threshold of the hazard). **Applies when:** Only products that can injure people or damage property. An office or learning web app normally has none: say so and skip.

**Illustrations in the source (specific products; not templates):**
- SAF-2. If the reactor vessel’s temperature is rising faster than 5°C per minute, the Chemical Reactor Control System shall turn off the heat source and signal a warning to the operator.

## SEC: Security (bảo mật)

**Meaning (source):** Security deals with blocking unauthorized access to system functions or data, ensuring that the software is protected from malware attacks, and so on

**Questions to ask (source):**
1. What sensitive data must be protected from unauthorized access?
2. Who is authorized to view sensitive data? Who, specifically, is not authorized?
3. Under what business conditions or operational time frames are authorized users allowed to access functionality?
4. What checks must be performed to confirm that the user is operating the application in a secure environment?
5. How frequently should virus software scan for viruses?
6. Is there a specific user authentication method that must be used?

**Requirement pattern (added):** `The system shall <control> [for <data / role>] [after <N> failed attempts within <T>]. / Only <role> shall be able to <action> <data>.`

**Measurable:** partly (limits, intervals). **Applies when:** Always when there are accounts, roles or personal data.

**Illustrations in the source (specific products; not templates):**
- SEC-1. The system shall lock a user’s account after four consecutive unsuccessful logon attempts within a period of five minutes
- SEC-7. Only users who have Auditor access privileges shall be able to view customer transaction histories

## USE: Usability (sử dụng)

**Meaning (source):** Usability addresses the myriad factors that constitute what people describe colloquially as user-friendliness, ease of use, and human engineering.

**Questions to ask (added; the source has none for this attribute):**
1. Who are the user groups and how experienced are they?
2. Which tasks must be easy, and how quickly must a new user manage them?
3. What accessibility, language or device needs exist?
4. How will usability be judged (task success, time, errors, satisfaction)?

**Requirement pattern (added):** `<P>% of <user group, experience level> shall be able to <task> correctly within <T> [after <orientation>] / with at most <N> errors.`

**Measurable:** yes. **Applies when:** Always for products with human users.

**Illustrations in the source (specific products; not templates):**
- USE-3. 95 percent of chemists who have never used the Chemical Tracking System before shall be able to place a request for a chemical correctly with no more than 15 minutes of orientation.

## EFF: Efficiency (hiệu suất)

**Meaning (added):** How well the system uses computer resources (processor, memory, storage, network) while doing its work.

**Questions to ask (source):**
1. What is the maximum number of concurrent users now and anticipated in the future?
2. By how much could response times or other performance indicators decrease before users or the business suffer adverse consequences?
3. How many operations must the system be able to perform simultaneously under both normal and extreme operating conditions?

**Requirement pattern (added):** `<Resource: CPU / memory / storage / network> use shall not exceed <X>% at <peak load>; the system shall warn <whom> when load exceeds <Y>% of planned capacity.`

**Measurable:** yes. **Applies when:** When capacity is limited or costs scale with usage.

**Illustrations in the source (specific products; not templates):**
- EFF-1. At least 30 percent of the processor capacity and memory available to the application shall be unused at the planned peak load conditions.
- EFF-2. The system shall provide the operator with a warning message when the usage load exceeds 80 percent of the maximum planned capacity.

## MOD: Modifiability

**Meaning (source):** Modifiability addresses how easily the software designs and code can be understood, changed, and extended.

**Questions to ask (added; the source has none for this attribute):**
1. Which changes are expected (rules, content, integrations, languages, roles)?
2. Who makes each change and how fast must it be possible?
3. What must be configurable without code changes?

**Requirement pattern (added):** `A <maintainer role> shall be able to <make change X> in at most <T> [without <side effect>]. / <Code or design constraint, e.g. nesting depth, modular boundaries>.`

**Measurable:** partly (time to change, structural limits). **Applies when:** When the product will evolve (rules, integrations, content, languages): state which changes.

**Illustrations in the source (specific products; not templates):**
- MOD-2. Function calls shall not be nested more than two levels deep
- SUP-1. A certified repair technician shall be able to replace the scanner module in no more than 10 minutes.

## POR: Portability (di chuyển)

**Meaning (source):** Portability goals should identify those portions of the product that must be movable to other environments and describe those target environments

**Questions to ask (source):**
1. What different platforms will this software need to run on, both now and in the future?
2. What portions of the product need to be designed for greater portability than other portions?
3. What data files, program components, or other elements of the system need to be portable?
4. By making the software more portable, what other quality attributes might be compromised?

**Requirement pattern (added):** `The system shall run on <platforms and versions>. / <Data> shall be portable to and from <targets>.`

**Measurable:** partly (named platforms, versions). **Applies when:** Whenever it must run on more than one environment (browsers, devices, operating systems).

**Illustrations in the source (specific products; not templates):**
- POR-2. The user shall be able to port browser bookmarks to and from Firefox, Internet Explorer, Opera, Chrome, and Safari.

## REU: Reusability (tái sử dụng)

**Meaning (source):** Reusable software must be modular, well documented, independent of a specific application and operating environment, and somewhat generic in capability.

**Questions to ask (source):**
1. What existing requirements, models, design components, data, or tests could be reused in this application?
2. What functionality available in related applications might meet certain requirements for this application?
3. What portions of this application offer good potential for being reused elsewhere?
4. What special actions should be taken to facilitate making portions of this application reusable?

**Requirement pattern (added):** `<Component> shall be reusable at <level: source / object code / service> in <context>. / At least <X>% of <artifact> shall be reused from <source>.`

**Measurable:** partly (percentage of reuse). **Applies when:** Seldom a user requirement; include only when reuse is a stated goal.

**Illustrations in the source (specific products; not templates):**
- REU-1. The chemical structure input functions shall be reusable at the object code level in other applications.
- REU-2. At least 30 percent of the application architecture shall be reused from the approved reference architectures

## SCA: Scalability (mở rộng)

**Meaning (source):** Scalability requirements address the ability of the application to grow to accommodate more users, data, servers, geographic locations, transactions, network traffic, searches, and other services without compromising performance or correctness

**Questions to ask (source):**
1. What are your estimates for the number of total and concurrent users the system must be able to handle over the next several months, quarters, or years?
2. Can you describe how and why data capacity demands of the system might grow in the future?
3. What are the minimum acceptable performance criteria that must be satisfied regardless of the number of users?
4. What growth plans are available regarding how many servers, data centers, or individual installations the system might be expected to run on

**Requirement pattern (added):** `The system shall grow from <A> to <B> <users / data / transactions / sites> within <T> [without degrading <performance requirement>].`

**Measurable:** yes. **Applies when:** When growth is expected.

**Illustrations in the source (specific products; not templates):**
- SCA-1. The capacity of the emergency telephone system must be able to be increased from 500 calls per day to 2,500 calls per day within 12 hours.

## VER: Verifiability (kiểm tra)

**Meaning (added):** How easily testers and users can confirm that the software behaves as intended.

**Questions to ask (added; the source has none for this attribute):**
1. How will each requirement be verified (test, inspection, demonstration)?
2. Which test environments, data and access do testers need?
3. What logging or observability must the product provide for testing?

**Requirement pattern (added):** `<Environment> shall be <configured the same as> <test environment>. / A tester shall be able to <configure / observe / log> <what>.`

**Measurable:** partly. **Applies when:** When testing needs support built into the product or environment.

**Illustrations in the source (specific products; not templates):**
- VER-1. The development environment configuration shall be identical to the test configuration environment to avoid irreproducible testing failures.
- VER-2. A tester shall be able to configure which execution results are logged during testing

## Observations on the source file

- Ids use three-letter codes. `INT` here means Integrity; do not reuse `INT` for interfaces.
- The Modifiability row lists `SUP-1` (a supportability example) under it: treat it as an example of maintainability work, not of a separate catalog code.
- Examples number from 1 but skip some ids (REL-2, MOD-2, SEC-7): ids are per-project; number your own requirements from 01 in each attribute.
- Gaps in the source: no description for Efficiency and Verifiability; no questions for Performance, Usability, Modifiability and Verifiability. They were completed by analysis and are marked (added).
