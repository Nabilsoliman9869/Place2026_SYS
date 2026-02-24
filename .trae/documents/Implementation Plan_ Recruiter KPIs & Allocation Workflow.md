# Recruiter Workflow & Allocation Logic Implementation Plan

## 1. Recruiter Dashboard & KPIs
**Goal:** Provide clear visibility of candidate pipeline status to Recruiters and Managers.
*   **KPIs:**
    *   Total Registered Candidates
    *   In-Progress (Scheduled for Talent Test)
    *   Passed Test (Ready for Matching)
    *   Failed Test (Needs Training/Rejected)
    *   Rejected/Disqualified
*   **View:**
    *   **Recruiter:** Sees their own stats only.
    *   **Manager:** Can filter stats by specific Recruiter or view "All".

## 2. Allocation & Matching (The "Sync" Button)
**Goal:** Match "Ready" candidates to "Open" Job Orders based on criteria (CEFR, etc.).
*   **Actor:** Allocation Specialist / Allocator.
*   **Action:** Click "Sync Candidates".
*   **Logic:**
    *   Fetch all Candidates with Status `Ready_For_Matching`.
    *   Fetch all Open Job Orders (Client Requests).
    *   Compare: Candidate CEFR >= Job Required CEFR.
    *   **Output:** A "Proposed Match" list.
*   **Review Step:** Allocator reviews matches, checks missing data (Age, etc.), and "Approves" the match to move it to "Client Interview".

## 3. Client Interview Scheduling Cycle
**Goal:** Coordinate interviews between Client, Allocator, and Recruiter.
*   **Step 1 (Allocator):** Sets Interview Date/Time for approved matches.
*   **Step 2 (System):** Notifies the *Original Recruiter*.
*   **Step 3 (Recruiter):** Sees "To Notify" list. Contacts candidate. Marks as "Candidate Informed".
*   **Step 4 (Follow-up):** Daily Agenda for Recruiter shows today's interviews to confirm attendance.
*   **Step 5 (Result):** Allocator records Client Result (Pass/Fail).
    *   **Pass:** Schedule 2nd Interview (if any) or Request Documents.
    *   **Fail:** Record Reason.
*   **Step 6 (Recruiter):** Notified of result. Contacts candidate for next steps (Docs/2nd Interview).

## 4. Onboarding & Billing
**Goal:** Finalize hiring and trigger invoicing.
*   **Action:** Recruiter confirms "Offer Accepted" & "Work Started".
*   **System:** Updates status to `Hired`.
*   **Visibility:** Account Manager sees `Hired` candidates to issue Invoice.

## Immediate Next Steps
1.  **Verify** Talent Context & Drive Link fixes (Already implemented, just needs confirmation).
2.  **Implement** Recruiter Dashboard KPIs.
3.  **Build** Allocation Matching View ("Sync" Logic).
