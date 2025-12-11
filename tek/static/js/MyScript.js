// State Management
document.addEventListener("DOMContentLoaded", function () {
    currentUser = JSON.parse(localStorage.getItem("currentUser"));
    updateAuthButtons(currentUser);
    renderBlogPosts();
    initBlogModalTriggers();
});
let cart = [];
let currentUser = null;
let currentPage = 'home';
let currentProduct = null;
let currentProductReviews = [];
let authMode = 'login';
let products = {};
let organizedProducts = {}; 
const blogPosts = [];
// Sample Products Data
function buildStarIcons(rating = 0) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5 ? 1 : 0;
    const emptyStars = 5 - fullStars - halfStar;

    return `${'★'.repeat(fullStars)}${halfStar ? '☆' : ''}${'☆'.repeat(emptyStars)}`;
}

function renderRatingMarkup(rating = 0, count = 0) {
    const safeRating = Number(rating) || 0;
    const safeCount = Number(count) || 0;
    const stars = buildStarIcons(safeRating);
    return `
        <div class="flex items-center gap-2 text-yellow-400">
            <span class="text-lg">${stars}</span>
            <span class="text-xs text-gray-500">${safeRating.toFixed(1)} (${safeCount} نظر)</span>
        </div>
    `;
}


// تفکیک محصولات بر اساس دسته‌ها و ویژگی‌ها
// 📦 دریافت محصولات از API
async function fetchProducts() {
    try {
        const response = await fetch('/products/api/list/');
        if (!response.ok) throw new Error("API response error");
        const data = await response.json();
        
        return Array.isArray(data) ? data : [];
    } catch (error) {
       
        return [];
    }
}
// 🧩 تفکیک محصولات بر اساس ویژگی‌ها
function organizeProducts(products) {
    const organized = {
        laptops: [],
        computers: [],
        accessories: [],
        discounted: [],
        newProducts: [],
        lowStock: [],
        brands: {}, // مثلا { "Apple": [...], "Dell": [...] }
        customFilters: {} // برای فیلترهای دلخواه
    };

    products.forEach(p => {
    const categorySlugs = (p.categories || [])
        .map(c => c?.slug?.toLowerCase())
        .filter(Boolean);

    // دسته‌بندی لپتاپ
    if (categorySlugs.includes("lt"))
        organized.laptops.push(p);

    // دسته‌بندی کامپیوتر
    if (categorySlugs.includes("pc"))
        organized.computers.push(p);

    // دسته‌بندی لوازم جانبی (مثال)
    if (categorySlugs.includes("accessories") || categorySlugs.includes("accessory"))
        organized.accessories.push(p);

    // تخفیف‌دارها
    if (p.discount && p.discount > 0)
        organized.discounted.push(p);

    // جدیدها
    if (p.id < 50)
        organized.newProducts.push(p);

    // موجودی کم
    if (p.stock_quantity && p.stock_quantity < 5)
        organized.lowStock.push(p);

    // برند
    if (p.brand?.title) {
        const brandName = p.brand.title;
        if (!organized.brands[brandName]) organized.brands[brandName] = [];
        organized.brands[brandName].push(p);
    }
});

    return organized;
}

// 🧱 رندر محصولات
function renderProducts(products) {
    renderProductSection('discountedProducts', products.discounted.slice(0, 8));
    renderProductSection('newProducts', products.newProducts.slice(0, 8));
    renderProductSection('lowStockProducts', products.lowStock.slice(0, 8));
    renderProductSection('laptopsList', products.laptops);
    renderProductSection('computersList', products.computers);
    renderProductSection('accessoriesList', products.accessories);

}


// 🚀 راه‌اندازی
async function init() {
    const data = await fetchProducts();
    products = organizeProducts(data); // مقداردهی سراسری
    renderProducts(products);
    updateCartBadge?.();
}

// اجرای اولیه
init();

// 🎨 تابع رندر هر بخش
function renderProductSection(elementId, productList) {
    const container = document.getElementById(elementId);
    if (!container) return;

    // تعیین رنگ‌های مخصوص هر دسته‌بندی
    let cardClass = 'bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700';
    let priceColor = 'text-[#008B8B]';
    let buttonClass = 'btn-primary';
    let hoverEffect = 'hover:shadow-lg hover:shadow-[#008B8B]/20';

    if (elementId === 'laptopsList') {
        cardClass = 'bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-blue-200 dark:border-blue-700/50';
        priceColor = 'text-blue-600 dark:text-blue-400';
        buttonClass = 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white';
        hoverEffect = 'hover:shadow-xl hover:shadow-blue-500/30 hover:scale-105';
    } else if (elementId === 'computersList') {
        cardClass = 'bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border-red-200 dark:border-red-700/50';
        priceColor = 'text-red-600 dark:text-red-400';
        buttonClass = 'bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 text-white';
        hoverEffect = 'hover:shadow-xl hover:shadow-red-500/30 hover:scale-105';
    } else if (elementId === 'accessoriesList') {
        cardClass = 'bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 border-green-200 dark:border-green-700/50';
        priceColor = 'text-green-600 dark:text-green-400';
        buttonClass = 'bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white';
        hoverEffect = 'hover:shadow-xl hover:shadow-green-500/30 hover:scale-105';
    }
    
    // اعمال رنگ‌های مخصوص برای محصولات تخفیف‌دار، جدید و موجودی محدود در صفحه اصلی
    if (elementId === 'discountedProducts') {
        cardClass = 'bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-blue-200 dark:border-blue-700/50';
        priceColor = 'text-blue-600 dark:text-blue-400';
        buttonClass = 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white';
        hoverEffect = 'hover:shadow-xl hover:shadow-blue-500/30 hover:scale-105';
    } else if (elementId === 'newProducts') {
        cardClass = 'bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border-red-200 dark:border-red-700/50';
        priceColor = 'text-red-600 dark:text-red-400';
        buttonClass = 'bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 text-white';
        hoverEffect = 'hover:shadow-xl hover:shadow-red-500/30 hover:scale-105';
    } else if (elementId === 'lowStockProducts') {
        cardClass = 'bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 border-green-200 dark:border-green-700/50';
        priceColor = 'text-green-600 dark:text-green-400';
        buttonClass = 'bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white';
        hoverEffect = 'hover:shadow-xl hover:shadow-green-500/30 hover:scale-105';
    }
    container.innerHTML = productList.map(product => {
        const ratingMarkup = renderRatingMarkup(product.average_rating, product.review_count);
        const hasDiscount = product.discount && product.discount > 0;
        const isLowStock = product.stock_quantity && product.stock_quantity < 5;
        const isOutOfStock = !product.stock_quantity || product.stock_quantity <= 0;

        return `
        <div class="product-card ${cardClass} rounded-xl shadow-lg overflow-hidden border transition-all duration-300 ${hoverEffect}">
          <div class="relative">
            <img src="${product.main_image}" alt="${product.name}" class="w-full h-48 object-cover">
            
            ${hasDiscount ? '<span class="absolute top-3 left-3 bg-gradient-to-r from-red-500 to-pink-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg">تخفیف ویژه</span>' : ''}
            ${isLowStock ? '<span class="absolute top-3 left-3 bg-gradient-to-r from-orange-500 to-red-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg">موجودی محدود</span>' : ''}
            ${isOutOfStock ? '<span class="absolute top-3 left-3 bg-gray-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg">ناموجود</span>' : ''}
            
            <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
          </div>

          <div class="p-5">
            <h4 class="font-bold mb-3 text-lg dark:text-white line-clamp-2">${product.name}</h4>
            
            <div class="flex items-center gap-2 mb-4">
              ${hasDiscount ? `<span class="text-gray-400 line-through text-sm">${product.originalPrice.toLocaleString()} تومان</span>` : ''}
              <span class="${priceColor} font-bold text-xl">${(hasDiscount ? product.finalPrice : product.originalPrice).toLocaleString()} تومان</span>
            </div>

            <div class="flex items-center justify-between mb-4">
              <p class="text-sm text-gray-600 dark:text-gray-400">موجودی: ${product.stock_quantity || 0} عدد</p>
               ${ratingMarkup}
            </div>

            ${isOutOfStock
                ? '<div class="text-center text-red-600 font-bold">ناموجود</div>'
                : `<div class="flex gap-2">
                    <button onclick="viewProduct('${product.id}')" class="flex-1 bg-white/70 dark:bg-gray-700/70 hover:bg-white dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 px-3 py-2 rounded-lg transition-all duration-300 text-sm font-medium backdrop-blur-sm">مشاهده</button>
                    <button onclick="addToCart('${product.id}')" class="flex-1 ${buttonClass} px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300 shadow-md hover:shadow-lg">افزودن</button>
                  </div>`}
          </div>
        </div>
        `;
    }).join('');
}


let currentBlogFilter = 'all';
let displayedBlogPosts = 6;

function updateFeaturedBlogPost(post) {
    const featuredImage = document.getElementById('blogFeaturedImage');
    const featuredCategory = document.getElementById('blogFeaturedCategory');
    const featuredTag = document.getElementById('blogFeaturedTag');
    const featuredDate = document.getElementById('blogFeaturedDate');
    const featuredTitle = document.getElementById('blogFeaturedTitle');
    const featuredExcerpt = document.getElementById('blogFeaturedExcerpt');
    const featuredAuthorInitial = document.getElementById('blogFeaturedAuthorInitial');
    const featuredAuthorName = document.getElementById('blogFeaturedAuthorName');
    const featuredButton = document.getElementById('blogFeaturedButton');

    if (!post || !featuredImage || !featuredCategory || !featuredTag || !featuredDate || !featuredTitle || !featuredExcerpt || !featuredAuthorInitial || !featuredAuthorName || !featuredButton) {
        return;
    }

    featuredImage.src = post.image;
    featuredImage.alt = post.title;
    featuredCategory.textContent = getCategoryName(post.category);
    featuredTag.textContent = getCategoryName(post.category);
    featuredDate.textContent = post.date;
    featuredTitle.textContent = post.title;
    featuredExcerpt.textContent = post.excerpt;
    featuredAuthorInitial.textContent = post.author.charAt(0);
    featuredAuthorName.textContent = post.author;
    featuredButton.onclick = () => openBlogPost(post);
}

function renderBlogPosts() {
    const container = document.getElementById('blogList');
    if (!container) return;

    const filteredPosts = currentBlogFilter === 'all'
        ? blogPosts
        : blogPosts.filter(post => post.category === currentBlogFilter);
     if (filteredPosts.length > 0) {
        updateFeaturedBlogPost(filteredPosts[0]);
    }

    const postsToShow = filteredPosts.slice(0, displayedBlogPosts);

    container.innerHTML = postsToShow.map(post => `
        <div class="form-glass rounded-2xl overflow-hidden hover:scale-105 transition-all duration-300 cursor-pointer" onclick="openBlogPost('${post.id}')">
          <div class="relative">
            <img src="${post.image}" alt="${post.title}" class="w-full h-48 object-cover" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'400\' height=\'250\' viewBox=\'0 0 400 250\'%3E%3Crect fill=\'%23008B8B\' width=\'400\' height=\'250\'/%3E%3Ctext x=\'200\' y=\'130\' font-family=\'Arial\' font-size=\'24\' fill=\'white\' text-anchor=\'middle\'%3EBlog Post%3C/text%3E%3C/svg%3E'; this.alt='Image failed to load';">
            <div class="absolute top-4 right-4 bg-[#008B8B] text-white px-3 py-1 rounded-full text-xs font-bold">${getCategoryName(post.category)}</div>
          </div>
          <div class="p-6">
            <h4 class="font-bold text-lg mb-3 dark:text-white line-clamp-2">${post.title}</h4>
            <p class="text-gray-600 dark:text-gray-400 mb-4 text-sm leading-relaxed line-clamp-3">${post.excerpt}</p>
            <div class="flex justify-between items-center text-sm">
              <div class="flex items-center gap-2">
                <div class="w-6 h-6 bg-gradient-to-r from-[#008B8B] to-[#006666] rounded-full flex items-center justify-center text-white text-xs font-bold">
                  ${post.author.charAt(0)}
                </div>
                <span class="text-gray-500 dark:text-gray-400">${post.author}</span>
              </div>
              <div class="flex items-center gap-4 text-gray-500 dark:text-gray-400">
                <span>${post.date}</span>
                <span>${post.comments} نظر</span>
              </div>
            </div>
          </div>
        </div>
      `).join('');
      const loadMoreBtn = document.getElementById('blogLoadMore');
    if (loadMoreBtn) {
        loadMoreBtn.style.display = displayedBlogPosts >= filteredPosts.length ? 'none' : 'inline-flex';
    }
    initBlogModalTriggers();
}

