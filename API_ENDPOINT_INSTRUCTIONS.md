# Donera API Instructions Manual

This manual maps every backend API URL to its purpose and frontend usage.

## Base Rules For Frontend Integration

- Base URL is your backend host, for example http://localhost:8000.
- JSON endpoints use application/json unless the endpoint explicitly requires multipart/form-data.
- For protected endpoints, send Authorization header as:
  - Authorization: Bearer <access_token>
- Token refresh endpoint is public and uses the refresh token in request body.
- Response lists are plain arrays for DRF ListAPIView endpoints in this project.

## Category Reference

All causes are assigned to one of 14 standard categories. When creating or updating causes, use the category **ID** (integer), not the name or slug.

### Standard Categories (Always Use These IDs: 0-13)

| ID | Category Name |
|-------|-------|
| 0 | Health |
| 1 | Education |
| 2 | Water & Sanitation |
| 3 | Food Security |
| 4 | Livelihood |
| 5 | Disaster Relief |
| 6 | Community Development |
| 7 | Child Welfare & Protection |
| 8 | Environmental Conservation |
| 9 | Women & Girls' Empowerment |
| 10 | Disability Support & Inclusion |
| 11 | Human Rights & Advocacy |
| 12 | Sports & Culture |
| 13 | Other |

### Using Categories in Requests

**When Creating a Cause:**
```json
{
  "title": "Clean Water Initiative",
  "description": "...",
  "category": 2,
  "target_amount": "10000.00"
}
```

**When Setting User Interests (for Recommendations):**
```json
{
  "interests": [0, 1, 2]
}
```

**In Responses:**
```json
{
  "id": 42,
  "title": "My Cause",
  "category": 2,
  "organization": {...}
}
```

### Important Notes
- Always send `category` as an **integer ID** (0-13), never as a name or slug.
- The `category` field is **required** when creating a cause.
- Category IDs range from **0 to 13** (14 total categories).
- Category IDs are immutable and consistent across all environments.
- Frontend should hardcode or cache these mappings at app startup.

### Recommended Frontend Implementation

1. Store category mappings at app boot:
   ```javascript
   const CATEGORIES = {
     0: "Health",
     1: "Education",
     2: "Water & Sanitation",
     3: "Food Security",
     4: "Livelihood",
     5: "Disaster Relief",
     6: "Community Development",
     7: "Child Welfare & Protection",
     8: "Environmental Conservation",
     9: "Women & Girls' Empowerment",
     10: "Disability Support & Inclusion",
     11: "Human Rights & Advocacy",
     12: "Sports & Culture",
     13: "Other"
   };
   ```

2. Create dropdown/select using this mapping

3. When submitting cause creation, send the selected ID integer (0-13)

4. When displaying a cause, fetch the category ID from response and look up display name

## Auth Endpoints

### POST /api/users/register/
- Purpose: Create a new user account (donor or organization).
- Auth: Public.
- Request body:
  - username
  - email
  - password
  - first_name (optional)
  - last_name (optional)
  - phone_number (optional)
  - role (optional): Pass "DONOR" or "ORGANIZATION". If omitted, defaults to "DONOR". Once registered, role cannot be changed.
- Frontend extraction:
  - Use response status to determine registration success.
  - Extract user role from response to branch signup flow (donors skip org onboarding, org users see org registration form).
  - If validation fails, show field-level error messages from response body.

### POST /api/users/login/
- Purpose: User login (JWT pair).
- Auth: Public.
- Request body:
  - email
  - password
- Response includes:
  - access: JWT access token for Bearer authorization
  - refresh: JWT refresh token for token refresh endpoint
  - user: User object containing id, email, username, role, and has_organization flag
- Frontend extraction:
  - Read access and refresh tokens and store for Authorization header and refresh flow.
  - Read user.role (DONOR, ORGANIZATION, or ADMIN) to branch UI:
    - DONOR: show donor homepage
    - ORGANIZATION: check user.has_organization to branch:
      - false: show org onboarding flow (POST /api/organizations/register/)
      - true: show org dashboard
    - ADMIN: show admin dashboard
  - Store has_organization flag to skip org registration screen if already complete.

### POST /api/users/token/refresh/
- Purpose: Exchange refresh token for new access token.
- Auth: Public.
- Request body:
  - refresh
- Frontend extraction:
  - Replace stored access token with the new one.
  - On refresh failure, clear auth state and force login.

### GET /api/users/me/
- Purpose: Fetch current user profile and role.
- Auth: Bearer token.
- Frontend extraction:
  - Read role to branch UI: DONOR, ORGANIZATION, ADMIN.
  - Useful fields:
    - id
    - email
    - full_name
    - role
    - phone_number

### PATCH /api/users/me/
- Purpose: Update current user profile.
- Auth: Bearer token.
- Request body: Any writable UserSerializer fields.
- Frontend extraction:
  - Refresh local profile state from returned object.

## Admin Organization Endpoints

