document.addEventListener('DOMContentLoaded', function() {
    initNavbar();
    initMobileMenu();
    initCounterAnimation();
    initCountdown();
    initFormSubmission();
    initSmoothScroll();
    initCartButtons();
    initWhatsAppButton();
    initPurchaseToggle();
    initHeroParallax();
});

function initHeroParallax() {
    const heroBg = document.querySelector('.hero-bg-image');
    if (!heroBg) return;
    
    let ticking = false;
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                const scrolled = window.pageYOffset;
                const rate = scrolled * 0.4;
                const scale = 1 + (scrolled * 0.0002);
                heroBg.style.transform = `translateY(${rate}px) scale(${scale})`;
                ticking = false;
            });
            ticking = true;
        }
    });
}

function initNavbar() {
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section[id]');
    
    window.addEventListener('scroll', () => {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (window.pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

function initMobileMenu() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    navToggle.addEventListener('click', () => {
        navToggle.classList.toggle('active');
        navLinks.classList.toggle('active');
        document.body.style.overflow = navLinks.classList.contains('active') ? 'hidden' : '';
    });
    
    navLinks.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navToggle.classList.remove('active');
            navLinks.classList.remove('active');
            document.body.style.overflow = '';
        });
    });
}

function initCounterAnimation() {
    const counters = document.querySelectorAll('.stat-number');
    let animated = false;
    
    function animateCounters() {
        if (animated) return;
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-count'));
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;
            
            function updateCounter() {
                current += step;
                if (current < target) {
                    counter.textContent = Math.floor(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            }
            
            updateCounter();
        });
        
        animated = true;
    }
    
    const heroStats = document.querySelector('.hero-stats');
    if (heroStats) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounters();
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(heroStats);
    }
}

function initCountdown() {
    const saleEndDate = new Date();
    saleEndDate.setDate(saleEndDate.getDate() + 7);
    
    function updateCountdown() {
        const now = new Date().getTime();
        const distance = saleEndDate.getTime() - now;
        
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        document.getElementById('days').textContent = days.toString().padStart(2, '0');
        document.getElementById('hours').textContent = hours.toString().padStart(2, '0');
        document.getElementById('minutes').textContent = minutes.toString().padStart(2, '0');
        document.getElementById('seconds').textContent = seconds.toString().padStart(2, '0');
    }
    
    updateCountdown();
    setInterval(updateCountdown, 1000);
}

function initFormSubmission() {
    const form = document.querySelector('.contact-form');

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;

        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        submitBtn.disabled = true;

        setTimeout(() => {
            submitBtn.innerHTML = '<i class="fas fa-check"></i> Sent!';
            submitBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';

            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.style.background = '';
                submitBtn.disabled = false;
                form.reset();
            }, 2000);
        }, 1500);
    });
}

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                const offsetTop = target.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

function initCartButtons() {
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const originalText = this.innerHTML;
            
            this.innerHTML = '<i class="fas fa-check"></i> Added!';
            this.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.style.background = '';
            }, 2000);
        });
    });
}

document.querySelectorAll('.quick-view-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const card = this.closest('.product-card');
        const productName = card.querySelector('.product-name').textContent;
        
        alert(`Quick View: ${productName}\n\nThis would open a detailed product modal in a full implementation.`);
    });
});

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
if (prefersReducedMotion.matches) {
    document.querySelectorAll('*, *::before, *::after').forEach(el => {
        el.style.animationDuration = '0.01ms !important';
        el.style.transitionDuration = '0.01ms !important';
    });
}

function initWhatsAppButton() {
    const whatsappBtn = document.getElementById('whatsappChat');

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 500) {
            whatsappBtn.classList.add('visible');
        } else {
            whatsappBtn.classList.remove('visible');
        }
    });
}

function initPurchaseToggle() {
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    const productCards = document.querySelectorAll('.product-card');

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const mode = this.getAttribute('data-mode');
            switchMode(mode);
        });
    });
}

function switchMode(mode) {
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    const productCards = document.querySelectorAll('.product-card');

    // Update active button
    toggleBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-mode') === mode) {
            btn.classList.add('active');
        }
    });

    // Update all product cards
    productCards.forEach(card => {
        // Update data attribute
        card.setAttribute('data-mode', mode);

        // Get buy and rent content elements
        const buyContent = card.querySelector('.buy-content');
        const rentContent = card.querySelector('.rent-content');
        const addToCartBtn = card.querySelector('.add-to-cart-btn .btn-content span:last-child');
        const addToCartIcon = card.querySelector('.add-to-cart-btn .btn-content i');

        if (mode === 'rent') {
            // Show rent content, hide buy content
            if (buyContent) buyContent.style.display = 'none';
            if (rentContent) rentContent.style.display = 'block';
            
            // Update button text
            if (addToCartBtn) addToCartBtn.textContent = 'Rent Now';
            if (addToCartIcon) {
                addToCartIcon.className = 'fas fa-key';
            }
        } else {
            // Show buy content, hide rent content
            if (buyContent) buyContent.style.display = 'block';
            if (rentContent) rentContent.style.display = 'none';
            
            // Update button text
            if (addToCartBtn) addToCartBtn.textContent = 'Add to Cart';
            if (addToCartIcon) {
                addToCartIcon.className = 'fas fa-shopping-bag';
            }
        }

        // Add animation
        card.style.animation = 'none';
        card.offsetHeight; // Trigger reflow
        card.style.animation = 'cardFadeIn 0.5s ease';
    });
}

// Add card fade-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes cardFadeIn {
        0% {
            opacity: 0;
            transform: scale(0.95) translateY(10px);
        }
        100% {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }
`;
document.head.appendChild(style);

// Toggle Services Function
function toggleServices() {
    const hiddenServices = document.getElementById('hiddenServices');
    const showMoreBtn = document.getElementById('showMoreBtn');
    const btnText = showMoreBtn.querySelector('.btn-text');
    
    if (hiddenServices.classList.contains('show')) {
        // Hide services
        hiddenServices.classList.remove('show');
        btnText.textContent = 'Show More Services';
        showMoreBtn.classList.remove('active');
    } else {
        // Show services
        hiddenServices.classList.add('show');
        btnText.textContent = 'Show Less';
        showMoreBtn.classList.add('active');
    }
}