function getCategoryName(category) {
    const categoryNames = {
        'laptop': 'لپ‌تاپ',
        'computer': 'کامپیوتر',
        'gaming': 'گیمینگ',
        'guide': 'راهنما'
    };
    return categoryNames[category] || category;
}

function filterBlogPosts(category) {
    currentBlogFilter = category;
    displayedBlogPosts = 6;

    // Update active filter button
    document.querySelectorAll('.blog-filter-btn').forEach(btn => {
        btn.classList.remove('active', 'bg-[#008B8B]', 'text-white');
        btn.classList.add('glass', 'dark:text-white');
    });

    event.target.classList.remove('glass', 'dark:text-white');
    event.target.classList.add('active', 'bg-[#008B8B]', 'text-white');

    renderBlogPosts();
}

function loadMoreBlogPosts() {
    displayedBlogPosts += 6;
    renderBlogPosts();

    const filteredPosts = currentBlogFilter === 'all'
        ? blogPosts
        : blogPosts.filter(post => post.category === currentBlogFilter);

    if (displayedBlogPosts >= filteredPosts.length) {
        event.target.style.display = 'none';
    }
}

function buildBlogMetaText(post) {
    const metaParts = [];

    if (post.date) {
        metaParts.push(post.date);
    }

    if (post.rating) {
        metaParts.push(`امتیاز: ${post.rating}`);
    }

    metaParts.push(`${post.comments ?? 0} نظر`);
    return metaParts.join(' • ');
}

async function handleBlogModalTrigger(event) {
    event.preventDefault();
    const trigger = event.currentTarget;
    const fallbackData = getBlogDataFromTrigger(trigger);

    const remotePost = await fetchBlogPostContent(fallbackData.modalUrl);
    openBlogPost(remotePost || fallbackData);
}

function initBlogModalTriggers() {
    const triggers = document.querySelectorAll('[data-blog-modal="true"]');

    triggers.forEach(trigger => {
        trigger.removeEventListener('click', handleBlogModalTrigger);
        trigger.addEventListener('click', handleBlogModalTrigger);
    });
}

function getBlogDataFromTrigger(trigger) {
    const dataset = trigger.dataset || {};
    const title = dataset.blogTitle || trigger.querySelector('h4')?.textContent?.trim() || '';

    return {
        id: dataset.blogSlug || dataset.blogId || title,
        title,
        date: dataset.blogDate || '',
        excerpt: dataset.blogExcerpt || '',
        image: dataset.blogCover || trigger.querySelector('img')?.src || '',
        comments: dataset.blogComments || 0,
        rating: dataset.blogRating || '',
        modalUrl: dataset.blogModalUrl || trigger.getAttribute('href') || '',
    };
}

async function fetchBlogPostContent(url) {
    if (!url) return null;

    try {
        const response = await fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (!response.ok) return null;

        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const article = doc.querySelector('[data-blog-article]');

        if (!article) return null;

        const content = article.querySelector('[data-blog-content]');

        return {
            id: article.dataset.blogSlug || article.dataset.blogTitle,
            title: article.dataset.blogTitle || '',
            date: article.dataset.blogDate || '',
            image: article.dataset.blogCover || article.querySelector('img')?.src || '',
            excerpt: article.dataset.blogExcerpt || '',
            comments: article.dataset.blogComments || 0,
            rating: article.dataset.blogRating || '',
            content: content ? content.innerHTML : article.innerHTML,
        };
    } catch (error) {
        console.error('خطا در بارگذاری محتوای مقاله', error);
        return null;
    }
}

