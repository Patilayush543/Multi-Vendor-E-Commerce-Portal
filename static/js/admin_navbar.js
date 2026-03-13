// Add "Go to Main Page" button to admin navbar
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.navbar') || document.querySelector('#header');
    
    if (navbar) {
        // Check if button already exists
        if (!document.getElementById('main-page-btn')) {
            // Create the button
            const button = document.createElement('a');
            button.id = 'main-page-btn';
            button.href = '/';
            button.className = 'main-page-btn';
            button.innerHTML = '<i class="fas fa-home"></i> Go to Main Page';
            
            // Find the navbar nav or append to navbar
            const navRight = navbar.querySelector('.navbar-nav') || navbar;
            
            // Create a wrapper for better styling
            const wrapper = document.createElement('div');
            wrapper.className = 'navbar-main-page-wrapper';
            wrapper.appendChild(button);
            
            // Append to navbar
            navbar.insertBefore(wrapper, navbar.firstChild);
        }
    }
});
