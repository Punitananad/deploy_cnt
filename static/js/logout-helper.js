// Logout Helper - Ensures complete client-side cleanup
(function() {
    'use strict';
    
    function completeLogout() {
        // Clear all localStorage
        try {
            localStorage.clear();
        } catch(e) {}
        
        // Clear all sessionStorage
        try {
            sessionStorage.clear();
        } catch(e) {}
        
        // Clear any cached authentication state
        if (window.sessionManager) {
            window.sessionManager.clearSession();
        }
        
        // Force reload to ensure clean state
        setTimeout(() => {
            window.location.reload(true);
        }, 100);
    }
    
    // Attach to logout links
    document.addEventListener('DOMContentLoaded', function() {
        const logoutLinks = document.querySelectorAll('a[href*="/logout"]');
        logoutLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Let the server-side logout happen first
                setTimeout(completeLogout, 500);
            });
        });
    });
    
    // Export for manual use
    window.completeLogout = completeLogout;
})();