function openBlogPost(postOrId) {
    const resolvedPost = (typeof postOrId === 'object' && postOrId !== null)
        ? postOrId
        : blogPosts.find(p => p.id === postOrId);

    if (!resolvedPost) return;

    const placeholderImage = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300"%3E%3Crect fill="%23008B8B" width="800" height="300"/%3E%3Ctext x="400" y="160" font-family="Arial" font-size="32" fill="white" text-anchor="middle"%3EBlog Article%3C/text%3E%3C/svg%3E';
    const imageSrc = resolvedPost.image || placeholderImage;
    const authorName = resolvedPost.author || resolvedPost.title || '';
    const authorInitial = authorName ? authorName.charAt(0) : '?';
    const metaText = buildBlogMetaText(resolvedPost);
    const articleContent = resolvedPost.content || resolvedPost.excerpt || '';
    const categoryLabel = resolvedPost.category ? getCategoryName(resolvedPost.category) : '';
    const commentsText = resolvedPost.comments ?? 0;

    const blogModal = document.createElement('div');
    blogModal.className = 'modal active';
    blogModal.innerHTML = `
        <div class="modal-content p-0 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div class="form-glass rounded-2xl">
            <div class="relative">
               <img src="${imageSrc}" alt="${resolvedPost.title || ''}" class="w-full h-64 object-cover rounded-t-2xl" onerror="this.src='${placeholderImage}'; this.alt='Image failed to load';">
              <button onclick="closeBlogPost()" class="absolute top-4 left-4 glass p-3 rounded-xl text-white hover:bg-white/20 transition-all">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
           ${categoryLabel ? `<div class="absolute bottom-4 right-4 bg-[#008B8B] text-white px-4 py-2 rounded-full text-sm font-bold">${categoryLabel}</div>` : ''}
            </div>
            
            <div class="p-8">
              <div class="flex items-center gap-4 mb-6">
                <div class="w-12 h-12 bg-gradient-to-r from-[#008B8B] to-[#006666] rounded-full flex items-center justify-center text-white text-lg font-bold">
                  ${authorInitial}
                </div>
                <div>
                  <p class="font-bold dark:text-white">${authorName}</p>
                  <p class="text-sm text-gray-500">${metaText}</p>
                </div>
              </div>
              
                 <h1 class="text-4xl font-bold mb-6 dark:text-white leading-tight">${resolvedPost.title || ''}</h1>
              
               ${resolvedPost.excerpt ? `<p class="text-lg text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">${resolvedPost.excerpt}</p>` : ''}
              <div class="prose prose-lg max-w-none dark:prose-invert">${articleContent}</div>
              
              <div class="border-t pt-6 mt-8">
                <div class="flex items-center justify-between">
                  <div class="flex gap-4">
                    <button class="glass px-4 py-2 rounded-xl hover:bg-white/20 transition-all flex items-center gap-2 dark:text-white">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                      </svg>
                      پسندیدن
                    </button>
                    <button class="glass px-4 py-2 rounded-xl hover:bg-white/20 transition-all flex items-center gap-2 dark:text-white">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"></path>
                      </svg>
                      اشتراک‌گذاری
                    </button>
                  </div>
                  <span class="text-sm text-gray-500">${commentsText} نظر</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
     blogModal.addEventListener('click', (event) => {
        if (event.target === blogModal) {
            closeBlogPost();
        }
    });
    document.body.appendChild(blogModal);
}

function closeBlogPost() {
    const modal = document.querySelector('.modal:last-child');
    if (modal) {
        modal.remove();
    }
}
// وقتی محصولات از API میاد
async function initPage() {
    const productsArray = await fetchProducts(); // همه محصولات
    organizedProducts = organizeProducts(productsArray); // دسته‌بندی
    renderProducts(organizedProducts); // رندر همه بخش‌ها
}

// findProduct جدید
function findProduct(id) {
    const allProducts = [
        ...(products.laptops || []),
        ...(products.computers || []),
        ...(products.accessories || [])
    ];
    return allProducts.find(p => p.id === Number(id));
}
// function viewProduct(id) {
//     showLoading();
//     setTimeout(() => {
//         currentProduct = findProduct(id);
//         if (!currentProduct) return;

//         document.getElementById('modalProductName').textContent = currentProduct.name;
//         document.getElementById('modalProductPrice').textContent = `${currentProduct.price.toLocaleString()} تومان`;
//         document.getElementById('modalProductDesc').textContent = currentProduct.description;
//         document.getElementById('modalProductImage').src = currentProduct.image;
//         document.getElementById('modalProductImage').alt = currentProduct.name;
        
//         const specsSelect = document.getElementById('modalProductSpecs');
//         specsSelect.innerHTML = currentProduct.specs.map(spec => `<option>${spec}</option>`).join('');

//         const reviewsContainer = document.getElementById('modalProductReviews');
//         reviewsContainer.innerHTML = currentProduct.reviews.map(review => `
//           <div class="bg-gray-50 p-4 rounded-lg">
//             <div class="flex justify-between items-center mb-2">
//               <span class="font-bold">${review.user}</span>
//               <span class="text-yellow-500">${'⭐'.repeat(review.rating)}</span>
//             </div>
//             <p class="text-gray-600">${review.comment}</p>
//           </div>
//         `).join('');

//         document.getElementById('productModal').classList.add('active');
//         hideLoading();
//     }, 300);
// }
// ==========================
//       LocalStorage
// ==========================

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function loadCart() {
    const saved = localStorage.getItem('cart');
    if (saved) {
        cart = JSON.parse(saved);
        updateCartBadge();
    }
}

loadCart();

// ==========================
//       افزودن محصول
// ==========================

function addToCart(id) {
    const product = findProduct(id);
    if (!product) return;

    const existingItem = cart.find(i => String(i.id) === String(id));

    // جلوگیری از بیش از موجودی
    if (existingItem) {
        if (existingItem.quantity >= product.stock_quantity) {
            showNotification("موجودی کافی نیست");
            return;
        }
        existingItem.quantity++;
    } else {

        if (product.stock_quantity <= 0) {
            showNotification("این محصول ناموجود است");
            return;
        }

        // ذخیره صحیح تصویر (اصلی)
        const imageUrl = fixImagePath(product.main_image);

        cart.push({
    id: product.id,
    name: product.name,
    price: product.price,                  // قیمت اصلی
    originalPrice: product.originalPrice,  // قیمت قبل تخفیف
    finalPrice: product.finalPrice,        // قیمت با تخفیف
    discount: product.discount || 0,       // مبلغ تخفیف
    discountPercent: product.discount 
        ? Math.round((product.discount / product.originalPrice) * 100)
        : 0,
    stock_quantity: product.stock_quantity,
    image: fixImagePath(product.main_image),
    quantity: 1
});

    }

    saveCart();
    updateCartBadge();
    showNotification("محصول به سبد اضافه شد");
}

// ==========================
//       نمایش سبد خرید
// ==========================

function openCart() {
    const cartItems = document.getElementById("cartItems");
    const cartTotal = document.getElementById("cartTotal");

    if (cart.length === 0) {
        cartItems.innerHTML = `<p class="text-center text-gray-500">سبد خرید شما خالی است</p>`;
        cartTotal.textContent = "0 تومان";
    } 
    else {
        cartItems.innerHTML = cart.map(item => `

            <div class="flex items-center gap-4 bg-gray-50 p-4 rounded-lg">

                <img src="${item.image}" class="w-20 h-20 rounded object-cover" alt="${item.name}">

                <div class="flex-1">
                    <h4 class="font-bold">${item.name}</h4>

                    ${
                        item.discountPercent > 0 
                        ? `
                            <p class="text-[#008B8B] font-bold">${item.finalPrice.toLocaleString()} تومان</p>
                            <p class="text-red-500 text-sm line-through">${item.originalPrice.toLocaleString()} تومان</p>
                            <p class="text-green-600 text-xs">${item.discountPercent}% تخفیف</p>
                          `
                        : `
                            <p class="text-[#008B8B] font-bold">${item.price.toLocaleString()} تومان</p>
                          `
                    }
                </div>

                <div class="flex items-center gap-2">
                    <button class="dec-btn w-8 h-8 bg-gray-200 rounded" data-id="${item.id}">−</button>
                    <span class="font-bold">${item.quantity}</span>
                    <button class="inc-btn w-8 h-8 bg-gray-200 rounded" data-id="${item.id}">+</button>
                </div>

                <button class="remove-btn text-red-500" data-id="${item.id}">حذف</button>
            </div>

        `).join('');

        // -------------------
        // محاسبه مجموع صحیح
        // -------------------
        const total = cart.reduce((sum, item) => {
            const price = item.discountPercent > 0 ? item.finalPrice : item.price;
            return sum + price * item.quantity;
        }, 0);

        cartTotal.textContent = `${total.toLocaleString()} تومان`;
    }

    document.getElementById("cartModal").classList.add("active");
    attachCartEvents();
}

// ==========================
//       رویدادها
// ==========================

function attachCartEvents() {
    document.querySelectorAll(".inc-btn").forEach(btn => {
        btn.onclick = () => updateCartQuantity(btn.dataset.id, 1);
    });

    document.querySelectorAll(".dec-btn").forEach(btn => {
        btn.onclick = () => updateCartQuantity(btn.dataset.id, -1);
    });

    document.querySelectorAll(".remove-btn").forEach(btn => {
        btn.onclick = () => removeFromCart(btn.dataset.id);
    });
}

function closeCart() {
    document.getElementById("cartModal").classList.remove("active");
}

// ==========================
//    کم / زیاد کردن تعداد
// ==========================

function updateCartQuantity(id, change) {
    const item = cart.find(i => String(i.id) === String(id));
    if (!item) return;

    item.quantity += change;

    if (item.quantity <= 0) {
        removeFromCart(id);
        return;
    }

    saveCart();
    updateCartBadge();
    openCart();
    
}

// ==========================
//           حذف
// ==========================

function removeFromCart(id) {
    cart = cart.filter(i => String(i.id) !== String(id));
    saveCart();
    updateCartBadge();
    openCart();
}

// ==========================
//          Badge
// ==========================

function updateCartBadge() {
    const badge = document.getElementById("cartBadge");
     if (!badge) return;
    const totalItems = cart.reduce((s, i) => s + i.quantity, 0);
    badge.textContent = totalItems;
}

function applyDiscount() {
    const code = document.getElementById('discountCode').value.trim();
    if (code === 'TECH20') {
        const newPrice = Math.floor(currentProduct.price * 0.8);
        document.getElementById('modalProductPrice').textContent = `${newPrice.toLocaleString()} تومان`;
        showNotification('کد تخفیف با موفقیت اعمال شد!');
    } else {
        showNotification('کد تخفیف نامعتبر است');
    }
}

function checkout() {
    if (cart.length === 0) {
        showNotification('سبد خرید شما خالی است!', 'error');
        return;
    }

    if (!currentUser) {
        closeCart();
        openAuthModal('login');
        showNotification('برای تکمیل خرید ابتدا وارد شوید', 'error');
        return;
    }

    // بدون navigateTo → مستقیم کاربر را به پروفایل می‌بریم
    window.location.href = "/accounts/profile/";
}

// function openPaymentModal() {
//     const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
//     document.getElementById('paymentTotal').textContent = `${total.toLocaleString()} تومان`;
//     document.getElementById('paymentModal').classList.add('active');
// }

// function closePaymentModal() {
//     document.getElementById('paymentModal').classList.remove('active');
// }

// function processPayment(method) {
//     showNotification('در حال انتقال به درگاه پرداخت...', 'info');
//     closePaymentModal();

//     // Create payment gateway simulation
//     const paymentGateway = document.createElement('div');
//     paymentGateway.className = 'modal active';
//     paymentGateway.innerHTML = `
//         <div class="modal-content p-0 w-full max-w-lg">
//           <div class="form-glass p-8 rounded-2xl">
//             <div class="text-center mb-8">
//               <div class="w-20 h-20 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
//                 <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
//                 </svg>
//               </div>
//               <h3 class="text-2xl font-bold dark:text-white mb-2">درگاه پرداخت امن</h3>
//               <p class="text-gray-600 dark:text-gray-400">پرداخت با ${method}</p>
//             </div>
            
//             <div class="bg-gradient-to-r from-[#008B8B]/10 to-[#006666]/10 p-4 rounded-xl mb-6 border border-[#008B8B]/20">
//               <div class="flex justify-between items-center mb-2">
//                 <span class="font-medium dark:text-white">مبلغ قابل پرداخت:</span>
//                 <span class="text-xl font-bold text-[#008B8B]" id="gatewayTotal">0 تومان</span>
//               </div>
//               <div class="text-sm text-gray-600 dark:text-gray-400">
//                 شماره پیگیری: ${Math.random().toString(36).substr(2, 9).toUpperCase()}
//               </div>
//             </div>
            
//             ${method === 'کارت بانکی' ? `
//               <form onsubmit="completePayment(event, '${method}')" class="space-y-4">
//                 <div>
//                   <label class="block font-bold mb-2 dark:text-white">شماره کارت</label>
//                   <input type="text" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white" placeholder="1234-5678-9012-3456" maxlength="19" oninput="formatCardNumber(this)">
//                 </div>
//                 <div class="grid grid-cols-2 gap-4">
//                   <div>
//                     <label class="block font-bold mb-2 dark:text-white">تاریخ انقضا</label>
//                     <input type="text" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white" placeholder="MM/YY" maxlength="5" oninput="formatExpiry(this)">
//                   </div>
//                   <div>
//                     <label class="block font-bold mb-2 dark:text-white">CVV2</label>
//                     <input type="password" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white" placeholder="123" maxlength="4">
//                   </div>
//                 </div>
//                 <div>
//                   <label class="block font-bold mb-2 dark:text-white">رمز دوم (اختیاری)</label>
//                   <input type="password" class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white" placeholder="رمز دوم کارت">
//                 </div>
//                 <button type="submit" class="btn-primary btn-modern w-full py-4 rounded-xl text-lg font-bold">پرداخت</button>
//               </form>
//             ` : method === 'کیف پول دیجیتال' ? `
//               <div class="space-y-4">
//                 <div class="text-center">
//                   <div class="w-32 h-32 mx-auto mb-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
//                     <svg class="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//                       <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
//                     </svg>
//                   </div>
//                   <p class="text-gray-600 dark:text-gray-400 mb-4">لطفاً اپلیکیشن کیف پول خود را باز کرده و QR کد زیر را اسکن کنید</p>
//                   <div class="w-40 h-40 mx-auto bg-white p-4 rounded-xl border-2 border-gray-200">
//                     <div class="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center">
//                       <span class="text-gray-500 text-sm">QR Code</span>
//                     </div>
//                   </div>
//                 </div>
//                 <button onclick="completePayment(event, '${method}')" class="btn-primary btn-modern w-full py-4 rounded-xl text-lg font-bold">تأیید پرداخت</button>
//               </div>
//             ` : method === 'اقساط' ? `
//               <div class="space-y-4">
//                 <div class="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-xl border border-yellow-200 dark:border-yellow-700">
//                   <h4 class="font-bold text-yellow-800 dark:text-yellow-200 mb-2">شرایط خرید اقساطی</h4>
//                   <ul class="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
//                     <li>• حداقل مبلغ خرید: 10 میلیون تومان</li>
//                     <li>• تعداد اقساط: 3، 6، 9، 12 ماه</li>
//                     <li>• کارمزد: 2% ماهانه</li>
//                     <li>• نیاز به ضامن معتبر</li>
//                   </ul>
//                 </div>
//                 <form onsubmit="completePayment(event, '${method}')" class="space-y-4">
//                   <div>
//                     <label class="block font-bold mb-2 dark:text-white">تعداد اقساط</label>
//                     <select required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white">
//                       <option value="">انتخاب کنید</option>
//                       <option value="3">3 قسط (کارمزد 6%)</option>
//                       <option value="6">6 قسط (کارمزد 12%)</option>
//                       <option value="9">9 قسط (کارمزد 18%)</option>
//                       <option value="12">12 قسط (کارمزد 24%)</option>
//                     </select>
//                   </div>
//                   <div>
//                     <label class="block font-bold mb-2 dark:text-white">کد ملی</label>
//                     <input type="text" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white" placeholder="کد ملی 10 رقمی" maxlength="10">
//                   </div>
//                   <button type="submit" class="btn-primary btn-modern w-full py-4 rounded-xl text-lg font-bold">ادامه فرآیند</button>
//                 </form>
//               </div>
//             ` : `
//               <div class="space-y-4">
//                 <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-xl border border-green-200 dark:border-green-700">
//                   <h4 class="font-bold text-green-800 dark:text-green-200 mb-2">پرداخت در محل تحویل</h4>
//                   <p class="text-sm text-green-700 dark:text-green-300">سفارش شما ثبت شده و هنگام تحویل پرداخت خواهید کرد.</p>
//                 </div>
//                 <div>
//                   <label class="block font-bold mb-2 dark:text-white">آدرس تحویل</label>
//                   <select required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white">
//                     <option value="">انتخاب آدرس</option>
//                     ${currentUser && currentUser.addresses ? currentUser.addresses.map(addr => `<option value="${addr}">${addr}</option>`).join('') : '<option value="آدرس پیش‌فرض">آدرس پیش‌فرض</option>'}
//                   </select>
//                 </div>
//                 <div>
//                   <label class="block font-bold mb-2 dark:text-white">زمان تحویل ترجیحی</label>
//                   <select required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white">
//                     <option value="">انتخاب کنید</option>
//                     <option value="صبح">صبح (9-12)</option>
//                     <option value="عصر">عصر (14-17)</option>
//                     <option value="شب">شب (18-21)</option>
//                   </select>
//                 </div>
//                 <button onclick="completePayment(event, '${method}')" class="btn-primary btn-modern w-full py-4 rounded-xl text-lg font-bold">ثبت سفارش</button>
//               </div>
//             `}
            
//             <div class="flex justify-center mt-6">
//               <button onclick="cancelPayment()" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-sm">انصراف از پرداخت</button>
//             </div>
//           </div>
//         </div>
//       `;

//     document.body.appendChild(paymentGateway);

//     // Set total amount
//     const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
//     document.getElementById('gatewayTotal').textContent = `${total.toLocaleString()} تومان`;
// }

function formatCardNumber(input) {
    let value = input.value.replace(/\D/g, '');
    value = value.replace(/(\d{4})(?=\d)/g, '$1-');
    input.value = value;
}

function formatExpiry(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length >= 2) {
        value = value.substring(0, 2) + '/' + value.substring(2, 4);
    }
    input.value = value;
}

// function completePayment(e, method) {
//     e.preventDefault();

//     showNotification('در حال پردازش پرداخت...', 'info');

//     setTimeout(() => {
//         // Simulate payment processing
//         const success = Math.random() > 0.1; // 90% success rate

