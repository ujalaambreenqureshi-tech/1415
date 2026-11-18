/**
 * Jumma Couture by Noman - Core Interactive Engine
 * Handles Color Swatches, Multi-Currency, Shopify Sync, Cart Drawer, Wishlist,
 * and 100% Full Advance Payment Checkout.
 */

// Global State
const Heritage = {
  currency: localStorage.getItem('heritage_currency') || 'PKR',
  rates: {
    PKR: 1,
    USD: 0.0036, // 1 PKR = 0.0036 USD (~278 PKR/USD)
    GBP: 0.0028,
    EUR: 0.0033,
    AED: 0.0132,
    SAR: 0.0135,
    CAD: 0.0049,
    AUD: 0.0055
  },
  symbols: {
    PKR: 'Rs. ',
    USD: '$',
    GBP: '£',
    EUR: '€',
    AED: 'AED ',
    SAR: 'SAR ',
    CAD: 'C$',
    AUD: 'A$'
  },
  cart: JSON.parse(localStorage.getItem('heritage_cart') || '[]'),
  wishlist: JSON.parse(localStorage.getItem('heritage_wishlist') || '[]')
};

// Formatting Helper
function formatPrice(pkrAmount) {
  const code = Heritage.currency;
  const rate = Heritage.rates[code] || 1;
  const converted = pkrAmount * rate;
  const symbol = Heritage.symbols[code] || '';

  if (code === 'PKR') {
    return symbol + Math.round(converted).toLocaleString();
  }
  return symbol + converted.toFixed(2);
}

// Update all prices across the DOM
function refreshDOMPrices() {
  document.querySelectorAll('[data-price-pkr]').forEach(el => {
    const pkr = parseFloat(el.getAttribute('data-price-pkr'));
    if (!isNaN(pkr)) {
      el.textContent = formatPrice(pkr);
    }
  });
}

// Currency Switcher
function setCurrency(code) {
  if (Heritage.rates[code]) {
    Heritage.currency = code;
    localStorage.setItem('heritage_currency', code);
    refreshDOMPrices();
    renderCart();
    showToast(`Currency updated to ${code}`);
  }
}

// Toast Notifications
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span>✨</span> <div>${message}</div>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Cart Engine
function saveCart() {
  localStorage.setItem('heritage_cart', JSON.stringify(Heritage.cart));
  updateCartBadges();
}

function updateCartBadges() {
  const totalCount = Heritage.cart.reduce((sum, item) => sum + item.qty, 0);
  document.querySelectorAll('.cart-badge-count').forEach(el => {
    el.textContent = totalCount;
  });
}

function addToCart(item) {
  // item: { id, slug, title, price, image, color, size, qty }
  const existingIdx = Heritage.cart.findIndex(
    i => i.slug === item.slug && i.color === item.color && i.size === item.size
  );

  if (existingIdx > -1) {
    Heritage.cart[existingIdx].qty += (item.qty || 1);
  } else {
    Heritage.cart.push({
      ...item,
      qty: item.qty || 1
    });
  }

  saveCart();
  renderCart();
  openCartDrawer();
  showToast(`Added ${item.title} (${item.color}) to Bag`);
}

function buyNow(item) {
  // Add item directly and redirect to checkout
  const existingIdx = Heritage.cart.findIndex(
    i => i.slug === item.slug && i.color === item.color && i.size === item.size
  );

  if (existingIdx > -1) {
    Heritage.cart[existingIdx].qty += (item.qty || 1);
  } else {
    Heritage.cart.push({
      ...item,
      qty: item.qty || 1
    });
  }

  saveCart();
  renderCart();
  window.location.href = '/checkout';
}

function updateCartQty(idx, delta) {
  if (Heritage.cart[idx]) {
    Heritage.cart[idx].qty += delta;
    if (Heritage.cart[idx].qty <= 0) {
      Heritage.cart.splice(idx, 1);
    }
    saveCart();
    renderCart();
  }
}

function removeFromCart(idx) {
  if (Heritage.cart[idx]) {
    Heritage.cart.splice(idx, 1);
    saveCart();
    renderCart();
  }
}

function openCartDrawer() {
  const overlay = document.getElementById('cart-drawer-overlay');
  const drawer = document.getElementById('cart-drawer');
  if (overlay && drawer) {
    overlay.classList.add('active');
    drawer.classList.add('active');
  }
}

