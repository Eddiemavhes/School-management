# Dashboard Access Patterns & URL Reference

## Quick Access URLs

### Admin Dashboard
```
URL: /admin/dashboard/
Full: http://localhost:8000/admin/dashboard/
Name: admin_dashboard
```

### Class Dashboard
```
URL: /admin/dashboard/class/<class_id>/
Examples:
  - http://localhost:8000/admin/dashboard/class/1/
  - http://localhost:8000/admin/dashboard/class/2/
  - http://localhost:8000/admin/dashboard/class/46/
Name: class_dashboard
```

### Student Dashboard
```
URL: /admin/dashboard/student/<student_id>/
Examples:
  - http://localhost:8000/admin/dashboard/student/1/
  - http://localhost:8000/admin/dashboard/student/5/
  - http://localhost:8000/admin/dashboard/student/40/
Name: student_dashboard
```

---

## Django URL Configuration

```python
# From core/urls.py
urlpatterns = [
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('dashboard/class/<int:class_id>/', ClassDashboardView.as_view(), name='class_dashboard'),
    path('dashboard/student/<int:student_id>/', StudentDashboardView.as_view(), name='student_dashboard'),
]
```

---

## Using the URLs in Templates

### Link to Admin Dashboard
```django
<a href="{% url 'admin_dashboard' %}">System Dashboard</a>
```

### Link to Class Dashboard
```django
<a href="{% url 'class_dashboard' class.id %}">{{ class }} Dashboard</a>
```

### Link to Student Dashboard
```django
<a href="{% url 'student_dashboard' student.id %}">{{ student }} Dashboard</a>
```

---

## Example Integration Points

### In Class List Template
```django
{% for class in classes %}
  <a href="{% url 'class_dashboard' class.id %}">
    View {{ class.grade }}-{{ class.section }} Dashboard
  </a>
{% endfor %}
```

### In Student Detail Template
```django
<a href="{% url 'student_dashboard' student.id %}">
  View Financial Dashboard
</a>
```

### In Navigation/Menu
```django
<nav>
  <a href="{% url 'admin_dashboard' %}">System Dashboard</a>
  <a href="{% url 'class_list' %}">Classes</a>
  <a href="{% url 'student_list' %}">Students</a>
</nav>
```

---

## Views & View Classes

### AdminDashboardView
- **File**: core/views/dashboard_views.py
- **Template**: templates/dashboard/admin_dashboard.html
- **Context Variables**: 40+
- **Authentication**: LoginRequiredMixin

### ClassDashboardView
- **File**: core/views/dashboard_views.py
- **Template**: templates/dashboard/class_dashboard.html
- **URL Parameter**: class_id (integer)
- **Context Variables**: 20+
- **Authentication**: LoginRequiredMixin

### StudentDashboardView
- **File**: core/views/dashboard_views.py
- **Template**: templates/dashboard/student_dashboard.html
- **URL Parameter**: student_id (integer)
- **Context Variables**: 25+
- **Authentication**: LoginRequiredMixin

---

## Testing URLs

### Admin Dashboard Test
```bash
curl http://localhost:8000/admin/dashboard/
```

### Class Dashboard Tests
```bash
curl http://localhost:8000/admin/dashboard/class/1/
curl http://localhost:8000/admin/dashboard/class/2/
```

### Student Dashboard Tests
```bash
curl http://localhost:8000/admin/dashboard/student/1/
curl http://localhost:8000/admin/dashboard/student/5/
```

---

## Available Classes (Examples)

Based on current database:
- Class 1 (Grade 1, Section A-H) IDs: 1-8
- Class 2 (Grade 2, Section A-G) IDs: 9-15
- Class 3 (Grade 3, Section A-F) IDs: 16-21
- ... up to 46 total classes

**Try**: `/admin/dashboard/class/1/` through `/admin/dashboard/class/46/`

---

## Available Students (Examples)

Based on current database:
- 40 students total
- IDs range from 1 to 40

**Try**: `/admin/dashboard/student/1/` through `/admin/dashboard/student/40/`

---

## Error Handling

### Invalid Class ID
```
URL: /admin/dashboard/class/999/
Result: Error message displayed: "Class not found"
Status: 200 OK (graceful error)
```

### Invalid Student ID
```
URL: /admin/dashboard/student/999/
Result: Error message displayed: "Student not found"
Status: 200 OK (graceful error)
```

### Not Authenticated
```
URL: /admin/dashboard/
Result: Redirected to login page
Status: 302 Redirect
```