//         if (success) {
//             // Add purchases to user profile
//             const purchaseDate = new Date().toLocaleDateString('fa-IR');
//             const purchaseItems = cart.map(item => ({
//                 ...item,
//                 purchaseDate,
//                 paymentMethod: method,
//                 status: 'پرداخت شده',
//                 trackingCode: Math.random().toString(36).substr(2, 9).toUpperCase()
//             }));

//             if (currentUser) {
//                 currentUser.purchases = [...(currentUser.purchases || []), ...purchaseItems];
//             }

//             showNotification(`پرداخت با ${method} موفقیت‌آمیز بود! کد پیگیری: ${purchaseItems[0].trackingCode}`, 'success');
//             cart = [];
//             updateCartBadge();
//             closeCart();
//             cancelPayment();
            
//             // Update profile if currently viewing
//             if (currentPage === 'profile') {
//                 renderProfile();
//             }
//         } else {
//             showNotification('پرداخت ناموفق بود. لطفاً دوباره تلاش کنید.', 'error');
//         }
//     }, 3000);
// }

// function cancelPayment() {
//     const modal = document.querySelector('.modal:last-child');
//     if (modal) {
//         modal.remove();
//     }
// }



// Handle browser back/forward buttons
// window.addEventListener('popstate', function (event) {
//     if (event.state && event.state.page) {
//         navigateTo(event.state.page, false);
//     } else {
//         // Default to home if no state
//         navigateTo('home', false);
//     }
// });

// // Set initial history state
// window.addEventListener('load', function () {
//     history.replaceState({ page: 'home' }, '', '/');
// });
//======================================================================
const iranProvinces = {
    "تهران": ["تهران", "ری", "اسلامشهر", "شمیرانات", "پردیس", "ورامین"],
    "اصفهان": ["اصفهان", "نجف‌آباد", "کاشان", "خمینی‌شهر", "شاهین‌شهر"],
    "خراسان رضوی": ["مشهد", "نیشابور", "سبزوار", "تربت جام"],
    "فارس": ["شیراز", "مرودشت", "کازرون", "داراب"],
    "آذربایجان شرقی": ["تبریز", "مراغه", "مرند"]
};
let userAddressesCache = [];
function renderProfile(addressesFromServer = null) {
    const userAddresses = document.getElementById("userAddresses");
    const addresses = addressesFromServer;
    if (userAddresses && Array.isArray(addresses)) {
        renderAddresses(addresses);
    }
    /* ==========================================================
       2) نمایش لیست خریدهای قبلی
    ========================================================== */
    const userPurchases = document.getElementById("userPurchases");
    const purchaseCountElement = document.getElementById("purchaseCount");

    if (userPurchases && purchaseCountElement) {
        if (!currentUser || !currentUser.purchases || currentUser.purchases.length === 0) {
            purchaseCountElement.textContent = "0 خرید";
            userPurchases.innerHTML = `
                <p class="text-gray-500 dark:text-gray-300">هنوز هیچ خریدی ثبت نشده است.</p>
            `;
        } else {
            purchaseCountElement.textContent = `${currentUser.purchases.length} خرید`;

            userPurchases.innerHTML = currentUser.purchases.map(p => `
                <div class="bg-gray-100 dark:bg-gray-800 p-4 rounded-xl">
                    <p class="font-bold">${p.title || "خرید"}</p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">تاریخ: ${p.purchaseDate}</p>
                    <p class="font-bold text-[#008B8B]">${p.price.toLocaleString()} تومان</p>
                </div>
            `).join("");
        }
    }

    /* ==========================================================
       3) نمایش آمار خرید
    ========================================================== */
    const totalPurchases = document.getElementById("totalPurchases");
    const totalSpent = document.getElementById("totalSpent");
    const lastPurchase = document.getElementById("lastPurchase");

    if (currentUser && currentUser.purchases && currentUser.purchases.length > 0) {
        const purchases = currentUser.purchases;

        totalPurchases.textContent = purchases.length;

        const total = purchases.reduce((sum, p) => sum + (p.price || 0), 0);
        totalSpent.textContent = `${total.toLocaleString()} تومان`;

        lastPurchase.textContent = purchases[purchases.length - 1].purchaseDate;
    } else {
        totalPurchases.textContent = "0";
        totalSpent.textContent = "0 تومان";
        lastPurchase.textContent = "-";
    }
}

function handleAddressSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const addressId = form.dataset.addressId;
    const title = document.getElementById('addressTitle').value;
    const province = document.getElementById('addressProvince').value;
    const city = document.getElementById('addressCity').value;
    const fullAddress = document.getElementById('addressFull').value;
    const postal = document.getElementById('addressPostal').value;

    const payload = {
        title: title,
        province: province,
        city: city,
        full_address: fullAddress,
        postal_code: postal
    };

    const url = addressId ? `/accounts/address/${addressId}/update/` : '/accounts/add_address/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
           'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
           showNotification(data.message || 'آدرس با موفقیت ذخیره شد!', 'success');
            closeAddressModal();
            userAddressesCache = data.addresses || [];
            renderAddresses(userAddressesCache);
        } else {
            showNotification(data.message || 'خطا در ارسال درخواست', 'error');
        }
    })
    .catch(error => {
        console.error('خطا:', error);
        showNotification('خطا در ارسال درخواست', 'error');
    });
}

function deleteAddress(addressId) {
    fetch(`/accounts/address/${addressId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message || 'آدرس حذف شد', 'success');
            userAddressesCache = data.addresses || [];
            renderAddresses(userAddressesCache);
        } else {
            showNotification(data.message || 'خطا در حذف آدرس', 'error');
        }
    })
    .catch(error => {
        console.error('خطا:', error);
        showNotification('خطا در حذف آدرس', 'error');
    });
}

function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    return csrfToken;
}

// تابع برای نمایش آدرس‌ها
function renderAddresses(addresses = null) {
    const userAddresses = document.getElementById("userAddresses");

     if (!userAddresses) return;

    const data = Array.isArray(addresses) ? addresses : userAddressesCache;

    if (!Array.isArray(data) || data.length === 0) {
        if (addresses === null) {
            fetch('/accounts/get_addresses/')
                .then(response => response.json())
                .then(res => {
                    userAddressesCache = res.addresses || [];
                    renderAddresses(userAddressesCache);
                })
                .catch(error => {
                    console.error('Error fetching addresses:', error);
                    userAddresses.innerHTML = `<p class="text-gray-500 dark:text-gray-300">خطا در بارگذاری آدرس‌ها</p>`;
                });
        } else {
            userAddresses.innerHTML = `<p class="text-gray-500 dark:text-gray-300">هیچ آدرسی ثبت نشده است.</p>`;
        }
        return;
    }
userAddressesCache = data;
    userAddresses.innerHTML = data.map(addr => `
        <div class="bg-gray-100 dark:bg-gray-800 p-3 rounded-xl">
            <p class="font-bold">${addr.title || "عنوان ندارد"}</p>
            <p class="text-sm">${addr.full_address || "آدرس کامل ندارد"}</p>
            <p class="text-sm">${addr.city || ""}, ${addr.province || ""} - کد پستی: ${addr.postal_code || ""}</p>
            <div class="flex gap-2 mt-2">
                <button onclick="openAddressModal({id: ${addr.id}, title: '${(addr.title || "").replace(/'/g, "&#39;")}', province: '${(addr.province || "").replace(/'/g, "&#39;")}', city: '${(addr.city || "").replace(/'/g, "&#39;")}', full_address: '${(addr.full_address || "").replace(/'/g, "&#39;")}', postal_code: '${(addr.postal_code || "").replace(/'/g, "&#39;")}'})" class="px-3 py-1 bg-blue-500 text-white rounded-lg text-sm">ویرایش</button>
                <button onclick="deleteAddress(${addr.id})" class="px-3 py-1 bg-red-500 text-white rounded-lg text-sm">حذف</button>
            </div>
        </div>
    `).join("");
}

function addAddress() {
    openAddressModal();
}

function openAddressModal(address = null) {
    const addressModal = document.createElement('div');
    addressModal.className = 'modal active';
    const titleValue = address?.title || '';
    const provinceValue = address?.province || '';
    const cityValue = address?.city || '';
    const fullAddressValue = address?.full_address || '';
    const postalValue = address?.postal_code || '';
    const isEdit = Boolean(address?.id);
    addressModal.innerHTML = `
        <div class="modal-content p-0 w-full max-w-md">
          <div class="form-glass p-8 rounded-2xl">
            <div class="flex justify-between items-center mb-8">
             <h3 class="text-2xl font-bold dark:text-white">${isEdit ? 'ویرایش آدرس' : 'افزودن آدرس جدید'}</h3>
              <button onclick="closeAddressModal()" class="glass p-2 hover:bg-white/20 rounded-xl transition-all duration-300 text-gray-500 hover:text-gray-700">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <form onsubmit="handleAddressSubmit(event)" data-address-id="${address?.id || ''}" class="space-y-6">
              <div>
                <label class="block font-bold mb-2 dark:text-white">عنوان آدرس</label>
                <input type="text" id="addressTitle" value="${titleValue}" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400" placeholder="مثال: منزل، محل کار">
              </div>
              
              <div>
                <label class="block font-bold mb-2 dark:text-white">استان</label>
                   <input type="text" id="addressProvince" value="${provinceValue}" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white" placeholder="استان">
              </div>
              
              <div>
                <label class="block font-bold mb-2 dark:text-white">شهر</label>
             <input type="text" id="addressCity" value="${cityValue}" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400" placeholder="نام شهر">
              </div>
              
              <div>
                <label class="block font-bold mb-2 dark:text-white">آدرس کامل</label>
                <textarea id="addressFull" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400 h-24 resize-none" placeholder="آدرس کامل شامل خیابان، کوچه، پلاک و واحد">${fullAddressValue}</textarea>
              </div>
              
              <div>
                <label class="block font-bold mb-2 dark:text-white">کد پستی</label>
               <input type="text" id="addressPostal" value="${postalValue}" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400" placeholder="کد پستی 10 رقمی" maxlength="10">
              </div>
              
             <button type="submit" class="btn-primary btn-modern w-full py-4 rounded-xl text-lg font-bold">${isEdit ? 'ذخیره تغییرات' : 'افزودن آدرس'}
            </form>
          </div>
        </div>
      `;

    document.body.appendChild(addressModal);
}

function closeAddressModal() {
    const modal = document.querySelector('.modal:last-child');
    if (modal) {
        modal.remove();
    }
}




function subscribeNewsletter(e) {
    e.preventDefault();
    showNotification('با موفقیت در خبرنامه عضو شدید!');
    e.target.reset();
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showNotification(message, type = 'info') {
    // Play notification sound
    playNotificationSound(type);

    const notification = document.createElement('div');
    const typeStyles = {
        success: 'bg-gradient-to-r from-green-500 to-emerald-500',
        error: 'bg-gradient-to-r from-red-500 to-pink-500',
        warning: 'bg-gradient-to-r from-yellow-500 to-orange-500',
        info: 'bg-gradient-to-r from-[#008B8B] to-[#006666]'
    };

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    // Check if there are existing notifications and stack them
    const existingNotifications = document.querySelectorAll('.notification-toast');
    const topOffset = 24 + (existingNotifications.length * 80); // 24px base + 80px per notification

    notification.className = `notification-toast fixed right-6 ${typeStyles[type]} text-white px-6 py-4 rounded-xl shadow-2xl z-[9999] flex items-center gap-3 min-w-[320px] max-w-[400px] transform translate-x-full transition-all duration-300 backdrop-blur-sm`;
    notification.style.top = `${topOffset}px`;
    notification.innerHTML = `
        <span class="text-xl flex-shrink-0">${icons[type]}</span>
        <span class="flex-1 font-medium text-sm leading-relaxed">${message}</span>
        <button onclick="removeNotification(this.parentElement)" class="text-white/80 hover:text-white transition-colors flex-shrink-0 p-1 hover:bg-white/10 rounded-lg">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto remove
    setTimeout(() => {
        removeNotification(notification);
    }, 4000);
}

function removeNotification(notification) {
    if (!notification || !notification.parentElement) return;

    notification.style.transform = 'translateX(100%)';
    notification.style.opacity = '0';

    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
            // Reposition remaining notifications
            repositionNotifications();
        }
    }, 300);
}