function closeCartDrawer() {
  const overlay = document.getElementById('cart-drawer-overlay');
  const drawer = document.getElementById('cart-drawer');
  if (overlay && drawer) {
    overlay.classList.remove('active');
    drawer.classList.remove('active');
  }
}

function renderCart() {
  const container = document.getElementById('drawer-items-list');
  const subtotalEl = document.getElementById('drawer-subtotal-val');
  if (!container) return;

  if (Heritage.cart.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px 10px; color: var(--color-text-muted);">
        <p style="font-size: 32px; margin-bottom: 12px;">🛍️</p>
        <p style="font-weight: 600; font-size: 16px;">Your Shopping Bag is empty</p>
        <p style="font-size: 13px; margin-top: 6px;">Discover our handcrafted ethnic luxury collections.</p>
        <a href="/shop" class="btn-primary" style="margin-top: 20px; display: inline-block; font-size: 11px;">Explore Catalog</a>
      </div>
    `;
    if (subtotalEl) subtotalEl.textContent = formatPrice(0);
    return;
  }

  let subtotal = 0;
  let html = '';

  Heritage.cart.forEach((item, idx) => {
    const itemTotal = item.price * item.qty;
    subtotal += itemTotal;
    html += `
      <div style="display: flex; gap: 14px; border-bottom: 1px solid var(--color-border); padding-bottom: 14px;">
        <img src="/static/images/${item.image}" alt="${item.title}" style="width: 70px; height: 90px; object-fit: cover; border-radius: 4px; border: 1px solid var(--color-border);" />
        <div style="flex: 1; display: flex; flex-direction: column;">
          <h4 style="font-size: 13px; font-weight: 600; color: var(--color-burgundy);">${item.title}</h4>
          <span style="font-size: 11px; color: var(--color-text-muted);">Color: <strong>${item.color}</strong> | Size: <strong>${item.size}</strong></span>
          <span style="font-size: 13px; font-weight: 700; color: var(--color-burgundy); margin-top: 4px;">${formatPrice(item.price)}</span>
          <div style="display: flex; align-items: center; justify-content: space-between; margin-top: auto;">
            <div style="display: flex; border: 1px solid var(--color-border); border-radius: 3px;">
              <button onclick="updateCartQty(${idx}, -1)" style="border:none; background:none; width: 24px; cursor: pointer;">-</button>
              <span style="padding: 0 8px; font-size: 12px; font-weight: 600;">${item.qty}</span>
              <button onclick="updateCartQty(${idx}, 1)" style="border:none; background:none; width: 24px; cursor: pointer;">+</button>
            </div>
            <button onclick="removeFromCart(${idx})" style="border:none; background:none; color: #999; font-size: 11px; cursor: pointer; text-decoration: underline;">Remove</button>
          </div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
  if (subtotalEl) subtotalEl.textContent = formatPrice(subtotal);

  // If on checkout page or full cart page, update their respective displays
  const cartPageSubtotal = document.getElementById('cart-page-subtotal');
  if (cartPageSubtotal) cartPageSubtotal.textContent = formatPrice(subtotal);
}

// Wishlist Engine
function toggleWishlist(slug, title) {
  const idx = Heritage.wishlist.indexOf(slug);
  if (idx > -1) {
    Heritage.wishlist.splice(idx, 1);
    showToast(`Removed ${title} from Wishlist`);
  } else {
    Heritage.wishlist.push(slug);
    showToast(`Saved ${title} to Wishlist`);
  }
  localStorage.setItem('heritage_wishlist', JSON.stringify(Heritage.wishlist));
  updateWishlistBadges();
  document.querySelectorAll(`[data-wishlist-slug="${slug}"]`).forEach(btn => {
    btn.classList.toggle('active', Heritage.wishlist.includes(slug));
  });
}

function updateWishlistBadges() {
  document.querySelectorAll('.wishlist-badge-count').forEach(el => {
    el.textContent = Heritage.wishlist.length;
  });
}

// Color Swatch Swapper (Section 4 Strict Requirement)
function initColorSwatches() {
  document.querySelectorAll('.color-swatches, .pdp-swatches').forEach(swatchContainer => {
    const dots = swatchContainer.querySelectorAll('.color-swatch-dot, .pdp-swatch-dot');
    dots.forEach(dot => {
      dot.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        dots.forEach(d => d.classList.remove('active'));
        this.classList.add('active');

        const newImage = this.getAttribute('data-image');
        const colorName = this.getAttribute('data-color-name');
        const variantId = this.getAttribute('data-variant-id');

        // Look for image target in same card or on PDP
        const card = this.closest('.product-card');
        if (card) {
          const img = card.querySelector('.product-img-wrap img');
          if (img && newImage) {
            img.src = `/static/images/${newImage}`;
          }
        }

        // On PDP
        const pdpMainImg = document.getElementById('pdp-main-image');
        if (pdpMainImg && newImage) {
          pdpMainImg.src = `/static/images/${newImage}`;
        }
        const pdpSelectedColor = document.getElementById('pdp-selected-color-name');
        if (pdpSelectedColor && colorName) {
          pdpSelectedColor.textContent = colorName;
        }
        const pdpVariantInput = document.getElementById('pdp-selected-variant-id');
        if (pdpVariantInput && variantId) {
          pdpVariantInput.value = variantId;
        }
      });
    });
  });
}