---

## Context Variables Available in Templates

### Admin Dashboard
- total_students
- active_students
- inactive_students
- total_classes
- total_teachers
- assigned_teachers
- unassigned_teachers
- current_term_fee
- current_term_collected
- total_arrears
- collection_rate
- students_with_arrears
- no_payment_students
- term_collected (array)
- term_due (array)
- class_distribution_labels
- class_distribution_data
- balance_paid_count
- balance_partial_count
- balance_unpaid_count

### Class Dashboard
- class_obj
- students
- total_students
- class_fee_collected
- class_fee_due
- class_fee_outstanding
- class_total_arrears
- class_collection_rate
- gender_labels (JSON)
- gender_data (JSON)
- age_labels (JSON)
- age_data (JSON)
- students_needing_attention
- fully_paid
- partial_paid
- unpaid

### Student Dashboard
- student
- current_balance_obj
- current_balance
- current_term_fee
- current_arrears
- current_total_due
- current_amount_paid
- payment_priority
- payment_progress
- all_balances
- all_payments
- total_ever_due
- total_ever_paid
- lifetime_balance
- collection_rate
- arrears_timeline_labels (JSON)
- arrears_timeline_data (JSON)
- balance_timeline_data (JSON)
- payment_method_labels (JSON)
- payment_method_data (JSON)
- projected_next_terms

---

## Navigation Setup (Optional)

### Add to Main Navigation
```html
<!-- In base.html or main navigation template -->
<li><a href="/admin/dashboard/">Dashboard</a></li>
```

### Add to Sidebar
```django
<div class="sidebar">
  <h3>Views</h3>
  <ul>
    <li><a href="{% url 'admin_dashboard' %}">System Dashboard</a></li>
    <li><a href="{% url 'class_list' %}">Classes</a></li>
    <li><a href="{% url 'student_list' %}">Students</a></li>
  </ul>
</div>
```

---

## Performance Notes

### Query Optimization
- Class dashboard fetches all students for a class in one query
- Student dashboard uses prefetch_related for relationships
- Admin dashboard uses aggregations for counts
- All queries optimized with select_related/prefetch_related

### Caching Considerations
- Currently no caching (fresh data each request)
- Consider Redis caching for high-traffic sites
- Cache invalidation on payment/balance changes

### Database Indexes
- Ensure indexes on:
  - StudentBalance.term_id
  - StudentBalance.student_id
  - Class.grade, Class.section
  - Student.current_class_id

---

## Reverse URL Resolution

### In Python Code
```python
from django.urls import reverse

admin_url = reverse('admin_dashboard')
class_url = reverse('class_dashboard', kwargs={'class_id': 1})
student_url = reverse('student_dashboard', kwargs={'student_id': 5})
```

### In Management Commands
```python
from django.core.management.base import BaseCommand
from django.urls import reverse

class Command(BaseCommand):
    def handle(self, *args, **options):
        url = reverse('class_dashboard', kwargs={'class_id': 1})
        self.stdout.write(f"Class dashboard: {url}")
```

---

## API Integration (Future)

The dashboards could be enhanced with API endpoints:

```python
# Potential future endpoints
/api/dashboard/stats/
/api/class/<class_id>/stats/
/api/student/<student_id>/stats/
```

---

## Mobile Access

All dashboards are responsive and work on:
- ✅ Desktop browsers (1920x1080 and above)
- ✅ Tablets (768px-1023px)
- ✅ Mobile phones (< 768px)

Just visit the same URLs on mobile devices.

---

## Browser Compatibility

### Tested On:
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

### Requirements:
- JavaScript enabled (for Chart.js)
- Cookie support (for session management)
- CSS3 support (for glass-morphism effects)

---

## Common Issues & Solutions

### "Class not found" error
**Cause**: Invalid class_id in URL
**Solution**: Check class_id parameter, use class IDs from 1-46

### "Student not found" error
**Cause**: Invalid student_id in URL
**Solution**: Check student_id parameter, use student IDs from 1-40

### 404 Not Found
**Cause**: Typo in URL path
**Solution**: Verify URL format: `/admin/dashboard/class/1/` (with trailing slash)

### Charts not displaying
**Cause**: JavaScript error or Chart.js CDN down
**Solution**: Check browser console, reload page, verify internet connection

### Login page instead of dashboard
**Cause**: Not authenticated
**Solution**: Log in first, then access dashboard URLs

---

**Ready to explore your dashboards!** 📊