function repositionNotifications() {
    const notifications = document.querySelectorAll('.notification-toast');
    notifications.forEach((notification, index) => {
        const topOffset = 24 + (index * 80);
        notification.style.top = `${topOffset}px`;
    });
}

function playNotificationSound(type) {
    // Create audio context for notification sounds
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();

        const frequencies = {
            success: [523.25, 659.25, 783.99], // C5, E5, G5
            error: [349.23, 293.66], // F4, D4
            warning: [440, 554.37], // A4, C#5
            info: [523.25, 659.25] // C5, E5
        };

        const freq = frequencies[type] || frequencies.info;

        freq.forEach((frequency, index) => {
            setTimeout(() => {
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();

                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);

                oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
                oscillator.type = 'sine';

                gainNode.gain.setValueAtTime(0, audioContext.currentTime);
                gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
                gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.2);

                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.2);
            }, index * 100);
        });
    } catch (e) {
        // Fallback: no sound if audio context fails
        console.log('Audio not supported');
    }
}

// Dark Mode Functions
function toggleDarkMode() {
    const html = document.documentElement;
    const isDark = html.classList.contains('dark');

    if (isDark) {
        html.classList.remove('dark');
        localStorage.setItem('darkMode', 'false');
        updateDarkModeIcon(false);
    } else {
        html.classList.add('dark');
        localStorage.setItem('darkMode', 'true');
        updateDarkModeIcon(true);
    }
}

function updateDarkModeIcon(isDark) {
    const toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;
    toggle.innerHTML = isDark
        ? '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>'
        : '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>';
}

function initDarkMode() {
    const savedMode = localStorage.getItem('darkMode');
    const html = document.documentElement;

    if (savedMode === 'true') {
        html.classList.add('dark');
        updateDarkModeIcon(true);
    } else if (savedMode === 'false') {
        html.classList.remove('dark');
        updateDarkModeIcon(false);
    } else {
        updateDarkModeIcon(html.classList.contains('dark'));
        }
}

// 3D Slider Functions
let currentSlide = 0;
let currentLaptopSlide = 0;
let currentComputerSlide = 0;
let currentAccessorySlide = 0;

function changeSlide(index) {
    const products = document.querySelectorAll('.product-3d');
    const dots = document.querySelectorAll('.slider-dots .dot');

    if (!products.length) return;

    if (products[currentSlide]) products[currentSlide].classList.remove('active');
    if (dots[currentSlide]) dots[currentSlide].classList.remove('active');

    currentSlide = index % products.length;

    products[currentSlide].classList.add('active');
    dots[currentSlide].classList.add('active');
}

function autoSlide() {
    changeSlide(currentSlide + 1);
}

// --- Laptop Slider ---
function changeLaptopSlide(index) {
    const slides = document.querySelectorAll('.laptop-slide');
    const dots = document.querySelectorAll('.laptop-dots .dot');
    if (!slides.length) return;

    slides[currentLaptopSlide].classList.remove('active');
    dots[currentLaptopSlide].classList.remove('active');

    currentLaptopSlide = index % slides.length;

    slides[currentLaptopSlide].classList.add('active');
    dots[currentLaptopSlide].classList.add('active');
}

function autoLaptopSlide() {
    changeLaptopSlide(currentLaptopSlide + 1);
}

// --- Computer Slider ---
function changeComputerSlide(index) {
    const slides = document.querySelectorAll('.computer-slide');
    const dots = document.querySelectorAll('.computer-dots .dot');
    if (!slides.length) return;

    slides[currentComputerSlide].classList.remove('active');
    dots[currentComputerSlide].classList.remove('active');

    currentComputerSlide = index % slides.length;

    slides[currentComputerSlide].classList.add('active');
    dots[currentComputerSlide].classList.add('active');
}

function autoComputerSlide() {
    changeComputerSlide(currentComputerSlide + 1);
}

// --- Accessory Slider ---
function changeAccessorySlide(index) {
    const slides = document.querySelectorAll('.accessory-slide');
    const dots = document.querySelectorAll('.accessory-dots .dot');
    if (!slides.length) return;

    slides[currentAccessorySlide].classList.remove('active');
    dots[currentAccessorySlide].classList.remove('active');

    currentAccessorySlide = index % slides.length;

    slides[currentAccessorySlide].classList.add('active');
    dots[currentAccessorySlide].classList.add('active');
}

function autoAccessorySlide() {
    changeAccessorySlide(currentAccessorySlide + 1);
}

// Open category in new tab
function openCategoryInNewTab(category) {
    const baseUrl = window.location.origin + window.location.pathname;
    const categoryUrl = `${baseUrl}#${category}`;
    window.open(categoryUrl, '_blank', 'noopener,noreferrer');
}

// Scroll to products section
function scrollToProducts() {
    const productsSection = document.querySelector('.grid');
    if (productsSection) {
        productsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Enhanced Functions for New Features

// Mobile Menu Functions
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    const overlay = document.getElementById('mobileOverlay');

    menu.classList.toggle('active');
    overlay.classList.toggle('active');
}

// Search Functions
let searchTimeout;
function handleSearch(query, source = 'desktop') {
    clearTimeout(searchTimeout);
    const suggestionsId = source === 'mobile' ? 'mobileSearchSuggestions' : 'searchSuggestions';
    const suggestions = document.getElementById(suggestionsId);

    if (!suggestions) return;

    if (query.length < 2) {
        suggestions.classList.remove('active');
        return;
    }

    searchTimeout = setTimeout(() => {
        const allProducts = [
            ...(products?.laptops || []),
            ...(products?.computers || []),
            ...(products?.accessories || [])
        ];

        const normalizedQuery = (query || '').toLowerCase();
        const results = allProducts.filter(p => {
            const name = (p.name || '').toLowerCase();
            const description = (p.description || '').toLowerCase();
            const categorySlug = (p.category || p.categories?.[0]?.slug || '').toLowerCase();

            return name.includes(normalizedQuery) ||
                description.includes(normalizedQuery) ||
                categorySlug.includes(normalizedQuery);
        }).slice(0, 8);

        if (results.length === 0) {
            suggestions.innerHTML = `
            <div class="suggestion-item">
              <div class="text-center py-4">
                <div class="text-gray-500 dark:text-gray-400">محصولی یافت نشد</div>
                <div class="text-xs text-gray-400 mt-1">عبارت دیگری را امتحان کنید</div>
              </div>
            </div>
          `;
        } else {
          suggestions.innerHTML = results.map(product => {
                const image = fixImagePath(product.main_image || product.image);
                const price = product.finalPrice || product.originalPrice || product.price || 0;
                const categoryValue = product.category || product.categories?.[0]?.slug || 'accessory';

                return `
                <div class="suggestion-item" onclick="viewProduct('${product.id}'); document.getElementById('${suggestionsId}').classList.remove('active'); ${source === 'mobile' ? 'toggleMobileMenu();' : ''}">
                  <div class="flex items-center gap-3">
                    <img src="${image}" alt="${product.name}" class="w-12 h-12 rounded-lg object-cover" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'48\' height=\'48\' viewBox=\'0 0 48 48\'%3E%3Crect fill=\'%23f0f0f0\' width=\'48\' height=\'48\'/%3E%3Ctext x=\'24\' y=\'28\' font-family=\'Arial\' font-size=\'8\' fill=\'%23666\' text-anchor=\'middle\'%3ENo Image%3C/text%3E%3C/svg%3E'; this.alt='Image failed to load';">
                    <div class="flex-1">
                      <div class="font-medium text-sm dark:text-white">${product.name}</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">${price.toLocaleString()} تومان</div>
                      <div class="text-xs text-[#008B8B] mt-1">${getCategoryNameForSearch(categoryValue)}</div>
                    </div>
                    <div class="text-xs text-gray-400">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                      </svg>
                    </div>
                  </div>
                </div>
                `;
            }).join('');
        }

        suggestions.classList.add('active');
    }, 300);
}

function getCategoryNameForSearch(category) {
    const categoryNames = {
        'laptop': 'لپ‌تاپ',
        'computer': 'کامپیوتر',
        'accessory': 'لوازم جانبی'
    };
    return categoryNames[category] || category;
}

// Product Modal Enhanced Functions
let currentProductQuantity = 1;
let selectedProductColor = null;
let gallerySlideInterval = null;
let currentGallerySlide = 0;
let galleryProgressInterval = null;

function switchTab(tabName) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Add active class to clicked tab and corresponding content
    event.target.classList.add('active');
    document.getElementById(tabName + 'Tab').classList.add('active');
}

// وقتی محصول باز می‌شود
function setupColors() {
    const colorsContainer = document.getElementById('modalProductColors');
    if (!currentProduct.colors || currentProduct.colors.length === 0) {
        colorsContainer.innerHTML = "<span>هیچ رنگی موجود نیست</span>";
        selectedProductColor = null;
        return;
    }

    selectedProductColor = currentProduct.colors[0].color_name; // رنگ پیش‌فرض

    colorsContainer.innerHTML = currentProduct.colors.map((c, i) => `
        <button class="color-btn ${i === 0 ? 'active' : ''}" 
                style="background-color: ${c.color_code || '#000'}"
                onclick="selectColor(${i})" title="${c.color_name}"></button>
    `).join('');
}

function selectColor(index) {
    currentProduct.colors.forEach((c, i) => {
        document.querySelectorAll('.color-btn')[i].classList.remove('active');
    });
    document.querySelectorAll('.color-btn')[index].classList.add('active');
    selectedProductColor = currentProduct.colors[index].color_name;
}

function changeQuantity(change) {
    currentProductQuantity = Math.max(1, currentProductQuantity + change);
    document.getElementById('productQuantity').textContent = currentProductQuantity;
}

function openImageZoom(src) {
    document.getElementById('zoomedImage').src = src;
    document.getElementById('imageZoomModal').classList.add('active');
}

function closeImageZoom() {
    document.getElementById('imageZoomModal').classList.remove('active');
}

function addToWishlist() {
    showNotification('محصول به لیست علاقه‌مندی‌ها اضافه شد');
}

