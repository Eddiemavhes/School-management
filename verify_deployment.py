"""
Script to verify ECDA/ECDB is properly deployed.
Run this on the live server to check the template content.
"""

import os
import subprocess

template_path = 'templates/classes/create.html'

print("=" * 70)
print("CHECKING DEPLOYED TEMPLATE")
print("=" * 70)

if os.path.exists(template_path):
    with open(template_path, 'r') as f:
        content = f.read()
    
    if 'ECDA' in content and 'ECDB' in content:
        print("✅ TEMPLATE IS CORRECT")
        print("   - Contains ECDA option")
        print("   - Contains ECDB option")
        
        # Show the grade select section
        if '<option value="ECDA">' in content:
            print("   - Grade select HTML is updated")
    else:
        print("❌ TEMPLATE IS OUTDATED")
        print("   - Missing ECDA option")
        print("   - Missing ECDB option")
        print("\n   This means the deployment didn't pick up the latest code.")
        print("   Solution: Manually redeploy or push a new commit to trigger rebuild.")
else:
    print(f"❌ Template file not found: {template_path}")

print("\n" + "=" * 70)

# Also check git status
try:
    result = subprocess.run(['git', 'log', '--oneline', '-3'], capture_output=True, text=True)
    print("Recent commits:")
    print(result.stdout)
except:
    pass