### GET /api/admin/organizations/stats/
- Purpose: Single aggregated payload for admin dashboard cards.
- Auth: Admin only.
- Response keys:
  - pending_verifications
  - total_verified_orgs
  - active_causes
  - total_platform_volume
- Frontend extraction:
  - Use this endpoint for top summary widgets instead of multiple calls.
  - total_platform_volume is now computed from the Donation table in the database.

### GET /api/admin/organizations/pending/
- Purpose: Organization verification queue.
- Auth: Admin only.
- Frontend extraction:
  - Render table/list of organizations awaiting review.
  - Primary field: verification_status should be PENDING.

### GET /api/admin/organizations/all/
- Purpose: Fetch all registered organizations for admin dashboard listing.
- Auth: Admin only.
- Response includes per-organization metrics:
  - causes_count
  - active_causes_count
  - total_amount_raised
- Frontend extraction:
  - Use this endpoint for the full organizations table in admin dashboard.
  - Includes organizations regardless of verification_status (PENDING, APPROVED, REJECTED).

### PATCH /api/admin/organizations/:id/verify/
- Purpose: Approve or reject an organization.
- Auth: Admin only.
- Request body:
  - verification_status: APPROVED or REJECTED
- Frontend extraction:
  - Update row/status from returned organization object.
  - Remove item from pending list after successful review.

## Admin Cause Endpoints

### GET /api/admin/causes/
- Purpose: Admin-wide cause listing across the platform.
- Auth: Admin only.
- Optional query params:
  - status=active|paused|completed
- Frontend extraction:
  - For active totals, use either:
    - count where status is ACTIVE from returned list, or
    - /api/admin/organizations/stats/ active_causes.

## Organization Endpoints

### POST /api/organizations/register/
- Purpose: Organization onboarding/profile creation.
- Auth: Organization user.
- Request body:
  - name
  - description
  - registration_number
  - kra_pin
  - tcc_number
  - tcc_document (file)
  - payout_method
  - payout_bank_name (conditional)
  - payout_shortcode (conditional)
  - payout_account_number (conditional)
  - contact_email
  - contact_phone
  - physical_address
- Frontend extraction:
  - Use returned object as source of truth for profile state.

### GET /api/organizations/me/
- Purpose: Fetch current user organization profile.
- Auth: Organization user.
- Frontend extraction:
  - Prefill settings/profile forms.
  - If 404 with detail message, show onboarding prompt.

### PATCH /api/organizations/me/
- Purpose: Update organization profile/settings.
- Auth: Organization user.
- Frontend extraction:
  - Replace local organization state with returned object.

### GET /api/organizations/approved/
- Purpose: Public list of approved organizations.
- Auth: Public.
- Frontend extraction:
  - Use for donor trust sections or organization selectors.

## Causes Endpoints

### GET /api/causes/feed/
- Purpose: Cause feed endpoint.
- Auth: Public or Bearer.
- Behavior:
  - Public/Donor users: returns ACTIVE causes from APPROVED organizations.
  - Organization users: returns causes owned by authenticated organization.
- Optional query params:
  - status=active|paused|completed (applies to organization-owned view)
- Frontend extraction:
  - Donor homepage uses this as public feed.
  - Org dashboard can reuse this endpoint to list own causes.

### GET /api/causes/
- Purpose: Alias of cause feed/list behavior.
- Auth and behavior: same as /api/causes/feed/.
- Frontend extraction:
  - Supports hardcoded usage like /api/causes?status=active.

### POST /api/causes/create/
- Purpose: Create a cause.
- Auth: Organization user with approved organization.
- Request body:
  - title
  - description
  - cover_image (optional file)
  - category
  - status (optional, defaults ACTIVE)
  - target_amount
  - start_date (optional)
  - end_date (optional)
- Frontend extraction:
  - Use returned cause object to update list immediately.

### GET /api/causes/:id/
- Purpose: Public cause detail.
- Auth: Public.
- Frontend extraction:
  - Read full cause fields.
  - organization object includes:
    - id
    - name
    - verification_status

### GET /api/causes/:id/manage/
- Purpose: Organization-side cause detail for edit prefill.
- Auth: Organization user who owns cause.
- Frontend extraction:
  - Prefill edit form with response body.

### PATCH /api/causes/:id/manage/
- Purpose: Update owned cause.
- Auth: Organization user who owns cause.
- Frontend extraction:
  - Replace updated cause in local state with response body.

### GET /api/causes/recommended/
- Purpose: AI-powered personalized cause recommendations for authenticated users.
- Auth: Bearer token (Donor users only).
- Behavior:
  - Returns causes ranked by TF-IDF similarity to user's interests and donation history.
  - User interests are weighted 1x; recent donation categories are weighted 2x.
  - Falls back to newest active causes if no interests/donation history exists.
- Optional query params:
  - limit=5 (default, returns top N causes)
- Frontend extraction:
  - Use for "Recommended For You" section on donor homepage.
  - Causes are pre-ranked (order matters); display as-is without secondary sorting.
  - Same cause schema as /api/causes/ endpoint.