function openReviewModal() {
    const reviewModal = document.createElement('div');
    reviewModal.className = 'modal active';
    reviewModal.innerHTML = `
        <div class="modal-content p-0 w-full max-w-md">
          <div class="form-glass p-8 rounded-2xl">
            <div class="flex justify-between items-center mb-8">
              <h3 class="text-2xl font-bold dark:text-white">ثبت نظر جدید</h3>
              <button onclick="closeReviewModal()" class="glass p-2 hover:bg-white/20 rounded-xl transition-all duration-300 text-gray-500 hover:text-gray-700">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">نظر شما پس از تایید ادمین نمایش داده می‌شود.</p>
            <form onsubmit="submitReview(event)" class="space-y-6">
              <div>
                <label class="block font-bold mb-2 dark:text-white">نام شما</label>
                <input type="text" id="reviewerName" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400" placeholder="نام و نام خانوادگی">
              </div>
                 <div>
                <label class="block font-bold mb-2 dark:text-white">ایمیل</label>
                <input type="email" id="reviewerEmail" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400" placeholder="example@email.com">
              </div>
              <div>
                <label class="block font-bold mb-2 dark:text-white">امتیاز شما</label>
                <div class="flex gap-2 mb-2">
                  <span class="star-rating cursor-pointer text-2xl text-gray-300" data-rating="1">★</span>
                  <span class="star-rating cursor-pointer text-2xl text-gray-300" data-rating="2">★</span>
                  <span class="star-rating cursor-pointer text-2xl text-gray-300" data-rating="3">★</span>
                  <span class="star-rating cursor-pointer text-2xl text-gray-300" data-rating="4">★</span>
                  <span class="star-rating cursor-pointer text-2xl text-gray-300" data-rating="5">★</span>
                </div>
                <input type="hidden" id="reviewRating" value="5">
              </div>
              
              <div>
                <label class="block font-bold mb-2 dark:text-white">نظر شما</label>
                <textarea id="reviewComment" required class="input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400 h-32 resize-none" placeholder="نظر خود را در مورد این محصول بنویسید..."></textarea>
              </div>
              
              <button type="submit" class="btn-primary btn-modern w-full py-4 rounded-xl text-lg font-bold">ثبت نظر</button>
            </form>
          </div>
        </div>
      `;

    document.body.appendChild(reviewModal);

    // Add star rating functionality
    const stars = reviewModal.querySelectorAll('.star-rating');
    stars.forEach(star => {
        star.addEventListener('click', function () {
            const rating = parseInt(this.dataset.rating);
            document.getElementById('reviewRating').value = rating;

            stars.forEach((s, index) => {
                if (index < rating) {
                    s.classList.add('text-yellow-400');
                    s.classList.remove('text-gray-300');
                } else {
                    s.classList.remove('text-yellow-400');
                    s.classList.add('text-gray-300');
                }
            });
        });
    });

    // Set default 5 stars
    stars.forEach(star => {
        star.classList.add('text-yellow-400');
        star.classList.remove('text-gray-300');
    });
}

function closeReviewModal() {
    const modal = document.querySelector('.modal:last-child');
    if (modal) {
        modal.remove();
    }
}

