# Testing Guide - Fee Configuration Page

## Pre-Testing Checklist

```bash
# 1. Django checks pass
python manage.py check
# Expected: System check identified no issues (0 silenced).

# 2. Start development server
python manage.py runserver
# Expected: Starting development server at http://127.0.0.1:8000/
```

---

## Test Cases

### Test 1: Page Loads Without Errors
**Steps:**
1. Navigate to: `http://localhost:8000/admin/academic/fee-configuration/`
2. Observe: Page loads with term cards displayed

**Expected Results:**
- ✅ Page loads without 500 error
- ✅ No console errors (F12)
- ✅ All term cards visible
- ✅ Form inputs present

---

### Test 2: Lock Icons Appear for Terms with Payments
**Setup:** Ensure you have at least one term with payments recorded

**Steps:**
1. Open Fee Configuration page
2. Look for amber lock icon 🔒 on term cards
3. Scroll through all terms

**Expected Results:**
- ✅ Terms WITH payments show amber lock icon in top-right
- ✅ Terms WITHOUT payments show no lock icon
- ✅ Lock icon has tooltip "Locked: Payments recorded"
- ✅ Icon disappears/reappears correctly on page refresh

**Verification:**
```python
# In Django shell to verify payments exist:
from core.models.academic import Payment, AcademicTerm
term = AcademicTerm.objects.first()
print(f"Term {term.id} has {Payment.objects.filter(term=term).count()} payments")
# If count > 0, lock icon should show for that term
```

---

### Test 3: Locked Terms Show Disabled Inputs
**Steps:**
1. Find a term with lock icon
2. Try to click on Fee Amount input field
3. Try to click on Due Date input field
4. Verify Start Date and End Date are still editable

**Expected Results:**
- ✅ Fee Amount input is disabled (grayed out, cursor shows "not-allowed")
- ✅ Due Date input is disabled
- ✅ Start Date input is ENABLED (can still edit)
- ✅ End Date input is ENABLED (can still edit)
- ✅ Cannot type in disabled fields
- ✅ Cannot focus on disabled fields

---

### Test 4: Locked Terms Show Disabled Button
**Steps:**
1. Find a term with lock icon
2. Observe the Save button
3. Hover over the Save button
4. Try to click the Save button

**Expected Results:**
- ✅ Button text shows "Locked" (not "Save")
- ✅ Button appears grayed out (reduced opacity)
- ✅ Cursor shows "not-allowed" on hover
- ✅ Button doesn't respond to clicks (no fetch request)
- ✅ Hover title shows: "This term is locked because payments have been recorded"

---

### Test 5: Clicking Disabled Button Shows Warning Toast
**Steps:**
1. Find a locked term
2. Try to click the "Locked" button
3. Watch for notification

**Expected Results:**
- ✅ Warning toast appears from right side of screen
- ✅ Toast shows: "⚠️ This term is locked because payments have been recorded"
- ✅ Toast has amber/orange color scheme
- ✅ Toast slides in smoothly (300ms animation)
- ✅ Toast auto-dismisses after 5 seconds
- ✅ Can manually close with X button
- ✅ No page reload

---

### Test 6: Unlocked Terms Are Fully Editable
**Setup:** Use a term WITHOUT payments (or create one)

**Steps:**
1. Find a term without lock icon
2. Click on Fee Amount field
3. Change the value (e.g., from 100 to 150)
4. Click on Due Date field
5. Change the date
6. Observe button state

**Expected Results:**
- ✅ All input fields are enabled (normal color)
- ✅ Can type in Fee Amount field
- ✅ Can select Due Date from date picker
- ✅ Cursor shows normal pointer (not "not-allowed")
- ✅ Save button shows "Save" text (not "Locked")
- ✅ Save button has normal colors
- ✅ Button is clickable

---

### Test 7: Successful Save Shows Success Toast
**Steps:**
1. Find an unlocked term
2. Change Fee Amount to a different value
3. Click "Save" button
4. Wait for response

**Expected Results:**
- ✅ Button changes text to "Saving..."
- ✅ Button becomes disabled during save
- ✅ Success toast appears: "✓ Changes saved successfully!"
- ✅ Toast has emerald/teal color scheme
- ✅ Toast auto-dismisses after 3 seconds
- ✅ Page reloads after 1.5 seconds
- ✅ Changes are persisted (new value shows on page reload)

---

## Quick Checklist

- [ ] Page loads without errors
- [ ] Lock icons appear on locked terms
- [ ] Disabled inputs on locked terms
- [ ] Disabled button on locked terms
- [ ] Warning toast on locked button click
- [ ] Can edit unlocked terms
- [ ] Success toast on save
- [ ] Page reloads after success
- [ ] Error handling works
- [ ] Mobile layout responsive

**Status: Ready to test!** ✅
