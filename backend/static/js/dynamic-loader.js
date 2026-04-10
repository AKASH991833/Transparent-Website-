/**
 * ANSH AIR COOL - Dynamic Content Loader
 * Loads all content from backend API dynamically
 */

const API_BASE = window.location.origin.includes('localhost') 
    ? 'http://localhost:5000/api' 
    : '/api';

// Fetch data from API
async function fetchFromAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`API Fetch Error (${endpoint}):`, error);
        return null;
    }
}

// Load Hero Section
async function loadHeroSection() {
    const heroData = await fetchFromAPI('/public/hero-data');
    if (!heroData) return;

    // Trust Badge
    const trustBadge = document.querySelector('.hero-trust-badge span:last-child');
    if (trustBadge && heroData.trust_badge_text) {
        trustBadge.textContent = heroData.trust_badge_text;
    }

    // Title Lines
    const titleLines = document.querySelectorAll('.hero-title .title-line');
    if (titleLines.length >= 3) {
        if (heroData.title_line_1) titleLines[0].textContent = heroData.title_line_1;
        if (heroData.title_line_2) titleLines[1].textContent = heroData.title_line_2;
        if (heroData.title_line_3) titleLines[2].textContent = heroData.title_line_3;
    }

    // Subtitle
    const subtitle = document.querySelector('.hero-subtitle');
    if (subtitle && heroData.subtitle) {
        subtitle.innerHTML = heroData.subtitle;
    }

    // Stats
    const statNumbers = document.querySelectorAll('.stat-number');
    const statSuffixes = document.querySelectorAll('.stat-suffix');
    const statLabels = document.querySelectorAll('.stat-label');

    if (statNumbers.length >= 3) {
        // Stat 1
        statNumbers[0].setAttribute('data-count', heroData.stat_1_number || 15);
        statNumbers[0].textContent = '0';
        if (statSuffixes[0]) statSuffixes[0].textContent = heroData.stat_1_suffix || '+';
        if (statLabels[0]) statLabels[0].textContent = heroData.stat_1_label || 'Years Experience';

        // Stat 2
        statNumbers[1].setAttribute('data-count', heroData.stat_2_number || 50);
        statNumbers[1].textContent = '0';
        if (statSuffixes[1]) statSuffixes[1].textContent = heroData.stat_2_suffix || 'K+';
        if (statLabels[1]) statLabels[1].textContent = heroData.stat_2_label || 'Happy Customers';

        // Stat 3
        statNumbers[2].setAttribute('data-count', heroData.stat_3_number || 99);
        statNumbers[2].textContent = '0';
        if (statSuffixes[2]) statSuffixes[2].textContent = heroData.stat_3_suffix || '%';
        if (statLabels[2]) statLabels[2].textContent = heroData.stat_3_label || 'Satisfaction Rate';

        // Re-trigger counter animation
        animateCounters();
    }

    // Quick Features
    const quickFeatures = document.querySelectorAll('.quick-feature');
    if (quickFeatures.length >= 3) {
        const features = [
            heroData.quick_feature_1,
            heroData.quick_feature_2,
            heroData.quick_feature_3
        ];
        quickFeatures.forEach((feature, index) => {
            if (feature && features[index]) {
                const span = feature.querySelector('span:last-child');
                if (span) span.textContent = features[index];
            }
        });
    }
}

// Counter Animation
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
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
}

// Load Marquee
async function loadMarquee() {
    const items = await fetchFromAPI('/public/marquee');
    if (!items || items.length === 0) return;

    const marqueeContent = document.querySelector('.marquee-content');
    if (!marqueeContent) return;

    // Clear existing content
    marqueeContent.innerHTML = '';

    // Create marquee items (duplicate for seamless loop)
    const allItems = [...items, ...items];
    
    allItems.forEach(item => {
        const marqueeItem = document.createElement('span');
        marqueeItem.className = 'marquee-item';
        marqueeItem.innerHTML = `
            <span class="glow-text">${item.main_text}</span>
            <span class="marquee-divider">✦</span>
            <span class="marquee-text">${item.sub_text}</span>
            <span class="marquee-divider">✦</span>
        `;
        marqueeContent.appendChild(marqueeItem);
    });
}

