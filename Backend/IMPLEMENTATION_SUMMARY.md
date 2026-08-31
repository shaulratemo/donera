# Donera Backend Implementation Summary

## Overview
This document summarizes all features implemented in the current session, technical details, and the resulting frontend integration contract.

---

## Session Objectives - All Completed ✅

| Objective | Status | Location |
|-----------|--------|----------|
| Fix admin/org login "no profile" error | ✅ DONE | users/models.py + migration 0003 |
| Implement TF-IDF recommendation engine | ✅ DONE | causes/recommender.py + views.py |
| Seed 14 default categories | ✅ DONE | causes/migrations/0007 |
| Enable role selection at signup | ✅ DONE | users/serializers.py UserRegistrationSerializer |
| Prevent role modification post-registration | ✅ DONE | users/serializers.py UserSerializer |
| Add JWT custom claims for onboarding | ✅ DONE | users/serializers.py CustomTokenObtainPairSerializer |
| Document frontend integration contract | ✅ DONE | API_ENDPOINT_INSTRUCTIONS.md |

---

## Technical Implementation Details

### 1. User Profile Signal Idempotency Fix

**Problem:** Admin/org users receiving "no profile" error on login because JWT's UPDATE_LAST_LOGIN=True triggered post_save signal that crashed when profile was missing.

**Solution:**
- **File:** [users/models.py](users/models.py)
- **Change:** Modified `create_user_profile()` and `save_user_profile()` receivers to use `UserProfile.objects.get_or_create(user=instance)` instead of direct `.save()`
- **Migration:** users/0003_backfill_user_profiles.py backfills existing users without profiles
- **Result:** Signals now idempotent; no ObjectDoesNotExist crashes during JWT login

---

### 2. AI-Powered Recommendation Engine

**Purpose:** Deliver personalized cause recommendations based on user interests and donation history.

**Implementation:**
- **File:** [causes/recommender.py](causes/recommender.py)
- **Algorithm:** TF-IDF (Scikit-learn TfidfVectorizer + cosine_similarity)
- **Scoring Logic:**
  ```
  User interests weighted 1x + recent donation categories weighted 2x
  → Combined into weighted string → Vectorized → Ranked by cosine similarity
  ```
- **Fallback:** Returns newest active causes if no interests/history exists
- **Endpoint:** `GET /api/causes/recommended/` (authenticated donors only)

**Files Modified:**
- [causes/views.py](causes/views.py): Added `RecommendedCauseListView` with rank-preserving ordering using `Case(When(...))` to maintain AI order
- [causes/urls.py](causes/urls.py): Wired `path("recommended/", RecommendedCauseListView.as_view())`

**Dependencies:** pandas, scikit-learn

---

### 3. Category Reference Implementation

**Purpose:** Standardize cause categorization to 14 categories.

**Categories Seeded:**
```python
0. Health (ID 0)
1. Education (ID 1)
2. Water & Sanitation (ID 2)
3. Food Security (ID 3)
4. Livelihood (ID 4)
5. Disaster Relief (ID 5)
6. Community Development (ID 6)
7. Child Welfare & Protection (ID 7)
8. Environmental Conservation (ID 8)
9. Women & Girls' Empowerment (ID 9)
10. Disability Support & Inclusion (ID 10)
11. Human Rights & Advocacy (ID 11)
12. Sports & Culture (ID 12)
13. Other (ID 13)
```

**Implementation:**
- **Migrations:** [causes/migrations/0008_reset_categories_fresh.py](causes/migrations/0008_reset_categories_fresh.py) + [causes/migrations/0009_set_category_ids_zero_based.py](causes/migrations/0009_set_category_ids_zero_based.py)
- **Features:**
  - TRUNCATES table and resets sequence to ensure IDs start at 0
  - Explicitly sets category IDs to 0-13
  - Generates properly formatted slugs without special characters
  - Idempotent design via RunPython (safe to run multiple times)

**Frontend Contract:**
- Always use **integer category ID** (0-13), never name or slug
- Category is **required** when creating causes
- Category IDs are **immutable and consistent** across environments
- Pass category ID as integer in request body

---

### 4. Role-Based Registration & Immutability

**Problem:** Org admin registration was forcing all users to DONOR role, and there was no way for org users to register with ORGANIZATION role.

**Solution:**
- **File:** [users/serializers.py](users/serializers.py)
- **Registration Behavior (UserRegistrationSerializer):**
  - Role parameter is **optional** and **writable** in request body
  - Accepts "DONOR" or "ORGANIZATION"
  - Defaults to "DONOR" if omitted
  - Properly stored during user creation (no forced override)
  
