// DOM Elements
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileMenu = document.getElementById('mobile-menu');
const searchInput = document.getElementById('search-input');
const cartBadge = document.getElementById('cart-badge');
const newsletterForm = document.getElementById('newsletter-form');
const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');

// Cart State
let cartItems = [];

// Mobile Menu Toggle
if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('active');
        mobileMenuBtn.setAttribute('aria-expanded', 
            mobileMenu.classList.contains('active'));
    });
}

// Search Functionality
if (searchInput) {
    searchInput.addEventListener('input', debounce(handleSearch, 300));
}

function handleSearch(e) {
    const searchTerm = e.target.value.trim().toLowerCase();
    // TODO: Implement search functionality
    console.log('Searching for:', searchTerm);
}

// Cart Functions
function updateCartBadge() {
    if (cartBadge) {
        cartBadge.textContent = cartItems.length;
        cartBadge.classList.add('animate-bounce');
        setTimeout(() => cartBadge.classList.remove('animate-bounce'), 1000);
    }
}

function addToCart(productId, productName, price) {
    cartItems.push({ id: productId, name: productName, price: price });
    updateCartBadge();
    showNotification(`Added ${productName} to cart!`);
}

// Add to Cart Button Listeners
addToCartButtons.forEach(button => {
    button.addEventListener('click', (e) => {
        const product = e.target.closest('.product-card');
        if (product) {
            const productId = product.dataset.productId;
            const productName = product.querySelector('.product-name').textContent;
            const price = parseFloat(product.querySelector('.product-price').dataset.price);
            addToCart(productId, productName, price);
        }
    });
});

// Newsletter Subscription
if (newsletterForm) {
    newsletterForm.addEventListener('submit', handleNewsletterSubmit);
}

async function handleNewsletterSubmit(e) {
    e.preventDefault();
    const emailInput = newsletterForm.querySelector('input[type="email"]');
    const email = emailInput.value.trim();
    
    if (validateEmail(email)) {
        try {
            // TODO: Implement newsletter subscription
            console.log('Newsletter subscription for:', email);
            showNotification('Thank you for subscribing!');
            emailInput.value = '';
        } catch (error) {
            showNotification('Subscription failed. Please try again.', 'error');
        }
    } else {
        showNotification('Please enter a valid email address.', 'error');
    }
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white animate-fade-in`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.classList.add('animate-fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize any components that need setup
    updateCartBadge();
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});
