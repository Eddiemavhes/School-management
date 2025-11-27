# SUPERUSER EDWIN - QUICK START GUIDE

## Login Credentials
```
Email: eddy.mavhe@gmail.com
Password: 14E07d20!01
```

## What You Can Do

### 1. Reset Admin Passwords
If a school admin forgets their password:
1. Login to superuser panel
2. Click "Reset Admin Password"
3. Select the admin
4. Enter new password (strong password required)
5. Click "Reset Password"
✓ Admin can now login with new password

### 2. Clear System Data

#### Full System Reset
Deletes EVERYTHING except admin credentials:
- All students
- All payments
- All balances
- All terms
- All academic years
- Confirmation: `CONFIRM_SYSTEM_RESET_2025`

#### Clear Payments Only
Remove all payment history:
- All payments
- All student balances
- Confirmation: `CONFIRM_PAYMENTS_CLEAR_2025`

#### Clear Students Only
Remove all student records:
- All students
- Related payments/balances
- Confirmation: `CONFIRM_STUDENTS_CLEAR_2025`

#### Clear Terms Only
Remove academic structure:
- All terms
- All term fees
- Confirmation: `CONFIRM_TERMS_CLEAR_2025`

### 3. View System Statistics
Dashboard shows:
- Total students enrolled
- Total admin accounts
- Total payments recorded
- Academic structure (years/terms)
- System status

## How to Access

### Via Navigation
1. Login with Edwin credentials
2. Click "Settings" in top menu
3. Click "Superuser Panel" (red button)

### Direct URL
```
http://your-server/superuser/
```

## Safety Features

✓ All actions require confirmation
✓ You must type `CONFIRM_RESET` to proceed
✓ System shows what will be deleted
✓ Passwords protected with strong requirements
✓ Admin accounts always preserved

## Important Notes

⚠️ Data deletion is PERMANENT
⚠️ Backup database before system reset
⚠️ Always confirm you want to delete data
⚠️ Admin login credentials are never deleted

## Troubleshooting

**Can't find Superuser Panel?**
- Make sure you're logged in as Edwin
- Check Settings dropdown
- Clear browser cache
- Try direct URL: /superuser/

**Password reset not working?**
- Ensure new password is strong (8+ chars, uppercase, lowercase, numbers)
- Passwords must match exactly
- Try again with simpler password

**Can't access after reset?**
- Admin needs new password to login
- Contact them with new temporary password
- Have them change it on first login

## Password Reset Advice

When resetting admin password:
1. Use strong temporary password
2. Inform admin immediately
3. Ask them to change password after first login
4. Never reuse old passwords
5. Send via secure channel (not email if possible)

## System Reset Advice

Before doing full system reset:
1. ✓ Backup the database
2. ✓ Inform school admin
3. ✓ Verify you have new data ready
4. ✓ Choose right confirmation token
5. ✓ Check what will be deleted
6. ✓ Type CONFIRM_RESET
7. ✓ Hit Proceed

## Support Contact

If you need help as superuser:
- Check the comprehensive guide: SUPERUSER_PANEL_COMPLETE.md
- Review confirmation tokens for each action
- Verify admin accounts before password reset
- Always backup before system reset

---

**Welcome to the Superuser Panel, Edwin!**
You now have complete control over the school management system.
Use your power wisely.