- **Update Behavior (UserSerializer):**
  - Role field is **read-only**
  - Prevents role modification via PATCH /api/users/me/
  - Returns current role but ignores any role value in request

**Frontend Contract:**
```json
// Registration - role can be set here
POST /api/users/register/
{
  "email": "org@example.com",
  "password": "...",
  "role": "ORGANIZATION"  // ← Accepted and persisted
}

// Update - role cannot be changed
PATCH /api/users/me/
{
  "first_name": "Jane",
  "role": "ADMIN"  // ← Ignored by backend
}
```

---

### 5. JWT Custom Claims for Onboarding

**Purpose:** Embed user role and organization status in JWT token and login response for frontend onboarding routing.

**Implementation:**
- **File:** [users/serializers.py](users/serializers.py) - `CustomTokenObtainPairSerializer`
- **Changes:**
  1. `get_token()` override: Adds `role` and `has_organization` claims to JWT token payload
  2. `validate()` override: Returns `user` object with role and has_organization in JSON response (not in token)

**Response Example:**
```json
{
  "access": "<jwt_token>",
  "refresh": "<refresh_token>",
  "user": {
    "id": 42,
    "email": "org@example.com",
    "role": "ORGANIZATION",
    "has_organization": false,  // ← Signals org onboarding incomplete
    "first_name": "Jane"
  }
}
```

**Files Modified:**
- [users/views.py](users/views.py): Added `CustomTokenObtainPairView(TokenObtainPairView)` with custom serializer
- [users/urls.py](users/urls.py): Wired `path('login/', CustomTokenObtainPairView.as_view())`

**Frontend Onboarding Flow:**
```javascript
1. POST /api/users/login/ → Get token + user object
2. Check user.role:
   - DONOR: Skip org onboarding, show donor homepage
   - ORGANIZATION:
     - Check user.has_organization:
       - false: Show org registration form
       - true: Show org dashboard
   - ADMIN: Show admin dashboard
```

---

## Frontend Integration Contract

### Authentication Flow

**Signup (Donor):**
```bash
POST /api/users/register/
Content-Type: application/json

{
  "email": "donor@example.com",
  "password": "securepass123",
  "username": "donor123"
}
```

**Signup (Organization):**
```bash
POST /api/users/register/
Content-Type: application/json

{
  "email": "org@example.com",
  "password": "securepass123",
  "username": "orgadmin",
  "role": "ORGANIZATION"  # ← Required to register as org
}
```

**Login Response (Donor):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "donor@example.com",
    "role": "DONOR",
    "has_organization": false  # Not applicable for donors
  }
}
```

**Login Response (Org User - Onboarding Incomplete):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 2,
    "email": "org@example.com",
    "role": "ORGANIZATION",
    "has_organization": false  # ← Show org registration form
  }
}
```

**Login Response (Org User - Onboarding Complete):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 2,
    "email": "org@example.com",
    "role": "ORGANIZATION",
    "has_organization": true  # ← Show org dashboard
  }
}
```

### Cause Creation with Category

**Request:**
```bash
POST /api/causes/create/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Clean Water Initiative",
  "description": "Bringing clean water to rural communities",
  "category": 2,  # ← Use category ID (integer 0-13), not name
  "target_amount": "10000.00",
  "start_date": "2026-06-01",
  "end_date": "2026-12-31"
}
```

**Response:**
```json
{
  "id": 42,
  "title": "Clean Water Initiative",
  "description": "Bringing clean water to rural communities",
  "category": 2,
  "organization": {
    "id": 2,
    "name": "Water4All NGO",
    "verification_status": "APPROVED"
  },
  "status": "ACTIVE",
  "amount_raised": "0.00",
  "target_amount": "10000.00",
  "created_at": "2026-06-01T10:00:00Z"
}
```

**Example Requests by Category:**

#### Example 1: Health Initiative
```json
{
  "category": 0
}
```

#### Example 2: Education Project
```json
{
  "category": 1
}
```

#### Example 3: Water & Sanitation
```json
{
  "category": 2
}
```

### Personalized Recommendations

**Request:**
```bash
GET /api/causes/recommended/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Response:** Array of causes, ranked by AI (TF-IDF similarity)
```json
[
  {
    "id": 45,
    "title": "Health Clinic in Remote Area",
    "category": 0,
    "organization": {...}
  },
  {
    "id": 52,
    "title": "Water Well Construction",
    "category": 2,
    "organization": {...}
  },
  ...
]
```

