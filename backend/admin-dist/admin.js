/**
 * ANSH AIR COOL - Admin Panel JavaScript
 * Production-Ready Admin Dashboard Logic
 */

const API_BASE = window.location.origin + '/api';

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('admin_token');
    if (!token) {
        window.location.href = '/admin';
        return null;
    }
    return token;
}

// API request helper
async function apiRequest(endpoint, method = 'GET', body = null) {
    const token = checkAuth();
    if (!token) return;

    const options = {
        method,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        
        if (response.status === 401) {
            localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_user');
            window.location.href = '/admin';
            return null;
        }

        const data = await response.json();
        
        if (!response.ok) {
            showToast(data.error || 'Request failed', 'error');
            return null;
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast('Network error occurred', 'error');
        return null;
    }
}

// Toast notifications
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type === 'error' ? 'error' : ''}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Navigation
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function() {
        const section = this.dataset.section;
        
        // Update active menu
        document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        
        // Show section
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.getElementById(section).classList.add('active');
        
        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            hero: 'Hero Section',
            marquee: 'Marquee Text',
            products: 'Products',
            services: 'Services',
            settings: 'Site Settings',
            contacts: 'Contacts'
        };
        document.getElementById('pageTitle').textContent = titles[section];
        
        // Load section data
        loadSectionData(section);
        
        // Close mobile sidebar
        document.getElementById('sidebar').classList.remove('mobile-open');
    });
});

// Load section data
function loadSectionData(section) {
    switch(section) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'hero':
            loadHeroSettings();
            break;
        case 'marquee':
            loadMarqueeItems();
            break;
        case 'products':
            loadProducts();
            break;
        case 'services':
            loadServices();
            break;
        case 'settings':
            loadSiteSettings();
            break;
        case 'contacts':
            loadContacts();
            break;
    }
}

// Dashboard
async function loadDashboard() {
    const data = await apiRequest('/admin/dashboard');
    if (data) {
        document.getElementById('statProducts').textContent = data.active_products;
        document.getElementById('statServices').textContent = data.active_services;
        document.getElementById('statContacts').textContent = data.total_contacts;
        document.getElementById('statUnread').textContent = data.unread_contacts;
    }
}

// Hero Settings
async function loadHeroSettings() {
    const data = await apiRequest('/admin/hero');
    if (data) {
        document.getElementById('trustBadge_text').value = data.trust_badge_text || '';
        document.getElementById('titleLine1').value = data.title_line_1 || '';
        document.getElementById('titleLine2').value = data.title_line_2 || '';
        document.getElementById('titleLine3').value = data.title_line_3 || '';
        document.getElementById('subtitle').value = data.subtitle || '';
        document.getElementById('stat1Number').value = data.stat_1_number || 0;
        document.getElementById('stat1Suffix').value = data.stat_1_suffix || '';
        document.getElementById('stat1Label').value = data.stat_1_label || '';
        document.getElementById('stat2Number').value = data.stat_2_number || 0;
        document.getElementById('stat2Suffix').value = data.stat_2_suffix || '';
        document.getElementById('stat2Label').value = data.stat_2_label || '';
        document.getElementById('stat3Number').value = data.stat_3_number || 0;
        document.getElementById('stat3Suffix').value = data.stat_3_suffix || '';
        document.getElementById('stat3Label').value = data.stat_3_label || '';
        document.getElementById('feature1').value = data.quick_feature_1 || '';
        document.getElementById('feature2').value = data.quick_feature_2 || '';
        document.getElementById('feature3').value = data.quick_feature_3 || '';
    }
}

async function saveHeroSettings() {
    const data = {
        trust_badge_text: document.getElementById('trustBadge_text').value,
        title_line_1: document.getElementById('titleLine1').value,
        title_line_2: document.getElementById('titleLine2').value,
        title_line_3: document.getElementById('titleLine3').value,
        subtitle: document.getElementById('subtitle').value,
        stat_1_number: document.getElementById('stat1Number').value,
        stat_1_suffix: document.getElementById('stat1Suffix').value,
        stat_1_label: document.getElementById('stat1Label').value,
        stat_2_number: document.getElementById('stat2Number').value,
        stat_2_suffix: document.getElementById('stat2Suffix').value,
        stat_2_label: document.getElementById('stat2Label').value,
        stat_3_number: document.getElementById('stat3Number').value,
        stat_3_suffix: document.getElementById('stat3Suffix').value,
        stat_3_label: document.getElementById('stat3Label').value,
        quick_feature_1: document.getElementById('feature1').value,
        quick_feature_2: document.getElementById('feature2').value,
        quick_feature_3: document.getElementById('feature3').value
    };

    const result = await apiRequest('/admin/hero', 'PUT', data);
    if (result) {
        showToast('Hero settings saved successfully');
    }
}

