/* ============================================================
   Spar Merch SPA — клиентский модуль
   Работает с REST API через Fetch + JWT Bearer-авторизацию
   ============================================================ */

const API = '/api/v1';
const state = {
    token: localStorage.getItem('spar_token') || null,
    username: localStorage.getItem('spar_username') || null,
    balance: 0,
};

/* ---------- API-КЛИЕНТ ---------- */
async function apiCall(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

    const res = await fetch(`${API}${path}`, { ...options, headers });

    // Если токен протух — разлогиниваем
    if (res.status === 401) {
        logout();
        throw new Error('Сессия истекла, войдите заново');
    }

    // Скачивание файла (отчёт) — возвращаем blob
    if (options.blob) return await res.blob();

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        const detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
        throw new Error(detail || `Ошибка ${res.status}`);
    }
    return data;
}

/* ---------- TOAST-УВЕДОМЛЕНИЯ ---------- */
function toast(message, isError = false) {
    const container = document.getElementById('toast-container');
    const el = document.createElement('div');
    el.className = `toast ${isError ? 'error' : ''}`;
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => el.remove(), 3500);
}

/* ---------- ПЕРЕКЛЮЧЕНИЕ ЭКРАНОВ ---------- */
function showScreen(name) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(`screen-${name}`).classList.add('active');
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.screen === name));

    if (name === 'catalog') loadCatalog();
    if (name === 'inventory') loadInventory();
}

/* ---------- UI-СОСТОЯНИЯ ---------- */
function renderAuthUI() {
    const logged = !!state.token;
    document.getElementById('screen-auth').style.display = logged ? 'none' : '';
    document.getElementById('nav').style.display = logged ? 'flex' : 'none';
    document.getElementById('balance-badge').style.display = logged ? 'block' : 'none';
    document.getElementById('btn-logout').style.display = logged ? 'block' : 'none';
    if (logged) showScreen('catalog');
}

function renderBalance() {
    document.getElementById('balance-value').textContent = state.balance.toFixed(0);
}

/* ---------- АВТОРИЗАЦИЯ ---------- */
async function login(username, password) {
    const data = await apiCall('/auth/sign_in', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
    });
    state.token = data.access_token;
    state.username = username;
    localStorage.setItem('spar_token', data.access_token);
    localStorage.setItem('spar_username', username);
    await refreshProfile();
    renderAuthUI();
    toast(`Добро пожаловать, ${username}! 🎉`);
}

async function register(username, password, email) {
    await apiCall('/auth/sign_up', {
        method: 'POST',
        body: JSON.stringify({ username, password, email: email || undefined }),
    });
    toast('Регистрация успешна! Стартовый баланс: 1000 🪙');
    switchTab('login');
    document.getElementById('login-username').value = username;
    document.getElementById('login-password').value = password;
}

async function refreshProfile() {
    const me = await apiCall('/employees/me');
    state.balance = me.coins_amount;
    renderBalance();
}

function logout() {
    state.token = null;
    state.username = null;
    localStorage.removeItem('spar_token');
    localStorage.removeItem('spar_username');
    renderAuthUI();
}

function switchTab(tab) {
    document.getElementById('tab-login').classList.toggle('active', tab === 'login');
    document.getElementById('tab-register').classList.toggle('active', tab === 'register');
    document.getElementById('form-login').style.display = tab === 'login' ? 'flex' : 'none';
    document.getElementById('form-register').style.display = tab === 'register' ? 'flex' : 'none';
}

/* ---------- КАТАЛОГ ---------- */
const ITEM_ICONS = {
    'Худи': '🧥', 'Футболка': '👕', 'Кружка': '☕', 'Ручка': '🖊️',
    'Пауэрбанк': '🔋', 'Зонт': '☂️', 'Носки': '🧦', 'Кошелёк': '👛',
    'Книга': '📖', 'Розовое худи': '🌸', 'Кепка': '🧢',
};

function getIcon(name) {
    for (const [key, icon] of Object.entries(ITEM_ICONS)) {
        if (name.toLowerCase().includes(key.toLowerCase())) return icon;
    }
    return '🎁';
}