// Load Products
async function loadProducts() {
    const products = await fetchFromAPI('/public/products');
    if (!products || products.length === 0) return;

    const productsGrid = document.querySelector('.products-grid');
    if (!productsGrid) return;

    // Clear existing products
    productsGrid.innerHTML = '';

    // Create product cards
    products.forEach((product, index) => {
        const features = Array.isArray(product.features) 
            ? product.features 
            : JSON.parse(product.features || '[]');

        const card = document.createElement('div');
        card.className = 'product-card';
        card.setAttribute('data-mode', 'buy');
        card.setAttribute('data-buy-price', product.buy_price);
        card.setAttribute('data-rent-price', product.rent_price);

        card.innerHTML = `
            <div class="card-shine"></div>
            <div class="card-glow"></div>
            
            <div class="badge-container">
                <span class="product-badge ${product.badge || ''}">
                    <i class="fas fa-${getBadgeIcon(product.badge)}"></i> ${product.badge || ''}
                </span>
            </div>

            <div class="product-image-wrapper">
                <div class="product-glow"></div>
                <div class="product-image">
                    <img src="${product.image}" alt="${product.name}" loading="lazy">
                </div>
                <div class="product-reflection">
                    <img src="${product.image}" alt="" loading="lazy">
                </div>
                <div class="product-overlay">
                    <button class="quick-view-btn">
                        <i class="fas fa-eye"></i>
                        <span>Quick View</span>
                    </button>
                </div>
            </div>

            <div class="product-info">
                <div class="product-header">
                    <span class="product-category">${product.category}</span>
                    <div class="product-rating">
                        <div class="stars">
                            ${generateStars(product.rating || 4.5)}
                        </div>
                        <span class="rating-count">(${product.rating_count || 0})</span>
                    </div>
                </div>

                <h3 class="product-name">${product.name}</h3>

                <div class="buy-content">
                    <div class="product-price-row">
                        <div class="price-container">
                            <span class="price-current">₹${Number(product.buy_price).toLocaleString()}</span>
                            ${product.old_price ? `<span class="price-old">₹${Number(product.old_price).toLocaleString()}</span>` : ''}
                        </div>
                        ${product.old_price ? `<span class="savings-badge">Save ₹${Number(product.old_price - product.buy_price).toLocaleString()}</span>` : ''}
                    </div>
                    <p class="product-description">${product.description_buy || 'Premium quality product'}</p>
                </div>

                <div class="rent-content" style="display: none;">
                    <div class="product-price-row">
                        <div class="price-container">
                            <span class="price-current">₹${Number(product.rent_price).toLocaleString()}</span>
                            <span class="rent-period">/month</span>
                        </div>
                        <span class="savings-badge" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">Min. 6 Months</span>
                    </div>
                    <p class="product-description">${product.description_rent || 'Affordable rental option'}</p>
                </div>

                <div class="feature-chips">
                    ${features.map(f => `
                        <span class="feature-chip">
                            <i class="fas fa-check"></i>
                            <span>${f}</span>
                        </span>
                    `).join('')}
                </div>

                <button class="add-to-cart-btn">
                    <span class="btn-content">
                        <i class="fas fa-shopping-bag"></i>
                        <span>Add to Cart</span>
                    </span>
                    <div class="btn-glow"></div>
                </button>
            </div>
        `;

        productsGrid.appendChild(card);
    });
}

// Load Services
async function loadServices() {
    const services = await fetchFromAPI('/public/services');
    if (!services || services.length === 0) return;

    // Load into first services grid
    const servicesGrids = document.querySelectorAll('.services-grid');
    if (servicesGrids.length === 0) return;

    const mainGrid = servicesGrids[0];
    mainGrid.innerHTML = '';

    // Show first 3 in main grid, rest in hidden
    const visibleServices = services.slice(0, 3);
    const hiddenServices = services.slice(3);

    visibleServices.forEach(service => {
        const features = Array.isArray(service.features) 
            ? service.features 
            : JSON.parse(service.features || '[]');

        const card = createServiceCard(service, features);
        mainGrid.appendChild(card);
    });

    // Hidden services
    if (hiddenServices.length > 0) {
        const hiddenSection = document.getElementById('hiddenServices');
        if (hiddenSection) {
            const hiddenGrid = hiddenSection.querySelector('.services-grid');
            if (hiddenGrid) {
                hiddenGrid.innerHTML = '';
                hiddenServices.forEach(service => {
                    const features = Array.isArray(service.features) 
                        ? service.features 
                        : JSON.parse(service.features || '[]');
                    const card = createServiceCard(service, features);
                    hiddenGrid.appendChild(card);
                });
            }
        } else {
            // Create hidden section if doesn't exist
            const hiddenSection = document.createElement('div');
            hiddenSection.className = 'hidden-services';
            hiddenSection.id = 'hiddenServices';
            hiddenSection.innerHTML = `
                <div class="services-grid">
                    ${hiddenServices.map(service => {
                        const features = Array.isArray(service.features) 
                            ? service.features 
                            : JSON.parse(service.features || '[]');
                        return createServiceCardHTML(service, features);
                    }).join('')}
                </div>
            `;
            
            // Insert after main services grid
            mainGrid.parentElement.appendChild(hiddenSection);
            
            // Add show more button
            const showMoreContainer = document.createElement('div');
            showMoreContainer.className = 'show-more-container';
            showMoreContainer.innerHTML = `
                <button class="show-more-btn" id="showMoreBtn" onclick="toggleServices()">
                    <span class="btn-text">Show More Services</span>
                    <i class="fas fa-chevron-down"></i>
                </button>
            `;
            hiddenSection.parentElement.appendChild(showMoreContainer);
        }
    }
}