async function submitReview(e) {
    e.preventDefault();
    if (!currentProduct) return;
    const name = document.getElementById('reviewerName').value;
    const email = document.getElementById('reviewerEmail').value;
    const rating = parseInt(document.getElementById('reviewRating').value);
    const comment = document.getElementById('reviewComment').value;

    try {
        const response = await fetch(`/products/api/${currentProduct.slug}/reviews/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, rating, comment })
        });

    if (!response.ok) throw new Error('NETWORK');
        const data = await response.json();

     const pendingReview = {
            display_name: name,
            rating: rating,
            comment: comment,
            created_at: new Date().toISOString(),
            pending: true
        };

     currentProductReviews = [pendingReview, ...currentProductReviews];
        renderProductReviewList(currentProductReviews);
        updateModalRating(data.average_rating ?? currentProduct.average_rating ?? 0, data.review_count ?? currentProduct.review_count ?? 0);



    closeReviewModal();
        showNotification('نظر شما ارسال شد و پس از تایید نمایش داده می‌شود.', 'success');
    } catch (error) {
        showNotification('ارسال نظر با مشکل مواجه شد. لطفاً دوباره تلاش کنید.', 'error');
    }
}


// Utility: Fix image paths from backend
function fixImagePath(img) {
if (!img) return "/static/img/no-image.png";


if (img.startsWith("http")) return img;


if (img.startsWith("/media")) return img;


return "/media/products/" + img;
}
function renderProductColors(colors) {
    const container = document.getElementById('productColorOptions');
    const selectedColorSpan = document.getElementById('selectedColor');
    container.innerHTML = '';

    if (!colors || colors.length === 0) {
        selectedColorSpan.textContent = '—';
        return;
    }

    colors.forEach((color, index) => {
        const colorEl = document.createElement('div');
        colorEl.classList.add('w-8', 'h-8', 'rounded-full', 'cursor-pointer', 'border-2', 'border-gray-300');

        if (color.color_code) {
            colorEl.style.backgroundColor = color.color_code;
        } else if (color.image) {
            colorEl.style.backgroundImage = `url(${color.image})`;
            colorEl.style.backgroundSize = 'cover';
            colorEl.style.backgroundPosition = 'center';
        }

        // انتخاب پیش‌فرض
        if (index === 0) {
            selectProductColor(color, colorEl, container);
        }

        colorEl.addEventListener('click', () => selectProductColor(color, colorEl, container));
        container.appendChild(colorEl);
    });
}

function selectProductColor(color, element, container) {
    // ذخیره رنگ انتخاب‌شده
    selectedProductColor = color.color_name || '—';

    // فقط دایره‌های همین محصول
    container.querySelectorAll('div').forEach(el => {
        el.classList.remove('border-[#008B8B]');
    });

    element.classList.add('border-[#008B8B]');

    // تغییر عکس اصلی
    if (color.image) {
        document.getElementById('modalProductImage').src = color.image;
    }

    // نمایش نام رنگ
    document.getElementById('selectedColor').textContent = selectedProductColor;
}
async function fetchProductReviews(slug) {
     try {
        const response = await fetch(`/products/api/${slug}/reviews/`);
        if (!response.ok) throw new Error('NETWORK');
        return await response.json();
    } catch (error) {
        return { reviews: [], average_rating: 0, review_count: 0 };
    }
}

function renderProductReviewList(reviews) {
    const container = document.getElementById('modalProductReviews');
    if (!container) return;

    if (!reviews || reviews.length === 0) {
        container.innerHTML = '<div class="text-gray-500 dark:text-gray-400">هنوز نظری ثبت نشده است.</div>';
        return;
    }

    container.innerHTML = reviews.map(review => {
        const name = review.display_name || review.name || 'کاربر';
        const dateText = review.created_at ? new Date(review.created_at).toLocaleDateString('fa-IR') : '';
        const pendingBadge = review.pending ? '<span class="px-2 py-1 rounded-lg bg-yellow-100 text-yellow-700 text-xs">در انتظار تایید</span>' : '';

        return `
            <div class="form-glass p-4 rounded-xl">
                <div class="flex justify-between items-center mb-3">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-gradient-to-r from-[#008B8B] to-[#006666] rounded-full flex items-center justify-center text-white font-bold">
                            ${name.charAt(0)}
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <span class="font-bold dark:text-white">${name}</span>
                                ${pendingBadge}
                            </div>
                            <div class="text-xs text-gray-500">${dateText}</div>
                        </div>
                    </div>
                    <div class="flex text-yellow-400">
                        ${'★'.repeat(review.rating || 0)}${'☆'.repeat(5 - (review.rating || 0))}
                    </div>
                </div>
                <p class="text-gray-600 dark:text-gray-400">${review.comment || ''}</p>
            </div>
        `;
    }).join('');
}

function updateModalRating(rating = 0, count = 0) {
    const container = document.getElementById('modalProductRating');
    if (!container) return;
    container.innerHTML = renderRatingMarkup(rating, count);
}

async function viewProduct(id) {
    showLoading();

    currentProduct = findProduct(id);
    if (!currentProduct) {
        hideLoading();
        console.warn('محصول مورد نظر یافت نشد');
        return;
    }

        const reviewPayload = await fetchProductReviews(currentProduct.slug);
        currentProductReviews = reviewPayload.reviews || [];
        
        currentProductQuantity = 1;
        selectedProductColor = '';

        document.getElementById('modalProductName').textContent = currentProduct.name || '';
        const priceEl = document.getElementById('modalProductPrice');
        const originalPriceEl = document.getElementById('modalOriginalPrice');
        const discountEl = document.getElementById('modalDiscount');


        const hasDiscount = currentProduct.discount && currentProduct.discount > 0;

        if (hasDiscount) {
        originalPriceEl.textContent = `${currentProduct.originalPrice.toLocaleString()} تومان`;
        originalPriceEl.style.display = 'inline-block';

        cpriceEl.textContent = `${currentProduct.finalPrice.toLocaleString()} تومان`;

        const percent = Math.round((currentProduct.discount / currentProduct.originalPrice) * 100);
        discountEl.textContent = `${percent}% تخفیف`;
        discountEl.style.display = 'inline-block';
    } else {
        priceEl.textContent = `${currentProduct.price.toLocaleString()} تومان`;
        originalPriceEl.style.display = 'none';
        discountEl.style.display = 'none';
    }

    const averageRating = reviewPayload.average_rating ?? currentProduct.average_rating ?? 0;
    const reviewCount = reviewPayload.review_count ?? currentProduct.review_count ?? 0;
    updateModalRating(averageRating, reviewCount);

    let images = [];
    if (currentProduct.gallery_images && currentProduct.gallery_images.length > 0) {
        images = [
            fixImagePath(currentProduct.main_image),
            ...currentProduct.gallery_images.map(img => fixImagePath(img.image))
        ];
    } else {
        images = [fixImagePath(currentProduct.main_image)];
    }

        document.getElementById('modalProductImage').src = images[0];
        const thumbsContainer = document.getElementById('modalProductThumbs');
        thumbsContainer.innerHTML = images
        .map((img, i) => `
                <img src="${img}" class="thumb ${i === 0 ? 'active' : ''}" onclick="changeMainImage(${i})">
            `)
             .join('');
    window.currentGalleryImages = images;

    const features = currentProduct.features || {};
    const specsContainer = document.getElementById('modalProductFeatures');
    let specsHTML = '';
    for (const key in features) {
        features[key].forEach(value => {
            specsHTML += `
                    <div class="flex justify-between">
                        <span class="text-gray-600 dark:text-gray-400">${key}:</span>
                        <span class="font-medium">${value}</span>
                    </div>
                `;
           });
    }
    specsContainer.innerHTML = specsHTML;

        
        if (currentProduct.colors && currentProduct.colors.length > 0) {
            renderProductColors(currentProduct.colors);
        }

        
        const stockEl = document.getElementById('modalStock');
        if (currentProduct.stock_quantity != null && currentProduct.stock_quantity > 0) {
            stockEl.textContent = `تنها ${currentProduct.stock_quantity} عدد باقی مانده!`;
        } else {
            stockEl.textContent = 'ناموجود';
        }

        document.getElementById('productModal').classList.add('active');
    hideLoading();
}


// لیست آدرس تصاویر را اینجا ذخیره می‌کنیم
window.currentGalleryImages = [];

function loadProductGallery(product) {

    const mainImage = document.getElementById('modalProductImage');
    const thumbsContainer = document.getElementById('modalProductThumbs');

    // ذخیره آدرس عکس‌ها برای اسلاید
    currentGalleryImages = product.gallery.map(g => g.image);

    thumbsContainer.innerHTML = "";

    // ساختن thumbnail ها
    currentGalleryImages.forEach((imgSrc, index) => {
        const thumb = document.createElement("img");
        thumb.src = imgSrc;
        thumb.className = 'thumb';
        thumb.onclick = () => changeMainImage(index);

        thumbsContainer.appendChild(thumb);
    });

    // نمایش اولین عکس
    changeMainImage(0);
}

// ⭐ تغییر عکس اصلی
function changeMainImage(index) {
    const mainImage = document.getElementById('modalProductImage');
    const thumbs = document.querySelectorAll('.thumb');

    if (!currentGalleryImages.length) return;

    // اگر index خالی بود (مثلاً برای nextGallerySlide)
    if (index === null || index === undefined) {
        index = currentGallerySlide;
    } else {
        currentGallerySlide = index;
    }

    // تغییر active
    thumbs.forEach(t => t.classList.remove('active'));
    if (thumbs[index]) thumbs[index].classList.add('active');

    // تغییر عکس اصلی
    mainImage.src = currentGalleryImages[index];
}


// ⭐ رفتن به اسلاید بعدی
function nextGallerySlide() {
    if (!currentGalleryImages.length) return;

    currentGallerySlide = (currentGallerySlide + 1) % currentGalleryImages.length;
    changeMainImage(currentGallerySlide);
}


// ⭐ توقف اتوسلاید — الان غیرفعال است
function startGalleryAutoSlide() {
    return;
}

function stopGalleryAutoSlide() {
    return;
}




function startGalleryAutoSlide() {
    // Auto-slide disabled for better user experience
    return;
}

function stopGalleryAutoSlide() {
    // Auto-slide disabled for better user experience
    return;
}

function nextGallerySlide() {
    if (!currentProduct || !currentProduct.images) return;

    currentGallerySlide = (currentGallerySlide + 1) % currentProduct.images.length;
    changeMainImage(null, currentProduct.images[currentGallerySlide], currentGallerySlide);
}

// تعداد محصول
const quantitySelect = document.getElementById('productQuantity');
quantitySelect.innerHTML = ''; // خالی کردن قبلی

const maxQty = currentProduct.stock_quantity || 1;

for (let i = 1; i <= maxQty; i++) {
    const option = document.createElement('option');
    option.value = i;
    option.textContent = i;
    quantitySelect.appendChild(option);
}

// مقدار پیش‌فرض
currentProductQuantity = 1;
quantitySelect.value = currentProductQuantity;

// وقتی کاربر تغییر داد
quantitySelect.onchange = function() {
    currentProductQuantity = parseInt(this.value);
};
// هنگام نمایش محصول
function setupQuantitySelector() {
    const quantityDisplay = document.getElementById('productQuantity');
    currentProductQuantity = 1; // مقدار پیش‌فرض
    quantityDisplay.textContent = currentProductQuantity;
}

// تغییر تعداد
function changeQuantity(amount) {
    if (!currentProduct) return;

    const maxQty = currentProduct.stock_quantity || 1;
    currentProductQuantity = Math.min(
        Math.max(1, currentProductQuantity + amount), // حداقل 1
        maxQty // حداکثر برابر موجودی
    );

    document.getElementById('productQuantity').textContent = currentProductQuantity;
}
// Enhanced Add to Cart
function addToCartFromModal() {
    if (!currentProduct) return;

    for (let i = 0; i < currentProductQuantity; i++) {
        addToCart(currentProduct.id);
    }

    showNotification(`${currentProductQuantity} عدد ${currentProduct.name} (${selectedProductColor}) به سبد خرید اضافه شد`);
    closeProductModal();
}

// Initialize on load
initDarkMode();
init();

// Auto slide every 4 seconds
setInterval(autoSlide, 4000);

// Auto slide for category sliders every 5 seconds
setInterval(() => {
    if (currentPage === 'laptops') autoLaptopSlide();
    if (currentPage === 'computers') autoComputerSlide();
    if (currentPage === 'accessories') autoAccessorySlide();
}, 5000);

// Close dropdowns when clicking outside
document.addEventListener('click', function (event) {
    if (!event.target.closest('.search-container')) {
        const desktopSuggestions = document.getElementById('searchSuggestions');
        const mobileSuggestions = document.getElementById('mobileSearchSuggestions');

        if (desktopSuggestions) desktopSuggestions.classList.remove('active');
        if (mobileSuggestions) mobileSuggestions.classList.remove('active');
    }
});
function closeProductModal() {
    // بستن مودال محصول
    const productModal = document.getElementById('productModal');
    if (productModal) productModal.classList.remove('active');

    // بستن مودال سبد خرید
    const cartModal = document.getElementById('cartModal');
    if (cartModal) cartModal.classList.remove('active');
    // بستن مودال‌ها با دکمه ESC
document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {

        // اگر مودال محصول باز است
        const productModal = document.getElementById("productModal");
        if (productModal && productModal.classList.contains("active")) {
            closeProductModal();
        }

        // اگر مودال سبد خرید باز است
        const cartModal = document.getElementById("cartModal");
        if (cartModal && cartModal.classList.contains("active")) {
            closeCart();
        }
    }
});
}










// // ارسال فرم برای تغییر رمز عبور
// async function handleRememberPassword(event) {
//     event.preventDefault();
//     const form = event.target;

//     const formData = new FormData(form);
//     const data = Object.fromEntries(formData.entries());

//     const csrfToken = getCookie('csrftoken');
//     if (!csrfToken) {
//         showNotification("CSRF token یافت نشد. صفحه را رفرش کنید.", "error");
//         return;
//     }

//     try {
//         const res = await fetch(form.action, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': csrfToken,
//                 'X-Requested-With': 'XMLHttpRequest'
//             },
//             body: JSON.stringify(data),
//             credentials: 'same-origin'
//         });

//         const result = await res.json();

//         if (res.ok && result.success) {
//             showNotification(result.message || "کد فعال‌سازی ارسال شد!", "success");
//             setTimeout(() => {
//                 window.location.href = result.redirect || '/accounts/verify/';
//             }, 1000); 
//         } else {
//             showNotification(result.message || "شماره موبایل معتبر نیست", "error");
//             if (result.errors) {
//                 console.error(result.errors); // چاپ جزئیات خطا در کنسول
//                 for (let error in result.errors) {
//                     showNotification(result.errors[error], "error");
//                 }
//             }
//         }

//     } catch (err) {
//         console.error("خطای JS:", err);
//         showNotification("خطا در ارتباط با سرور!", "error");
//     }
// }

// // ارسال فرم برای ورود
// async function handleLogin(event) {
//     event.preventDefault();

//     const form = event.target;
//     const formData = new FormData(form);
//     const data = Object.fromEntries(formData.entries());

//     const csrfToken = getCookie('csrftoken');
//     if (!csrfToken) {
//         showNotification("CSRF token یافت نشد. صفحه را رفرش کنید.", "error");
//         return;
//     }

//     try {
//         const res = await fetch(form.action, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': csrfToken,
//                 'X-Requested-With': 'XMLHttpRequest'
//             },
//             body: JSON.stringify(data),
//             credentials: 'same-origin'
//         });

//         const result = await res.json();

//         if (res.ok && result.success) {
//             localStorage.setItem("access", result.access);
//             localStorage.setItem("refresh", result.refresh);

//             showNotification(result.message || "ورود موفقیت‌آمیز!", "success");
//             setTimeout(() => {
//                 window.location.href = result.redirect || "/";
//             }, 500);

//         } else {
//             showNotification(result.message || "نام کاربری یا رمز اشتباه است", "error");
//             if (result.errors) {
//                 console.error(result.errors); 
//                 for (let error in result.errors) {
//                     showNotification(result.errors[error], "error");
//                 }
//             }
//         }

//     } catch (err) {
//         console.error("خطای JS:", err);
//         showNotification("خطا در ارتباط با سرور!", "error");
//     }
// }

// // ارسال فرم برای ثبت‌نام
// async function handleRegister(event) {
//     event.preventDefault();
//     const mobile = document.getElementById("registerMobile").value.trim();
//     const password1 = document.getElementById("registerPassword1").value.trim();
//     const password2 = document.getElementById("registerPassword2").value.trim();

//     if (!/^09\d{9}$/.test(mobile)) return showNotification("شماره موبایل صحیح نیست", "error");
//     if (password1.length < 8) return showNotification("رمز عبور حداقل ۸ کاراکتر باشد", "error");
//     if (password1 !== password2) return showNotification("رمزها مطابقت ندارند", "error");

//     try {
//         const res = await fetch("/accounts/register/", {
//             method: "POST",
//             headers: { 
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": getCookie("csrftoken"),
//                 "X-Requested-With": "XMLHttpRequest"
//             },
//             body: JSON.stringify({ mobile_number: mobile, password1, password2 })
//         });

//         const data = await res.json();

//         if (res.ok && data.success) {
//             showNotification("ثبت‌نام موفقیت‌آمیز!", "success");
//             setTimeout(() => window.location.href = data.redirect, 1000);
//         } else {
//             showNotification(data.message || "خطا در ثبت‌نام", "error");
//             if (data.errors) {
//                 console.error(data.errors); 
//                 for (let error in data.errors) {
//                     showNotification(data.errors[error], "error");
//                 }
//             }
//         }

//     } catch (err) {
//         console.error(err);
//         showNotification("خطا در ارتباط با سرور!", "error");
//     }
// }


// async function handleVerify(event) {
//     event.preventDefault();

//     const input = document.getElementById("id_active_code");
//     if (!input) return showNotification("فیلد کد فعال‌سازی پیدا نشد!", "error");
//     const code = input.value.trim();
//     if (!code) return showNotification("لطفاً کد فعال‌سازی را وارد کنید", "error");

//     const csrfToken = getCookie("csrftoken");
//     if (!csrfToken) return showNotification("CSRF token یافت نشد. صفحه را رفرش کنید.", "error");

//     try {
//         const res = await fetch("/accounts/verify/", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": csrfToken
//             },
//             body: JSON.stringify({ active_code: code }),
//             credentials: "include"
//         });

//         const data = await res.json();

//         if (res.ok && data.success) {
//             showNotification(data.message || "کد تایید شد!", "success");
//             if (data.redirect) {
//                 // هدایت به صفحه‌ی مورد نظر پس از تایید کد
//                 window.location.href = data.redirect;
//             }
//         } else {
//             showNotification(data.message || "کد فعال‌سازی اشتباه است", "error");
//         }

//     } catch (error) {
//         console.error(error);
//         showNotification("خطا در ارتباط با سرور!", "error");
//     }
// }
// async function handleChangePassword(event) {
//     event.preventDefault();

//     // گرفتن مقادیر از فیلدهای فرم
//     const password1 = document.getElementById("password1_change").value.trim();
//     const password2 = document.getElementById("password2_change").value.trim();

//     // بررسی اینکه هر دو فیلد پر شده باشند
//     if (!password1 || !password2) return showNotification("لطفاً هر دو فیلد رمز عبور را پر کنید", "error");

//     // بررسی تطابق دو رمز عبور
//     if (password1 !== password2) return showNotification("رمز عبور و تکرار آن با هم مغایرت دارند", "error");

//     const csrfToken = getCookie("csrftoken");
//     if (!csrfToken) return showNotification("CSRF token یافت نشد. صفحه را رفرش کنید.", "error");

//     // ارسال درخواست به سرور
//     try {
//         const res = await fetch("/accounts/change_password/", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": csrfToken
//             },
//             body: JSON.stringify({
//                 password1: password1,
//                 password2: password2
//             }),
//             credentials: "include"
//         });

//         const data = await res.json();

//         if (res.ok && data.success) {
//             // پیام موفقیت
//             showNotification(data.message || "رمز عبور با موفقیت تغییر کرد!", "success");
//             if (data.redirect) {
//                 // هدایت به صفحه‌ی ورود بعد از تغییر رمز
//                 window.location.href = data.redirect;
//             }
//         } else {
//             showNotification(data.message || "خطا در تغییر رمز عبور", "error");
//         }

//     } catch (error) {
//         console.error(error);
//         showNotification("خطا در ارتباط با سرور!", "error");
//     }
// }



function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.classList.toggle('active');
}

async function sendMessage(e) {
    e.preventDefault();
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.innerHTML += `<div class="bg-[#008B8B] text-white p-2 rounded mb-2">${message}</div>`;
    input.value = "";

    try {
        const res = await fetch("/aiassistant/chat/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message})
        });
        const data = await res.json();
        messagesContainer.innerHTML += `<div class="bg-gray-100 p-2 rounded mb-2">${data.response}</div>`;
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } catch (err) {
        console.error(err);
    }
}


async function simulateChatGPTResponse(userMessage) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));

    // Context-aware responses based on user message
    const message = userMessage.toLowerCase();

    if (message.includes('لپ‌تاپ') || message.includes('لپتاپ')) {
        return 'برای انتخاب بهترین لپ‌تاپ، ابتدا نیاز خود را مشخص کنید. آیا برای گیمینگ، کار اداری یا طراحی می‌خواهید؟ محدوده قیمتی شما چقدر است؟ من می‌تونم بهترین گزینه‌ها رو پیشنهاد بدم.';
    }

    if (message.includes('کامپیوتر') || message.includes('سیستم')) {
        return 'کامپیوترهای ما شامل سیستم‌های گیمینگ، اداری و حرفه‌ای هستند. بر اساس بودجه و نیازتون می‌تونم بهترین پیکربندی رو پیشنهاد بدم. چه کاری قراره باهاش انجام بدید؟';
    }

    if (message.includes('قیمت') || message.includes('تخفیف')) {
        return 'ما همیشه بهترین قیمت‌ها رو ارائه می‌دیم! محصولات تخفیف‌دار رو در صفحه اصلی ببینید. همچنین امکان خرید اقساطی هم داریم. کدوم محصول رو می‌خواید؟';
    }

    if (message.includes('گارانتی') || message.includes('خدمات')) {
        return 'تمام محصولات ما دارای گارانتی معتبر هستند. خدمات پس از فروش، تعمیرات و پشتیبانی 24 ساعته ارائه می‌دیم. برای اطلاعات بیشتر با شماره 021-12345678 تماس بگیرید.';
    }

    if (message.includes('ارسال') || message.includes('تحویل')) {
        return 'ارسال رایگان برای خریدهای بالای 5 میلیون تومان داریم. ارسال سریع در تهران ظرف 24 ساعت و سایر شهرها 2-3 روز کاری. همچنین امکان تحویل حضوری از فروشگاه‌های ما هم هست.';
    }

    if (message.includes('مشاوره') || message.includes('راهنمایی')) {
        return 'حتماً! من اینجام تا کمکتون کنم. بگید چه نوع محصولی می‌خواید و برای چه کاری؟ بودجه‌تون چقدره؟ با این اطلاعات بهترین پیشنهاد رو می‌دم.';
    }

    if (message.includes('سلام') || message.includes('درود')) {
        return 'سلام و درود! خوش اومدید به تک‌استور. چطور می‌تونم کمکتون کنم؟ اگه سوالی درباره محصولات، قیمت‌ها یا خدماتمون دارید، بپرسید.';
    }

    // Default intelligent response
    const defaultResponses = [
        'سوال جالبی پرسیدید! برای پاسخ دقیق‌تر، می‌تونید با تیم فروش ما تماس بگیرید یا از بخش محصولات سایت دیدن کنید.',
        'متوجه نشدم دقیقاً چی می‌خواید. می‌تونید سوالتون رو واضح‌تر بپرسید؟ من اینجام تا کمکتون کنم.',
        'برای این موضوع بهتره با متخصصان ما صحبت کنید. شماره تماس: 021-12345678 یا می‌تونید از چت آنلاین سایت استفاده کنید.',
        'اطلاعات کاملی درباره این موضوع در بلاگ سایت داریم. همچنین می‌تونم راهنماییتون کنم که دنبال چی می‌گردید؟'
    ];

    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
}

// =======================
// گرفتن CSRF از کوکی
// =======================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            }
        });
    }
    return cookieValue;
}

// =======================
// باز و بسته کردن مودال
// =======================
function openAuthModal(mode = "login") {
    authMode = mode;
    const modal = document.getElementById("authModal");
    if (!modal) return console.error("authModal پیدا نشد!");
    modal.classList.remove("hidden");
    updateAuthUI();
}

function closeAuthModal() {
    const modal = document.getElementById("authModal");
    if (!modal) return;
    modal.classList.add("hidden");
}

// =======================
// تغییر حالت مودال
// =======================
function toggleAuthMode(e) {
    e.preventDefault();
    authMode = authMode === "login" ? "register" : "login";
    updateAuthUI();
}

function toggleAuthMode1(e) {
    e.preventDefault();
    authMode = authMode === "login" ? "remember" : "login";
    updateAuthUI();
}

// =======================
// اعتبارسنجی فرم‌ها
// =======================
function validateForm() {
    const form = document.getElementById("authForm");
    const inputs = form.querySelectorAll("input[required]");
    for (let input of inputs) {
        if (!input.value.trim()) {
            showNotification(`لطفاً فیلد ${input.name} را پر کنید.`, "error");
            return false;
        }
    }
    return true;
}

// =======================
// بروزرسانی UI مودال
// =======================
function updateAuthUI() {
    const sections = ["login", "register", "verify", "remember", "change"];
    const authTitle = document.getElementById("authTitle");
    const authSubmitBtn = document.getElementById("authSubmitBtn");
    const authFooterText = document.getElementById("authFooterText");
    const authToggleBtn = document.getElementById("authToggleBtn");

    sections.forEach(s => {
        const el = document.getElementById(s + "Fields");
        if (el) el.classList.add("hidden");
    });

    const activeFields = document.getElementById(authMode + "Fields");
    if (activeFields) activeFields.classList.remove("hidden");

    authToggleBtn.style.display = ["login","register"].includes(authMode) ? "inline-block" : "none";

    switch(authMode) {
        case "login":
            authTitle.textContent = "ورود به حساب";
            authSubmitBtn.textContent = "ورود";
            authFooterText.textContent = "حساب کاربری ندارید؟";
            authToggleBtn.textContent = "ثبت نام کنید";
            break;
        case "register":
            authTitle.textContent = "ثبت نام";
            authSubmitBtn.textContent = "ثبت نام";
            authFooterText.textContent = "قبلاً ثبت نام کرده‌اید؟";
            authToggleBtn.textContent = "ورود";
            break;
        case "verify":
            authTitle.textContent = "تایید شماره موبایل";
            authSubmitBtn.textContent = "تایید کد";
            authFooterText.textContent = "";
            break;
        case "remember":
            authTitle.textContent = "فراموشی رمز عبور";
            authSubmitBtn.textContent = "تایید شماره موبایل";
            authFooterText.textContent = "";
            break;
        case "change":
            authTitle.textContent = "تغییر رمز عبور";
            authSubmitBtn.textContent = "تغییر رمز عبور";
            authFooterText.textContent = "";
            break;
    }

    sections.forEach(s => {
        const required = s === authMode;
        document.querySelectorAll(`#${s}Fields input`).forEach(i => i.required = required);
    });
}

// =======================
// ارسال فرم مودال
// =======================
async function handleAuth(event) {
    event.preventDefault();
    if (!validateForm()) return;

    const form = event.target;
    const formData = new FormData(form);
    let url = "", payload = {};

    if (authMode === "login") {
        url = "/accounts/login/";
        payload = { mobile_number: formData.get("mobile_number_login"), password: formData.get("password_login") };
    } else if (authMode === "register") {
        url = "/accounts/register/";
        payload = { mobile_number: formData.get("mobile_number_register"), password1: formData.get("password1_register"), password2: formData.get("password2_register") };
    } else if (authMode === "verify") {
        url = "/accounts/verify/";
        payload = { active_code: formData.get("active_code") };
    } else if (authMode === "remember") {
        url = "/accounts/remember_password/";
        payload = { mobile_number: formData.get("mobile_number_remember") };
    } else if (authMode === "change") {
        url = "/accounts/change_password/";
        payload = { password1: formData.get("password1_change"), password2: formData.get("password2_change") };
    }

    const csrfToken = getCookie("csrftoken");
    if (!csrfToken) return showNotification("CSRF token یافت نشد!", "error");

    try {
        const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken, "X-Requested-With": "XMLHttpRequest" },
            credentials: "include",
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.success) {
            switch(authMode) {
                case "register":
                    showNotification("ثبت‌نام موفق! لطفاً کد تایید را وارد کنید", "success");
                    authMode = "verify";
                    updateAuthUI();
                    break;
                case "verify":
                    showNotification("کد تایید شد!", "success");
                    authMode = data.after === "register" ? "login" : "change";
                    updateAuthUI();
                    break;
                case "remember":
                    showNotification("کد ارسال شد! لطفاً کد را وارد کنید", "success");
                    authMode = "verify"; updateAuthUI();
                    break;
                case "change":
                    showNotification("رمز با موفقیت تغییر کرد!", "success");
                    authMode = "login"; updateAuthUI();
                    break;
                case "login":
                    showNotification("ورود موفق!", "success");
                    await handleLoginSuccess(data);
                    break;
            }
        } else {
            if (data.errors) Object.values(data.errors).forEach(e => showNotification(e, "error"));
            else showNotification(data.message || "خطایی رخ داده است!", "error");
        }
    } catch (err) {
        console.error(err);
        showNotification("خطا در ارتباط با سرور!", "error");
    }
}