async function loadCatalog() {
    const grid = document.getElementById('items-grid');
    grid.innerHTML = '<div class="empty-state">Загрузка...</div>';
    try {
        const items = await apiCall('/merch/');
        grid.innerHTML = items.map(item => `
            <div class="item-card">
                <div class="item-image">${getIcon(item.name)}</div>
                <div class="item-body">
                    <div class="item-name">${item.name}</div>
                    <div class="item-price">${item.price.toFixed(0)} 🪙</div>
                    <button class="btn-buy" data-id="${item.id}"
                            ${item.price > state.balance ? 'disabled title="Недостаточно монет"' : ''}>
                        ${item.price > state.balance ? 'Мало монет' : 'Купить'}
                    </button>
                </div>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = `<div class="empty-state">Ошибка: ${e.message}</div>`;
    }
}

async function buyItem(itemId, btn) {
    btn.disabled = true;
    try {
        const res = await apiCall(`/transactions/buy/${itemId}`, { method: 'POST' });
        toast(res.message || 'Покупка совершена! ✅');
        await refreshProfile();
        loadCatalog();
    } catch (e) {
        toast(e.message, true);
        btn.disabled = false;
    }
}

/* ---------- ИНВЕНТАРЬ ---------- */
async function loadInventory() {
    const wrap = document.getElementById('inventory-list');
    wrap.innerHTML = '<div class="empty-state">Загрузка...</div>';
    try {
        const items = await apiCall('/employees/me/inventory');
        if (!items.length) {
            wrap.innerHTML = '<div class="empty-state">Вы ещё ничего не купили 🛍️<br>Загляните в каталог!</div>';
            return;
        }
        wrap.innerHTML = `
            <table>
                <thead><tr><th>Товар</th><th>Цена</th><th>Дата покупки</th></tr></thead>
                <tbody>
                    ${items.map(i => `
                        <tr>
                            <td>${getIcon(i.item_name)} ${i.item_name}</td>
                            <td><b>${i.price.toFixed(0)} 🪙</b></td>
                            <td>${new Date(i.date).toLocaleString('ru-RU')}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>`;
    } catch (e) {
        wrap.innerHTML = `<div class="empty-state">Ошибка: ${e.message}</div>`;
    }
}

/* ---------- ПЕРЕВОДЫ ---------- */
async function sendCoins(username, amount) {
    try {
        const res = await apiCall('/transactions/send_coins', {
            method: 'POST',
            body: JSON.stringify({ gainer_username: username, amount: parseFloat(amount) }),
        });
        toast(res.message || 'Перевод выполнен! 💸');
        await refreshProfile();
    } catch (e) {
        toast(e.message, true);
    }
}

/* ---------- ОТЧЁТЫ ---------- */
async function downloadReport() {
    toast('Формируем отчёт...');
    try {
        const blob = await apiCall('/reports/sales', { blob: true });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'spar_merch_sales_report.docx';
        a.click();
        URL.revokeObjectURL(url);
        toast('Отчёт скачан! 📄');
    } catch (e) {
        toast(e.message, true);
    }
}

/* ---------- ИНИЦИАЛИЗАЦИЯ ---------- */
document.addEventListener('DOMContentLoaded', () => {
    // Табы авторизации
    document.getElementById('tab-login').onclick = () => switchTab('login');
    document.getElementById('tab-register').onclick = () => switchTab('register');

    // Формы авторизации
    document.getElementById('form-login').onsubmit = async (e) => {
        e.preventDefault();
        try {
            await login(
                document.getElementById('login-username').value.trim(),
                document.getElementById('login-password').value,
            );
        } catch (err) { toast(err.message, true); }
    };

    document.getElementById('form-register').onsubmit = async (e) => {
        e.preventDefault();
        try {
            await register(
                document.getElementById('reg-username').value.trim(),
                document.getElementById('reg-password').value,
                document.getElementById('reg-email').value.trim(),
            );
        } catch (err) { toast(err.message, true); }
    };

    // Навигация
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.onclick = () => showScreen(btn.dataset.screen);
    });

    // Выход
    document.getElementById('btn-logout').onclick = () => { logout(); toast('Вы вышли из системы'); };

    // Покупки (делегирование событий)
    document.getElementById('items-grid').addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-buy');
        if (btn) buyItem(btn.dataset.id, btn);
    });

    // Переводы
    document.getElementById('form-transfer').onsubmit = (e) => {
        e.preventDefault();
        sendCoins(
            document.getElementById('transfer-username').value.trim(),
            document.getElementById('transfer-amount').value,
        );
        e.target.reset();
    };

    // Отчёт
    document.getElementById('btn-download-report').onclick = downloadReport;

    // Если токен уже есть — восстанавливаем сессию
    if (state.token) {
        refreshProfile().then(renderAuthUI).catch(() => logout());
    } else {
        renderAuthUI();
    }
});