// Quick Search Modal Toggle
function toggleSearchModal() {
  const modal = document.getElementById('search-modal');
  if (modal) {
    modal.classList.toggle('active');
    if (modal.classList.contains('active')) {
      const input = modal.querySelector('.search-input');
      if (input) input.focus();
    }
  }
}

// Lookbook Quick Bundle Add
function addLookbookBundle() {
  const bundleItems = [
    { slug: 'anarkali-suit-set', title: 'Peach Embroidered Anarkali', price: 23999, image: 'anarkali-peach.jpg', color: 'Peach Blossom', size: 'M', qty: 1 },
    { slug: 'embellished-organza-saree', title: 'Champagne Tissue Dupatta', price: 8999, image: 'saree-champagne.jpg', color: 'Champagne Gold', size: 'Free Size', qty: 1 },
    { slug: 'zari-velvet-potli-bag', title: 'Zari Velvet Potli', price: 2499, image: 'potli-gold.jpg', color: 'Muted Gold', size: 'Standard', qty: 1 }
  ];

  bundleItems.forEach(item => {
    Heritage.cart.push(item);
  });
  saveCart();
  renderCart();
  openCartDrawer();
  showToast('Celebration Look added to Bag!');
}

// Picture Slideshow / Carousel Engine
let currentSlideIndex = 0;
let slideInterval = null;

function showSlide(index) {
  const slides = document.querySelectorAll('.slideshow-slide');
  const dots = document.querySelectorAll('.slide-dot');
  if (slides.length === 0) return;

  if (index >= slides.length) currentSlideIndex = 0;
  else if (index < 0) currentSlideIndex = slides.length - 1;
  else currentSlideIndex = index;

  slides.forEach((s, idx) => {
    s.classList.toggle('active', idx === currentSlideIndex);
  });

  dots.forEach((d, idx) => {
    d.classList.toggle('active', idx === currentSlideIndex);
  });
}

function moveSlide(delta) {
  showSlide(currentSlideIndex + delta);
  resetSlideTimer();
}

function setSlide(index) {
  showSlide(index);
  resetSlideTimer();
}

function startSlideTimer() {
  if (slideInterval) clearInterval(slideInterval);
  slideInterval = setInterval(() => {
    moveSlide(1);
  }, 4500);
}

function resetSlideTimer() {
  startSlideTimer();
}

// Document Ready Initialization
document.addEventListener('DOMContentLoaded', () => {
  // Sync badges
  updateCartBadges();
  updateWishlistBadges();
  renderCart();
  refreshDOMPrices();
  initColorSwatches();
  startSlideTimer();

  // Pause slideshow on hover
  const wrapper = document.querySelector('.slideshow-wrapper');
  if (wrapper) {
    wrapper.addEventListener('mouseenter', () => clearInterval(slideInterval));
    wrapper.addEventListener('mouseleave', () => startSlideTimer());
  }

  // Currency select listeners
  document.querySelectorAll('.currency-select').forEach(sel => {
    sel.value = Heritage.currency;
    sel.addEventListener('change', (e) => setCurrency(e.target.value));
  });

  // Mobile drawer toggle
  const mobileToggle = document.querySelector('.mobile-toggle');
  const mainNav = document.querySelector('.main-nav');
  if (mobileToggle && mainNav) {
    mobileToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      mainNav.classList.toggle('active');
      if (mainNav.classList.contains('active')) {
        mainNav.style.display = 'block';
      } else {
        mainNav.style.display = 'none';
      }
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 1024 && !mainNav.contains(e.target) && !mobileToggle.contains(e.target)) {
        mainNav.classList.remove('active');
        mainNav.style.display = 'none';
      }
    });
  }
});

