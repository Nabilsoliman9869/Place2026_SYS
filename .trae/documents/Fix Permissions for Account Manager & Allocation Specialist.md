# Fix Permissions & Sidebar for Account Manager and Allocation Specialist

## 1. Update Permissions (Backend)
*   **File:** `app.py`
*   **Action:** Apply strict Role-Based Access Control (RBAC) to Job Order routes.
*   **Routes:** `manage_requests` and `add_request`.
*   **Allowed Roles:** `Manager`, `AccountManager`, `AllocationSpecialist`, `Corporate`.
*   **Goal:** Ensure only these specific roles can define/receive job orders, as requested.

## 2. Update Sidebar (Frontend)
*   **File:** `templates/base.html`
*   **Action:**
    *   Add "Receive Job Order" link to the **Allocation Specialist** section.
    *   Verify **Account Manager** links are correct and visible.
*   **Goal:** Make the "Receive Job Order" window accessible to Allocation Specialists from their menu.

## 3. Rebuild Application
*   **Action:** Generate a new `PlaceGuideSystem.exe` to reflect the Python code changes.
*   **Goal:** Provide a fresh executable with the fixed permissions.

## Summary of Access Rights (After Fix):
| Feature | Allowed Roles |
| :--- | :--- |
| **Define Corporate Client** | Account Manager, Recruitment Manager, Manager |
| **Receive Job Order** | Account Manager, Allocation Specialist, Manager |
