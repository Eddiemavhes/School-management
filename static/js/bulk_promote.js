document.addEventListener('DOMContentLoaded', function() {
    console.log('Bulk promote script loaded');
    
    const submitBtn = document.getElementById('promote-btn');
    const studentCheckboxes = document.querySelectorAll('.student-checkbox');
    const selectAll = document.getElementById('select-all');
    
    console.log('Submit button found:', !!submitBtn);
    console.log('Student checkboxes found:', studentCheckboxes.length);

    // Function to update button state
    function updateButtonState() {
        const checkedCount = document.querySelectorAll('.student-checkbox:checked').length;
        console.log('Checked students:', checkedCount);
        
        if (submitBtn) {
            submitBtn.disabled = checkedCount === 0;
            console.log('Button disabled set to:', submitBtn.disabled);
        }
    }

    // Add event listeners to all checkboxes
    studentCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            console.log('Checkbox changed, value:', this.value, 'Checked:', this.checked);
            updateButtonState();
        });
    });

    // Handle select all
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            console.log('Select all changed:', this.checked);
            const visibleCheckboxes = document.querySelectorAll('tr:not(.hidden) .student-checkbox');
            visibleCheckboxes.forEach(cb => cb.checked = this.checked);
            updateButtonState();
        });
    }

    // Handle form submission
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Form submitted');
            const selected = document.querySelectorAll('.student-checkbox:checked');
            if (selected.length === 0) {
                e.preventDefault();
                alert('Please select at least one student');
                return;
            }
            console.log('Submitting with', selected.length, 'students');
        });
    }

    // Initial state
    updateButtonState();
});