### GET /api/causes/:id/reports/
- Purpose: Published reports for a specific cause.
- Auth: Public.
- Frontend extraction:
  - Render timeline/list of reports related to a cause.

## Reports Endpoints

### POST /api/reports/
- Purpose: Submit a report.
- Auth: Organization user with approved organization and ownership of target cause.
- Content type: multipart/form-data supported for evidence uploads.
- Request body:
  - cause
  - funds_utilized
  - expense_category
  - content
  - evidence (optional file)
  - status
- Frontend extraction:
  - Use returned report object to confirm save.

### POST /api/reports/create/
- Purpose: Alias of report creation endpoint.
- Auth and behavior: same as POST /api/reports/.

### GET /api/reports/feed/
- Purpose: Public feed of published reports.
- Auth: Public.
- Frontend extraction:
  - Build global reports feed using returned array.

### GET /api/reports/:id/
- Purpose: Organization report detail for retrieve/update flow.
- Auth: Authenticated user.
- Frontend extraction:
  - Intended for report management screens.

### PATCH /api/reports/:id/
- Purpose: Update a report in management flow.
- Auth: Authenticated user.
- Frontend extraction:
  - Update local report state from returned payload.

## Dashboard Endpoint

### GET /api/dashboard/organization/me/
- Purpose: Organization analytics overview card data.
- Auth: Organization user.
- Response shape:
  - overview.total_funds_raised
  - overview.active_causes
  - overview.total_donors
  - overview.pending_reports
  - alerts
- Frontend extraction:
  - Bind dashboard metrics directly from overview object.

## Donation And Payment Endpoints

### POST /payments/initiate/
- Purpose: Frontend donation initiation endpoint currently aligned to payment-style routes.
- Auth: Bearer token.
- Request body:
  - cause_id
  - amount
  - phone_number
- Frontend extraction:
  - Read CheckoutRequestID.
  - Start polling /payments/status/?checkout_id=<CheckoutRequestID>.

### GET /payments/status/?checkout_id=...
- Purpose: Poll payment status by checkout id.
- Auth: Bearer token.
- Frontend extraction:
  - Read status.
  - Terminal success condition: status equals SUCCESS.
  - Handle not found as failed/expired checkout state.

### POST /api/donations/initiate/
- Purpose: API-prefixed alias for initiating donation.
- Auth and behavior: same as /payments/initiate/.

### GET /api/donations/status/?checkout_id=...
- Purpose: API-prefixed alias for donation status polling.
- Auth and behavior: same as /payments/status/.

### GET /api/donations/status/:checkout_request_id/
- Purpose: Path-param status lookup alternative.
- Auth: Bearer token.
- Frontend extraction:
  - Same response keys as query-param form.

### POST /api/donations/webhook/
- Purpose: Payment provider callback receiver.
- Auth: Public (provider side).
- Frontend extraction:
  - Not called by browser frontend.

### GET /api/donations/history/
- Purpose: Donor donation history.
- Auth: Bearer token.
- Frontend extraction:
  - Render donations list for current user profile/history page.

### GET /api/donations/dashboard/
- Purpose: Organization donation list for dashboard context.
- Auth: Bearer token.
- Frontend extraction:
  - Use for org donations table and recent donation widgets.

## Suggested Frontend Data-Loading Strategy

- App boot:
  - GET /api/users/me/ to identify role and has_organization flag.
  - Cache category ID → name mapping (IDs 0-13).
- User signup flow:
  - POST /api/users/register/ with role parameter.
  - On response, check user.role:
    - DONOR: skip to login.
    - ORGANIZATION: proceed to org onboarding form (POST /api/organizations/register/).
    - ADMIN: skip to admin dashboard.
- Donor home:
  - GET /api/causes/feed/ for cause feed.
  - GET /api/causes/recommended/ for personalized recommendations.
  - GET /api/reports/feed/ for reports feed.
- Donation checkout:
  - POST /payments/initiate/ with cause_id and amount.
  - Poll GET /payments/status/?checkout_id=... until terminal state.
- Organization home:
  - Check login response has_organization flag:
    - false: show org onboarding form (POST /api/organizations/register/).
    - true: show org dashboard.
  - GET /api/dashboard/organization/me/ for analytics.
  - GET /api/causes/feed/ for own causes list.
- Admin home:
  - GET /api/admin/organizations/stats/ for summary cards.
  - GET /api/admin/organizations/pending/ for verification queue.
  - GET /api/admin/organizations/all/ for org table.
  - GET /api/admin/causes/?status=active for cause table.

## Error Handling Recommendations

- Treat 401 as expired access token and trigger refresh flow.
- Treat refresh failure as full logout.
- Treat 403 as role/permission mismatch and show access denied UI.
- Treat 404 for /api/organizations/me/ as not onboarded organization.
- For validation errors, map response field keys to form inputs directly.