function createServiceCard(service, features) {
    const card = document.createElement('div');
    card.className = 'service-card';
    card.innerHTML = `
        <div class="service-image-wrapper">
            <div class="service-glow"></div>
            <div class="service-image">
                <img src="${service.image}" alt="${service.title}" loading="lazy">
            </div>
        </div>
        <div class="service-info">
            <h3 class="service-title">${service.title}</h3>
            <p class="service-description">${service.description || 'Professional service'}</p>
            <ul class="service-features">
                ${features.map(f => `<li><i class="fas fa-check"></i> ${f}</li>`).join('')}
            </ul>
            <a href="#contact" class="service-cta-btn">
                <span>Book Now</span>
                <i class="fas fa-arrow-right"></i>
            </a>
        </div>
    `;
    return card;
}

function createServiceCardHTML(service, features) {
    return `
        <div class="service-card">
            <div class="service-image-wrapper">
                <div class="service-glow"></div>
                <div class="service-image">
                    <img src="${service.image}" alt="${service.title}" loading="lazy">
                </div>
            </div>
            <div class="service-info">
                <h3 class="service-title">${service.title}</h3>
                <p class="service-description">${service.description || 'Professional service'}</p>
                <ul class="service-features">
                    ${features.map(f => `<li><i class="fas fa-check"></i> ${f}</li>`).join('')}
                </ul>
                <a href="#contact" class="service-cta-btn">
                    <span>Book Now</span>
                    <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        </div>
    `;
}

// Load Site Settings (Phone, WhatsApp, etc.)
async function loadSiteSettings() {
    const settings = await fetchFromAPI('/public/site-settings');
    if (!settings) return;

    // Update phone links
    const phoneLinks = document.querySelectorAll('a[href^="tel:"]');
    if (phoneLinks.length > 0 && settings.phone) {
        phoneLinks.forEach(link => {
            link.href = `tel:${settings.phone}`;
        });
    }

    // Update WhatsApp links
    const whatsappLinks = document.querySelectorAll('a[href*="wa.me"]');
    if (whatsappLinks.length > 0 && settings.whatsapp) {
        whatsappLinks.forEach(link => {
            link.href = `https://wa.me/${settings.whatsapp}`;
        });
    }

    // Update floating WhatsApp button
    const whatsappBtn = document.getElementById('whatsappChat');
    if (whatsappBtn && settings.whatsapp) {
        whatsappBtn.href = `https://wa.me/${settings.whatsapp}?text=Hi%2C%20I'm%20interested%20in%20your%20AC%20products`;
    }
}

// Helper Functions
function getBadgeIcon(badge) {
    const icons = {
        'best-seller': 'fire',
        'new': 'sparkles',
        'hot': 'fire-flame-curved'
    };
    return icons[badge] || 'star';
}

function generateStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalf = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0);
    
    let stars = '';
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star"></i>';
    }
    if (hasHalf) {
        stars += '<i class="fas fa-star-half-alt"></i>';
    }
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star"></i>';
    }
    return stars;
}

// Toggle Services
function toggleServices() {
    const hiddenServices = document.getElementById('hiddenServices');
    const showMoreBtn = document.getElementById('showMoreBtn');
    if (!hiddenServices || !showMoreBtn) return;

    const btnText = showMoreBtn.querySelector('.btn-text');
    
    if (hiddenServices.classList.contains('show')) {
        hiddenServices.classList.remove('show');
        btnText.textContent = 'Show More Services';
        showMoreBtn.classList.remove('active');
    } else {
        hiddenServices.classList.add('show');
        btnText.textContent = 'Show Less';
        showMoreBtn.classList.add('active');
    }
}

// Initialize All
document.addEventListener('DOMContentLoaded', async function() {
    // Load all dynamic content
    await Promise.all([
        loadHeroSection(),
        loadMarquee(),
        loadProducts(),
        loadServices(),
        loadSiteSettings()
    ]);

    // Initialize existing functionality
    if (typeof initNavbar === 'function') initNavbar();
    if (typeof initMobileMenu === 'function') initMobileMenu();
    if (typeof initCounterAnimation === 'function') initCounterAnimation();
    if (typeof initSmoothScroll === 'function') initSmoothScroll();
    if (typeof initCartButtons === 'function') initCartButtons();
    if (typeof initWhatsAppButton === 'function') initWhatsAppButton();
    if (typeof initPurchaseToggle === 'function') initPurchaseToggle();
    if (typeof initHeroParallax === 'function') initHeroParallax();
});
