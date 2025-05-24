/**
 * Lost and Found Management System
 * Form validation and enhancement scripts
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle Form Validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Password strength meter
    const passwordInput = document.querySelector('input[name="password"]');
    const passwordStrengthMeter = document.querySelector('.password-strength-meter');
    
    if (passwordInput && passwordStrengthMeter) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strength = calculatePasswordStrength(password);
            
            // Remove all classes
            passwordStrengthMeter.classList.remove('strength-weak', 'strength-medium', 'strength-strong');
            
            if (password.length === 0) {
                passwordStrengthMeter.style.width = '0';
            } else if (strength < 40) {
                passwordStrengthMeter.classList.add('strength-weak');
            } else if (strength < 80) {
                passwordStrengthMeter.classList.add('strength-medium');
            } else {
                passwordStrengthMeter.classList.add('strength-strong');
            }
        });
    }
    
    // Image preview when uploading
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            const previewContainer = document.querySelector('.image-preview');
            if (!previewContainer) return;
            
            previewContainer.innerHTML = '';
            
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.classList.add('img-thumbnail', 'mt-2', 'mb-3');
                    img.style.maxHeight = '200px';
                    previewContainer.appendChild(img);
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    
    // Date validation (ensure date_lost is before date_found)
    const dateLostInput = document.querySelector('input[name="date_lost"]');
    const dateFoundInput = document.querySelector('input[name="date_found"]');
    
    if (dateLostInput && dateFoundInput) {
        dateFoundInput.addEventListener('change', function() {
            const dateLost = new Date(dateLostInput.value);
            const dateFound = new Date(this.value);
            
            if (dateLost > dateFound) {
                this.setCustomValidity('Found date must be after lost date');
            } else {
                this.setCustomValidity('');
            }
        });
        
        dateLostInput.addEventListener('change', function() {
            if (dateFoundInput.value) {
                const dateLost = new Date(this.value);
                const dateFound = new Date(dateFoundInput.value);
                
                if (dateLost > dateFound) {
                    dateFoundInput.setCustomValidity('Found date must be after lost date');
                } else {
                    dateFoundInput.setCustomValidity('');
                }
            }
        });
    }
    
    // Handle search form reset
    const searchResetButton = document.querySelector('.search-form-reset');
    if (searchResetButton) {
        searchResetButton.addEventListener('click', function() {
            const form = this.closest('form');
            form.reset();
            
            // Reset select2 components if they exist
            const select2Elements = form.querySelectorAll('.select2-hidden-accessible');
            select2Elements.forEach(select => {
                $(select).val(null).trigger('change');
            });
        });
    }
});

/**
 * Calculate password strength score between 0-100
 * @param {string} password - The password to check
 * @return {number} Strength score (0-100)
 */
function calculatePasswordStrength(password) {
    if (!password) return 0;
    
    let score = 0;
    
    // Length
    score += Math.min(password.length * 4, 25);
    
    // Character variety
    const hasLowercase = /[a-z]/.test(password);
    const hasUppercase = /[A-Z]/.test(password);
    const hasNumbers = /[0-9]/.test(password);
    const hasSpecial = /[^a-zA-Z0-9]/.test(password);
    
    if (hasLowercase) score += 10;
    if (hasUppercase) score += 15;
    if (hasNumbers) score += 10;
    if (hasSpecial) score += 15;
    
    // Variety of characters
    const uniqueChars = new Set(password.split(''));
    score += Math.min(uniqueChars.size * 2, 25);
    
    return Math.min(score, 100);
}

/**
 * Format a description as a searchable/comparable string
 * Used in the item matching algorithm
 * @param {string} text - The text to format
 * @return {string} Formatted text
 */
function formatForMatching(text) {
    if (!text) return '';
    
    return text
        .toLowerCase()
        .replace(/[^\w\s]/g, '') // Remove punctuation
        .replace(/\s+/g, ' ')    // Normalize whitespace
        .trim();
}
