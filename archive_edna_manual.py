"""
Script to manually archive Edna by setting correct status.
This is a one-time fix for the specific issue.
"""
from core.models.student import Student

print("\n" + "="*70)
print("ARCHIVING EDNA")
print("="*70)

# Find Edna
edna = Student.objects.filter(surname='Edna').first()

if not edna:
    print("\n✗ ERROR: Edna not found in database")
    exit(1)

print(f"\nBefore:")
print(f"  Name: {edna.full_name}")
print(f"  Status: {edna.status}")
print(f"  Is Active: {edna.is_active}")
print(f"  Is Archived: {edna.is_archived}")
print(f"  Balance: ${edna.overall_balance:.2f}")

# Status transition: ENROLLED → ACTIVE → GRADUATED
# Step 1: Transition to ACTIVE
edna.status = 'ACTIVE'
edna.save()
print(f"\nStep 1: Transitioned to ACTIVE")
print(f"  Status: {edna.status}")

# Step 2: Transition to GRADUATED
edna.status = 'GRADUATED'
edna.save()
print(f"\nStep 2: Transitioned to GRADUATED")
print(f"  Status: {edna.status}")

# Now call check_and_archive to archive her
archived = edna.check_and_archive()

if archived:
    print(f"\n✓ SUCCESS: Edna has been archived!")
    print(f"  Is Archived: {edna.is_archived}")
    print(f"\nFinal Status:")
    print(f"  Name: {edna.full_name}")
    print(f"  Status: {edna.status}")
    print(f"  Is Active: {edna.is_active}")
    print(f"  Is Archived: {edna.is_archived}")
    print(f"  Balance: ${edna.overall_balance:.2f}")
else:
    print(f"\n✗ Failed to archive. Reasons:")
    print(f"  - Already archived: {edna.is_archived}")
    print(f"  - Status not GRADUATED: {edna.status != 'GRADUATED'}")
    print(f"  - Still active: {edna.is_active}")
    print(f"  - Still owes fees: {edna.overall_balance > 0}")

print("\n" + "="*70)