// =======================
// لاگین موفق
// =======================
async function handleLoginSuccess(data) {
    if (!data.access) return showNotification("توکن دریافت نشد!", "error");
    localStorage.setItem('accessToken', data.access);
    currentUser = await fetchCurrentUser();
    if (!currentUser) return showNotification("خطا در دریافت اطلاعات کاربر!", "error");
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
    updateAuthButtons(currentUser);
    closeAuthModal();
}

// =======================
// لاگ‌اوت
// =======================
function logout() {
    localStorage.clear();
    currentUser = null;
    updateAuthButtons(null);
    window.location.href = '/';
}

// =======================
// بروزرسانی دکمه‌ها
// =======================
function updateAuthButtons(user = null) {
    const authButton = document.getElementById('authButton');
    if (!authButton) {
        return;
    }
    if (!user) user = currentUser;
    const onProfilePage = window.location.pathname.includes('/accounts/profile/');

    if (user) {
        authButton.textContent = onProfilePage ? 'خروج' : 'پروفایل من';
        authButton.onclick = onProfilePage 
            ? logout
            : () => { window.location.href = '/accounts/profile/'; };
    } else {
        authButton.textContent = 'ورود / ثبت‌نام';
        authButton.onclick = () => openAuthModal('login');
    }

    authButton.classList.remove('hidden');
}
// =======================
// گرفتن اطلاعات کاربر
// =======================
async function fetchCurrentUser() {
    const token = localStorage.getItem('accessToken');
    if (!token) return null;
    try {
        const res = await fetch("/accounts/api/me/", { headers: { 'Authorization': 'Bearer ' + token } });
        if (!res.ok) throw new Error('Unauthorized');
        return await res.json();
    } catch (err) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('currentUser');
        return null;
    }
}

// =======================
// بروزرسانی کاربر هنگام لود
// =======================
async function updateCurrentUser() {
    const storedUser = localStorage.getItem('currentUser');
    const token = localStorage.getItem('accessToken');

    if (storedUser && token) {
        currentUser = JSON.parse(storedUser);
        updateAuthButtons(currentUser);
    } else {
        currentUser = null;
        updateAuthButtons(null);
    }

    if (token) {
        try {
            const res = await fetch("/accounts/api/me/", {
                headers: { 'Authorization': 'Bearer ' + token }
            });
            if (!res.ok) throw new Error('Unauthorized');
            const data = await res.json();
            currentUser = data;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            updateAuthButtons(currentUser);
        } catch (err) {
            logout();
            
        }
    }
}

// =======================
// رویداد فرم‌ها
// =======================
document.querySelectorAll(".authForm").forEach(f => f.addEventListener("submit", handleAuth));

// =======================
// هنگام لود صفحه
// =======================
document.addEventListener("DOMContentLoaded", () => updateCurrentUser());



