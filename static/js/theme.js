// Dark mode toggle
document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle
    const toggle = document.getElementById('dark-toggle');
    if (toggle) {
        // Load saved preference or system default
        if (localStorage.getItem('darkMode') === 'enabled' || 
            (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
            toggle.textContent = '☀️';
        } else {
            toggle.textContent = '🌙';
        }

        toggle.addEventListener('click', function() {
            document.documentElement.classList.toggle('dark');
            if (document.documentElement.classList.contains('dark')) {
                localStorage.setItem('darkMode', 'enabled');
                toggle.textContent = '☀️';
            } else {
                localStorage.setItem('darkMode', 'disabled');
                toggle.textContent = '🌙';
            }
        });
    }

    // Auto-disappear flash alerts after 5 seconds
    function hideAlert(alertEl) {
        alertEl.classList.add('fade-out');
        setTimeout(() => {
            if (alertEl.parentNode) {
                alertEl.parentNode.removeChild(alertEl);
            }
        }, 500); // Match animation duration
    }

    function initAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.fade-out)');
        alerts.forEach(alert => {
            setTimeout(() => hideAlert(alert), 5000); // 5 seconds
        });
    }

    // Initial alerts
    initAlerts();

    // Watch for new alerts (in case added dynamically)
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.matches && node.matches('.alert')) {
                        setTimeout(() => hideAlert(node), 5000);
                    } else if (node.nodeType === 1) {
                        node.querySelectorAll('.alert:not(.fade-out)').forEach(initAlerts);
                    }
                });
            }
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });
});

