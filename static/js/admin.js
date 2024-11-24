// Admin Dashboard Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Settings form validation
    const settingsForm = document.querySelector('form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            const intervalInput = document.getElementById('synthesis_interval');
            const interval = parseInt(intervalInput.value);
            
            if (interval < 5 || interval > 1440) {
                e.preventDefault();
                alert('L''intervalle de synthèse doit être compris entre 5 et 1440 minutes.');
                return false;
            }
        });
    }

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Synthesis content expansion/collapse
    const synthesesContent = document.querySelectorAll('.synthesis-content');
    synthesesContent.forEach(content => {
        if (content.clientHeight > 300) {
            content.style.maxHeight = '300px';
            content.style.overflow = 'hidden';
            
            const expandBtn = document.createElement('button');
            expandBtn.className = 'btn btn-link btn-sm';
            expandBtn.textContent = 'Show more';
            
            expandBtn.addEventListener('click', function() {
                if (content.style.maxHeight) {
                    content.style.maxHeight = null;
                    expandBtn.textContent = 'Show less';
                } else {
                    content.style.maxHeight = '300px';
                    expandBtn.textContent = 'Show more';
                }
            });
            
            content.parentNode.insertBefore(expandBtn, content.nextSibling);
        }
    });

    // Settings notification handling
    const emailNotificationsCheckbox = document.getElementById('email_notifications');
    if (emailNotificationsCheckbox) {
        emailNotificationsCheckbox.addEventListener('change', function() {
            const saveBtn = this.closest('form').querySelector('button[type="submit"]');
            saveBtn.classList.add('btn-pulse');
            setTimeout(() => saveBtn.classList.remove('btn-pulse'), 1000);
        });
    }

    // Timestamp formatting
    const timestamps = document.querySelectorAll('.synthesis-item h5');
    timestamps.forEach(timestamp => {
        const date = new Date(timestamp.textContent.replace('Generated on: ', ''));
        const formattedDate = new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        }).format(date);
        timestamp.textContent = `Generated on: ${formattedDate}`;
    });

    // Add dynamic loading state to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            if (this.type === 'submit') {
                this.classList.add('disabled');
                const originalText = this.textContent;
                this.innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Processing...
                `;
                
                // Reset button state after form submission
                setTimeout(() => {
                    this.classList.remove('disabled');
                    this.textContent = originalText;
                }, 2000);
            }
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Alt + D for Dashboard
        if (e.altKey && e.key === 'd') {
            const dashboardLink = document.querySelector('a[href*="dashboard"]');
            if (dashboardLink) dashboardLink.click();
        }
        // Alt + S for Settings
        if (e.altKey && e.key === 's') {
            const settingsLink = document.querySelector('a[href*="settings"]');
            if (settingsLink) settingsLink.click();
        }
        // Alt + L for Logout
        if (e.altKey && e.key === 'l') {
            const logoutLink = document.querySelector('a[href*="logout"]');
            if (logoutLink) logoutLink.click();
        }
    });

    // Add copy functionality for synthesis content
    document.querySelectorAll('.synthesis-content').forEach(content => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-sm btn-outline-secondary float-end';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
        
        copyBtn.addEventListener('click', async function() {
            try {
                await navigator.clipboard.writeText(content.textContent.trim());
                this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-copy"></i> Copy';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy text:', err);
            }
        });
        
        content.insertBefore(copyBtn, content.firstChild);
    });
});

// Add custom CSS for button pulse animation
const style = document.createElement('style');
style.textContent = `
    .btn-pulse {
        animation: pulse 1s;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(var(--bs-primary-rgb), 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(var(--bs-primary-rgb), 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(var(--bs-primary-rgb), 0);
        }
    }
`;
document.head.appendChild(style);
