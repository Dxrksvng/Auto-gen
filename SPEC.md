# Assignment 2 — Specification

**Source:** official brief, page 7. The system takes an input file and generates PDF letters requesting additional customer documents. Questions 2.1–2.3 ask for workflow, a two-week operating process with users, and failure prevention/recovery. Page 2 requires the answer in the combined PDF for Assignments 2–4.

**Design objective:** file intake → preflight/schema/row validation → normalized record → business rules → approved template → PDF → output validation → review/release boundary. Generation and sending have separate states.

**Acceptance:** every populated source row has a known result; eligible records create traceable readable PDFs; invalid rows have actionable errors; duplicate and partial rerun behavior is defined; template version and source batch are recorded; business assumptions remain explicit.

**Boundary:** no claim that Sunday's actual approval, dispatch, retention, or technology choices are known. A local POC is optional. Production additions such as authentication, storage, audit records and asynchronous jobs are proposals.
