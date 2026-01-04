#!/usr/bin/env python
"""
ECD/ECDB SETUP HELPER
Shows how to properly set up ECDA→ECDB→Grade 1 progression with fees
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    ECD PROGRESSION & FEES SETUP GUIDE                      ║
║                       ECDA → ECDB → Grade 1 Path                           ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─ SYSTEM STRUCTURE ─────────────────────────────────────────────────────────┐
│                                                                             │
│  ECDA (Age 4-5)      ECDB (Age 5-6)     Grade 1-7                         │
│  • Class Model       • Class Model      • Class Model                      │
│  • Fee Structure     • Fee Structure    • Fee Structure                    │
│  • Students          • Students        • Students                          │
│  • Payments          • Payments        • Payments                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ PROGRESSION PATHWAY ──────────────────────────────────────────────────────┐
│                                                                             │
│  Year 2026                                Year 2027                        │
│  ├─ ECDA A (4-5 yrs)                                                      │
│  │  └─ [Transfer]                                                         │
│  └─ ECDB A (5-6 yrs) ────────────────────→ Grade 1 A                     │
│                                            ├─ Grade 2 A                   │
│  Same Year            Next Year             └─ ... Grade 7               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ SETUP STEPS (In Order!) ──────────────────────────────────────────────────┐
│                                                                             │
│  1. CREATE CLASSES                                                         │
│     Dashboard > Settings > Classes > Create Class                          │
│                                                                             │
│     For Year 2026:                                                        │
│     ✓ ECDA A, ECDA B                                                      │
│     ✓ ECDB A, ECDB B                                                      │
│     ✓ 1 A, 1 B, 2 A, 2 B, ... 7 A, 7 B                                   │
│                                                                             │
│  2. SET UP FEES FOR EACH CLASS                                            │
│     Dashboard > Settings > Fees > Create Fee                              │
│                                                                             │
│     Create TermFee for each combo:                                        │
│     • ECDA A + Term 1 = $X                                                │
│     • ECDA A + Term 2 = $X                                                │
│     • ECDA A + Term 3 = $X                                                │
│     • ECDA B + Term 1 = $X  (same or different)                           │
│     • ... (repeat for all classes)                                        │
│                                                                             │
│  3. ENROLL STUDENTS IN ECDA                                               │
│     Dashboard > Students > Create Student                                 │
│     • Select ECDA A or ECDA B as current_class                            │
│     • Mark as Active                                                      │
│                                                                             │
│  4. PROMOTE ECDA → ECDB (SAME YEAR)                                       │
│     Dashboard > Class Transfers                                           │
│     • Select student from ECDA                                            │
│     • Transfer to ECDB (Year 2026)                                        │
│     • System creates StudentMovement record                               │
│                                                                             │
│  5. PROMOTE ECDB → GRADE 1 (NEXT YEAR)                                    │
│     Dashboard > Class Transfers                                           │
│     • Select student from ECDB                                            │
│     • Transfer to Grade 1 (Year 2027)                                     │
│     • System creates StudentMovement record                               │
│     • StudentBalance auto-created for new fees                            │
│     • Previous balance carried forward as arrears                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ FEE MANAGEMENT ───────────────────────────────────────────────────────────┐
│                                                                             │
│  Each Class Can Have Different Fees:                                      │
│                                                                             │
│    ECDA A: Term 1=$500, Term 2=$500, Term 3=$500 = $1,500/year            │
│    ECDA B: Term 1=$500, Term 2=$500, Term 3=$500 = $1,500/year            │
│    ECDB A: Term 1=$550, Term 2=$550, Term 3=$550 = $1,650/year            │
│    ECDB B: Term 1=$550, Term 2=$550, Term 3=$550 = $1,650/year            │
│    Grade 1 A: Term 1=$600, Term 2=$600, Term 3=$600 = $1,800/year         │
│    ... (continue pattern)                                                 │
│                                                                             │
│  How Arrears Work:                                                        │
│    If student owes $300 from ECDA and transfers to ECDB:                  │
│    • $300 debt carries to ECDB                                            │
│    • Payment applies to most recent balance first                         │
│    • When transferred to Grade 1, $300 still outstanding                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ CHECKING PROGRESS ────────────────────────────────────────────────────────┐
│                                                                             │
│  View Student Journey:                                                    │
│    Dashboard > Students > Select Student                                  │
│    • Current Class: Shows ECDA, ECDB, or Grade X                          │
│    • Balance Tab: Total owing across all levels                           │
│    • Movements Tab: Shows all transfers (ECDA→ECDB→Grade 1)               │
│    • Payments Tab: All payments at each level                             │
│                                                                             │
│  View Class Occupancy:                                                    │
│    Dashboard > Classes                                                    │
│    • ECDA A: 10 students                                                  │
│    • ECDB A: 8 students                                                   │
│    • Grade 1 A: 7 students                                                │
│    • ... (shows progression)                                              │
│                                                                             │
│  Financial Reports:                                                       │
│    Dashboard > Fees > Fee Dashboard                                       │
│    • Outstanding by Grade: ECDA, ECDB, Grade 1, etc.                      │
│    • Total fees owed at each level                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ KEY FEATURES ─────────────────────────────────────────────────────────────┐
│                                                                             │
│  ✓ Automatic Fee Calculation                                              │
│    → When student transfers, correct fees assigned automatically          │
│                                                                             │
│  ✓ Arrears Tracking                                                       │
│    → Unpaid fees follow student through grades                            │
│                                                                             │
│  ✓ Movement History                                                       │
│    → Every transfer recorded (ECDA→ECDB→Grade 1→etc)                      │
│                                                                             │
│  ✓ Class Transfers                                                        │
│    → Flexible tool for moving students between classes                    │
│    → Used for ECDA→ECDB progression                                       │
│                                                                             │
│  ✓ Bulk Promotion                                                         │
│    → For promoting Grade 1→2, 2→3, etc at year end                        │
│    → NOT used for ECDA/ECDB (use transfers instead)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ EXAMPLE SCENARIO ─────────────────────────────────────────────────────────┐
│                                                                             │
│  Student: Alice Johnson                                                   │
│                                                                             │
│  Jan 2026 - Enrolls in ECDA A (Year 2026)                                │
│             Fees: $500/term × 3 = $1,500                                  │
│             Pays: $1,000 (owes $500)                                      │
│                                                                             │
│  Jun 2026 - Transfers to ECDB A (Same year: 2026)                        │
│             New Fees: $550/term × 2 = $1,100                              │
│             Previous Balance: $500 carries forward                         │
│             Total Outstanding: $500 + $1,100 = $1,600                     │
│             Pays: $800 (owes $800)                                        │
│                                                                             │
│  Jan 2027 - Transfers to Grade 1 A (Next year: 2027)                     │
│             New Fees: $600/term × 3 = $1,800                              │
│             Previous Balance: $800 carries forward                         │
│             Total Outstanding: $800 + $1,800 = $2,600                     │
│             Pays: $2,600 (fully paid!)                                    │
│                                                                             │
│  Total Fees Paid Across All Levels: $4,400                               │
│  (ECDA $1,000 + ECDB $800 + Grade 1 $2,600)                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

╔════════════════════════════════════════════════════════════════════════════╗
║  All code changes committed! System ready for ECDA→ECDB→Grade 1 setup    ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