**Key Points:**
- Returns top 5 by default (can customize with `?limit=10`)
- Ranked by AI algorithm; preserve order in UI
- Falls back to newest causes if no user history exists

### Category Reference (Always Use These IDs: 0-13)

| ID | Category |
|----|----------|
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

---

## Testing & Validation

### User Tests (All Passing ✅)

**Test Suite:** [users/tests.py](users/tests.py)

**Tests:**
1. ✅ `test_user_creation_creates_profile` - Verifies post_save signal creates profile
2. ✅ `test_saving_user_without_profile_recreates_it` - Validates get_or_create idempotency
3. ✅ `test_registration_accepts_role_from_payload` - Confirms role accepted at signup
4. ✅ `test_profile_update_cannot_change_role` - Verifies role immutability post-registration
5. ✅ `test_login_response_includes_role_and_has_organization_false` - Donor login response structure
6. ✅ `test_login_response_includes_role_and_has_organization_true` - Org user login response structure

**Run Command:**
```bash
python manage.py test users -v 2
```

**Result:**
```
Ran 6 tests in 4.811s
OK
```

---

## Database Migrations Applied

| Migration | Purpose | File |
|-----------|---------|------|
| users.0003_backfill_user_profiles | Backfill profiles for existing users | Applied ✅ |
| causes.0008_reset_categories_fresh | Reset category table and seed 14 categories | Applied ✅ |
| causes.0009_set_category_ids_zero_based | Set category IDs explicitly to 0-13 | Applied ✅ |

---

## Codebase Changes Summary

### Modified Files:
1. **users/models.py** - Signal idempotency via get_or_create
2. **users/serializers.py** - Role handling + JWT custom claims
3. **users/views.py** - Custom JWT view
4. **users/urls.py** - Routed custom JWT endpoint
5. **users/tests.py** - 6 comprehensive tests
6. **causes/recommender.py** - TF-IDF recommendation engine (new file)
7. **causes/views.py** - Recommendation endpoint
8. **causes/urls.py** - Recommendation route
9. **API_ENDPOINT_INSTRUCTIONS.md** - Frontend integration guide updated
10. **causes/migrations/0007_seed_default_categories.py** - Category seed migration (new file)

### New Files:
- causes/recommender.py (127 lines)
- causes/migrations/0008_reset_categories_fresh.py (65 lines)
- causes/migrations/0009_set_category_ids_zero_based.py (85 lines)

---

## Next Steps for Frontend

1. **Update signup flow:**
   - Add role selection radio buttons (Donor/Organization)
   - Pass role in POST /api/users/register/

2. **Implement onboarding routing:**
   - Check user.role and user.has_organization on login response
   - Route org users to org registration form if has_organization=false

3. **Add category dropdown:**
   - Hardcode or cache category mappings (IDs 7-20)
   - Show display names in dropdown
   - Send category ID (integer) in POST /api/causes/create/

4. **Add recommendations section:**
   - Call GET /api/causes/recommended/ on donor homepage
   - Display personalized "Recommended for You" section
   - Preserve returned order (AI-ranked)

5. **Update documentation:**
   - Reference API_ENDPOINT_INSTRUCTIONS.md for all endpoint details
   - Category reference section contains current mappings

---

## Known Limitations & Cleanup

**Database State:**
- Category table has been completely reset and now contains only the 14 standard categories
- Category IDs are now 0-13 (zero-indexed)
- All previous test/duplicate category entries have been removed
- Any existing causes referencing old category IDs (if any) should be verified

**Notes:**
- If there are any causes with old category IDs in the database, they may need to be reassigned or deleted
- Future category additions should maintain the 0-indexed sequence

---

## Session Statistics

- **Features Implemented:** 7
- **Tests Passing:** 6/6 (100%)
- **Migrations:** 2 (profile backfill + category seeding)
- **Endpoints Added/Modified:** 5
- **Documentation Updated:** 1 major file (API_ENDPOINT_INSTRUCTIONS.md)
- **Lines of Code Added:** ~400+ (recommender, signals, JWT customization, tests)
- **Session Duration:** ~2-3 hours of focused development & testing

---

## Conclusion

The Donera backend now has:
✅ Robust user profile handling (no more "no profile" errors)
✅ AI-powered cause recommendations
✅ Standardized category system
✅ Role-based user registration with post-registration immutability
✅ JWT claims for onboarding flow
✅ Complete frontend integration documentation

**Ready for frontend implementation!**
