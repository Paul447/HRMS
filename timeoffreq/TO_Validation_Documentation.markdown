# Theoretical Explanation of PTO Validation Conditions

## Overview
The Paid Time Off (PTO) validation system enforces business rules for employee time-off requests in a Django application, supporting leave types: Unverified Sick Leave (`UNVSL`), Medical Leave (`VSL`), and Family Care Sick Leave (`FVSL`). The validation logic is modularized into functions (`make_timezone_aware`, `validate_duration`, `validate_medical_document`, `validate_leave_balance`, `validate_pto_request`) to ensure separation of concerns, reusability, and maintainability.

## 1. Timezone Normalization (`make_timezone_aware`)

**Purpose**: Standardizes datetime inputs to be timezone-aware, preventing errors in date arithmetic.

**Conditions**:
- Return `None` if input datetime (`dt`) is `None`.
- Use Django’s current timezone if `target_tz` is not provided.
- Localize naive datetimes to the target timezone; convert aware datetimes to the target timezone.
- **Rationale**: Ensures consistent datetime handling, aligning with Django’s timezone-aware database requirements.

**Assumptions**: Django’s timezone framework is configured correctly.

## 2. Duration Validation (`validate_duration`)

**Purpose**: Ensures a positive duration and required datetimes, calculating total hours for balance checks.

**Conditions**:
- Error if `start_date_time` or `end_date_time` is missing.
- Error if duration (`end_date_time - start_date_time`) is zero or negative.
- Calculate `total_hours` as `Decimal` (seconds/3600, rounded to 2 decimals) if valid.
- Return `Decimal('0.00')` and errors if invalid.
- **Rationale**: Ensures meaningful leave periods and precise hour calculations for balance deductions.

**Assumptions**: Input datetimes are normalized; hours are tracked with 2-decimal precision.

## 3. Medical Document Validation (`validate_medical_document`)

**Purpose**: Enforces medical documentation for health-related leave types (`VSL`, `FVSL`).

**Conditions**:
- Error if `leave_type_name` is `VSL` or `FVSL` and `medical_document` is missing.
- No error for other leave types (e.g., `UNVSL`).
- **Rationale**: Verifies compliance with health-related leave policies.

**Assumptions**: `medical_document` is a file object or `None`.

## 4. Leave Balance Validation (`validate_leave_balance`)

**Purpose**: Ensures sufficient leave balance for the requested hours, specific to each leave type.

**Conditions**:
- Skip if `total_hours <= 0`, `user`, or `leave_type_name` is missing.
- Fetch `SickLeaveBalance` with `select_for_update` if required; error if no balance exists.
- **UNVSL**:
  - Error if `unverified_sick_balance < prorated_unverified_sick_leave`.
  - Error if `total_hours > unverified_sick_balance`.
- **VSL/FVSL**:
  - Error if `total_hours > verified_sick_balance`.
- **FVSL**:
  - Error if no `MaxSickValue` exists.
  - Error if `used_FVSL + total_hours > threshold_FVSL`.
- Catch unexpected errors for diagnostic feedback.
- **Rationale**: Prevents overdrawing leave balances, with `FVSL` having an additional threshold cap.

**Assumptions**: Balance fields are `DecimalField`; `MaxSickValue` has `threshold_FVSL`.

## 5. Centralized PTO Validation (`validate_pto_request`)

**Purpose**: Orchestrates all validations for a unified interface.

**Conditions**:
- Normalize datetimes using `make_timezone_aware`.
- Validate duration, update errors.
- Validate medical documents for relevant leave types, update errors.
- Validate balances, update errors.
- Return aggregated error dictionary.
- **Rationale**: Centralizes validation logic for consistent enforcement across model and serializer.

**Assumptions**: Inputs are valid; errors are handled by the caller.

## Integration
- Used in `TimeoffRequestSerializerEmployee` for `validate`, `create`, `update`.
- `use_select_for_update=True` in `create`/`update` with `transaction.atomic()` for safety.
- Errors raised as `ValidationError` for standardized API responses.

## Design Principles
- **Modularity**: Single-responsibility functions for testability.
- **Precision**: `Decimal` for accurate calculations.
- **Robustness**: Comprehensive error handling.
- **Reusability**: Independent functions for broader use.

This documentation clarifies the validation logic, ensuring developers understand the conditions and their purpose.