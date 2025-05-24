/**
 * Lost and Found Management System
 * Dashboard JavaScript functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Toggle mobile sidebar
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.toggle('show');
        });
    }
    
    // Responsive table handling
    makeTableResponsive();
    
    // Item status update
    const statusUpdateForms = document.querySelectorAll('.status-update-form');
    statusUpdateForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const itemId = formData.get('item_id');
            const newStatus = formData.get('status');
            const itemType = formData.get('item_type');
            
            // Confirm status change
            if (confirm(`Are you sure you want to mark this item as ${newStatus}?`)) {
                form.submit();
            }
        });
    });
    
    // Match review handling for admin
    const matchReviewForms = document.querySelectorAll('.match-review-form');
    matchReviewForms.forEach(form => {
        const actionSelect = form.querySelector('select[name="action"]');
        const notesField = form.querySelector('textarea[name="notes"]');
        
        if (actionSelect && notesField) {
            actionSelect.addEventListener('change', function() {
                if (this.value === 'reject') {
                    notesField.setAttribute('required', '');
                    notesField.placeholder = 'Please provide a reason for rejection';
                } else {
                    notesField.removeAttribute('required');
                    notesField.placeholder = 'Optional notes';
                }
            });
        }
    });
    
    // Filter for dashboard tables
    const tableFilter = document.querySelector('#tableFilter');
    if (tableFilter) {
        tableFilter.addEventListener('input', function() {
            const filterValue = this.value.toLowerCase().trim();
            const tableBody = document.querySelector(this.dataset.target);
            const rows = tableBody.querySelectorAll('tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filterValue) ? '' : 'none';
            });
            
            // Show empty message if no items are displayed
            const visibleRows = tableBody.querySelectorAll('tr[style=""]').length;
            const emptyMessage = document.querySelector(this.dataset.empty);
            
            if (emptyMessage) {
                emptyMessage.style.display = visibleRows === 0 ? 'block' : 'none';
            }
        });
    }
    
    // Initialize charts if present on the page
    initStatusChart();
});

/**
 * Make tables responsive by adding data attributes for mobile view
 */
function makeTableResponsive() {
    const tables = document.querySelectorAll('.responsive-table');
    
    tables.forEach(table => {
        const headerCells = table.querySelectorAll('thead th');
        const headerTexts = Array.from(headerCells).map(cell => cell.textContent.trim());
        
        const bodyRows = table.querySelectorAll('tbody tr');
        bodyRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            cells.forEach((cell, i) => {
                if (i < headerTexts.length) {
                    cell.setAttribute('data-label', headerTexts[i]);
                }
            });
        });
    });
}

/**
 * Initialize status chart for admin dashboard
 */
function initStatusChart() {
    const ctx = document.getElementById('statusChart');
    if (!ctx) return;
    
    // Get data from page
    const chartData = {
        labels: ['Unresolved', 'Resolved', 'Unclaimed', 'Claimed'],
        datasets: [{
            label: 'Item Status',
            data: [
                parseInt(ctx.dataset.unresolved || 0),
                parseInt(ctx.dataset.resolved || 0),
                parseInt(ctx.dataset.unclaimed || 0),
                parseInt(ctx.dataset.claimed || 0)
            ],
            backgroundColor: [
                '#ffcc33', // warning
                '#30c67c', // success
                '#33ccff', // info
                '#30c67c'  // success
            ]
        }]
    };
    
    // Create the chart using Chart.js if available
    if (typeof Chart !== 'undefined') {
        new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Item Status Distribution'
                    }
                }
            }
        });
    }
}

/**
 * Format match score as a percentage with appropriate color class
 * @param {number} score - Match score (0-1)
 * @return {Object} HTML and class information
 */
function formatMatchScore(score) {
    const percentage = Math.round(score * 100);
    let className = 'badge ';
    
    if (percentage < 50) {
        className += 'bg-danger';
    } else if (percentage < 75) {
        className += 'bg-warning text-dark';
    } else {
        className += 'bg-success';
    }
    
    return {
        html: `${percentage}%`,
        class: className
    };
}