// Site Settings
async function loadSiteSettings() {
    const data = await apiRequest('/admin/site-settings');
    if (data) {
        document.getElementById('siteName').value = data.site_name || '';
        document.getElementById('sitePhone').value = data.phone || '';
        document.getElementById('siteWhatsapp').value = data.whatsapp || '';
        document.getElementById('siteEmail').value = data.email || '';
        document.getElementById('siteAddress').value = data.address || '';
    }
}

async function saveSiteSettings() {
    const data = {
        site_name: document.getElementById('siteName').value,
        phone: document.getElementById('sitePhone').value,
        whatsapp: document.getElementById('siteWhatsapp').value,
        email: document.getElementById('siteEmail').value,
        address: document.getElementById('siteAddress').value
    };

    const result = await apiRequest('/admin/site-settings', 'PUT', data);
    if (result) {
        showToast('Site settings saved successfully');
    }
}

// Marquee Items
async function loadMarqueeItems() {
    const items = await apiRequest('/admin/marquee');
    const tbody = document.getElementById('marqueeTable');
    tbody.innerHTML = '';
    
    if (items) {
        items.forEach(item => {
            tbody.innerHTML += `
                <tr>
                    <td>${item.order_index}</td>
                    <td><strong>${item.main_text}</strong></td>
                    <td>${item.sub_text}</td>
                    <td><span class="badge badge-${item.is_active ? 'success' : 'danger'}">${item.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td class="action-btns">
                        <button class="action-btn edit" onclick="editMarqueeItem(${item.id})"><i class="fas fa-edit"></i></button>
                        <button class="action-btn delete" onclick="deleteMarqueeItem(${item.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        });
    }
}

function showMarqueeModal(id = null) {
    // Simple prompt-based editing (can be enhanced with modal)
    const mainText = prompt('Main Text (e.g., ANSH AIR COOL):');
    if (!mainText) return;
    
    const subText = prompt('Sub Text (e.g., Premium AC Services):');
    if (!subText) return;
    
    const orderIndex = prompt('Order Index (number):', '0');
    
    const data = {
        main_text: mainText,
        sub_text: subText,
        order_index: parseInt(orderIndex) || 0,
        is_active: true
    };
    
    if (id) {
        apiRequest(`/admin/marquee/${id}`, 'PUT', data).then(() => loadMarqueeItems());
    } else {
        apiRequest('/admin/marquee', 'POST', data).then(() => loadMarqueeItems());
    }
}

async function editMarqueeItem(id) {
    showMarqueeModal(id);
}

async function deleteMarqueeItem(id) {
    if (confirm('Are you sure you want to delete this item?')) {
        await apiRequest(`/admin/marquee/${id}`, 'DELETE');
        loadMarqueeItems();
        showToast('Item deleted successfully');
    }
}

// Products
async function loadProducts() {
    const products = await apiRequest('/admin/products');
    const tbody = document.getElementById('productsTable');
    tbody.innerHTML = '';
    
    if (products) {
        products.forEach(product => {
            tbody.innerHTML += `
                <tr>
                    <td><img src="${product.image}" alt="${product.name}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px;"></td>
                    <td><strong>${product.name}</strong></td>
                    <td>${product.category}</td>
                    <td>₹${parseFloat(product.buy_price).toLocaleString()}</td>
                    <td>₹${parseFloat(product.rent_price).toLocaleString()}/mo</td>
                    <td><span class="badge badge-info">${product.badge || '-'}</span></td>
                    <td><span class="badge badge-${product.is_active ? 'success' : 'danger'}">${product.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td class="action-btns">
                        <button class="action-btn edit" onclick="editProduct(${product.id})"><i class="fas fa-edit"></i></button>
                        <button class="action-btn delete" onclick="deleteProduct(${product.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        });
    }
}

function showProductModal() {
    const name = prompt('Product Name:');
    if (!name) return;
    
    const category = prompt('Category (e.g., Split AC):');
    const buyPrice = prompt('Buy Price:');
    const rentPrice = prompt('Rent Price (per month):');
    const imageUrl = prompt('Image URL (or leave empty):', '/static/images/split-ac.jpg');
    const badge = prompt('Badge (best-seller, new, hot):', '');
    
    const data = {
        name,
        category,
        buy_price: parseFloat(buyPrice) || 0,
        rent_price: parseFloat(rentPrice) || 0,
        image: imageUrl || '/static/images/split-ac.jpg',
        badge,
        description_buy: 'Premium quality product',
        description_rent: 'Affordable rental option',
        features: ['5 Star', 'Inverter', 'Cool'],
        is_active: true,
        order_index: 0
    };
    
    apiRequest('/admin/products', 'POST', data).then(() => {
        loadProducts();
        showToast('Product created successfully');
    });
}

async function editProduct(id) {
    const products = await apiRequest('/admin/products');
    const product = products.find(p => p.id === id);
    if (!product) return;
    
    const name = prompt('Product Name:', product.name);
    if (!name) return;
    
    const buyPrice = prompt('Buy Price:', product.buy_price);
    const rentPrice = prompt('Rent Price:', product.rent_price);
    
    const data = {
        ...product,
        name,
        buy_price: parseFloat(buyPrice) || product.buy_price,
        rent_price: parseFloat(rentPrice) || product.rent_price
    };
    
    await apiRequest(`/admin/products/${id}`, 'PUT', data);
    loadProducts();
    showToast('Product updated successfully');
}

async function deleteProduct(id) {
    if (confirm('Are you sure you want to delete this product?')) {
        await apiRequest(`/admin/products/${id}`, 'DELETE');
        loadProducts();
        showToast('Product deleted successfully');
    }
}

// Services
async function loadServices() {
    const services = await apiRequest('/admin/services');
    const tbody = document.getElementById('servicesTable');
    tbody.innerHTML = '';
    
    if (services) {
        services.forEach(service => {
            tbody.innerHTML += `
                <tr>
                    <td><img src="${service.image}" alt="${service.title}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px;"></td>
                    <td><strong>${service.title}</strong></td>
                    <td><i class="fas ${service.icon}"></i> ${service.icon}</td>
                    <td>${service.order_index}</td>
                    <td><span class="badge badge-${service.is_active ? 'success' : 'danger'}">${service.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td class="action-btns">
                        <button class="action-btn edit" onclick="editService(${service.id})"><i class="fas fa-edit"></i></button>
                        <button class="action-btn delete" onclick="deleteService(${service.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        });
    }
}

function showServiceModal() {
    const title = prompt('Service Title:');
    if (!title) return;
    
    const icon = prompt('Icon Class (e.g., fa-wrench):', 'fa-wrench');
    const imageUrl = prompt('Image URL:', '/static/images/ac-installation.jpg');
    
    const data = {
        title,
        description: 'Professional service',
        image: imageUrl,
        icon,
        features: ['Feature 1', 'Feature 2'],
        is_active: true,
        order_index: 0
    };
    
    apiRequest('/admin/services', 'POST', data).then(() => {
        loadServices();
        showToast('Service created successfully');
    });
}

async function editService(id) {
    const services = await apiRequest('/admin/services');
    const service = services.find(s => s.id === id);
    if (!service) return;
    
    const title = prompt('Service Title:', service.title);
    if (!title) return;
    
    const data = {
        ...service,
        title
    };
    
    await apiRequest(`/admin/services/${id}`, 'PUT', data);
    loadServices();
    showToast('Service updated successfully');
}

async function deleteService(id) {
    if (confirm('Are you sure you want to delete this service?')) {
        await apiRequest(`/admin/services/${id}`, 'DELETE');
        loadServices();
        showToast('Service deleted successfully');
    }
}

// Contacts
async function loadContacts() {
    const contacts = await apiRequest('/admin/contacts');
    const tbody = document.getElementById('contactsTable');
    tbody.innerHTML = '';
    
    if (contacts) {
        contacts.forEach(contact => {
            tbody.innerHTML += `
                <tr>
                    <td><strong>${contact.name}</strong></td>
                    <td>${contact.email}</td>
                    <td>${contact.phone || '-'}</td>
                    <td>${contact.message ? contact.message.substring(0, 50) + '...' : '-'}</td>
                    <td>${new Date(contact.submitted_at).toLocaleDateString()}</td>
                    <td><span class="badge badge-${contact.is_read ? 'success' : 'warning'}">${contact.is_read ? 'Read' : 'Unread'}</span></td>
                    <td class="action-btns">
                        <button class="action-btn edit" onclick="markContactRead(${contact.id})"><i class="fas fa-check"></i></button>
                        <button class="action-btn delete" onclick="deleteContact(${contact.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        });
    }
}

async function markContactRead(id) {
    await apiRequest(`/admin/contacts/${id}/read`, 'PUT');
    loadContacts();
    showToast('Contact marked as read');
}

async function deleteContact(id) {
    if (confirm('Are you sure you want to delete this contact?')) {
        await apiRequest(`/admin/contacts/${id}`, 'DELETE');
        loadContacts();
        showToast('Contact deleted successfully');
    }
}

// Logout
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_user');
        window.location.href = '/admin';
    }
}

// Mobile sidebar toggle
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('mobile-open');
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    const token = checkAuth();
    if (!token) return;
    
    // Load user info
    const user = JSON.parse(localStorage.getItem('admin_user') || '{}');
    if (user.username) {
        document.getElementById('username').textContent = user.username;
        document.getElementById('userAvatar').textContent = user.username.charAt(0).toUpperCase();
    }
    
    // Load dashboard
    loadDashboard();
});
