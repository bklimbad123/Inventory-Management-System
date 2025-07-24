# Part 1: Code Review & Debugging

## 1. Issues Identified

### Technical Issues:
- **No error handling:** If `request.json` is missing or malformed, the server may crash.
- **Missing validation:** No check for required fields or types.
- **Double commit:** Two `db.session.commit()` calls—this should be atomic.
- **No uniqueness check for SKU:** Could result in duplicate SKUs.
- **No check if product already exists in the warehouse.**
- **Assumes `initial_quantity` is always present.**

### Business Logic Issues:
- **Products can exist in multiple warehouses**, but this creates only one warehouse link.
- **SKU must be unique**, but the code does not enforce or handle violations.
- **Price as float might cause rounding issues.**

---

## 2. Impact in Production

| Issue | Impact |
|-------|--------|
| No error handling | Crashes API with 500 errors. |
| No validation | Bad data can pollute DB (e.g., null price). |
| No SKU uniqueness enforcement | Can break search/inventory tracking logic. |
| Two commits | Inconsistent state if one commit succeeds and the other fails. |
| Missing optional/required field validation | Leads to exceptions or invalid records. |
