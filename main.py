import sqlite3
import logging
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
API_TOKEN = '7857025943:AAHamcNP_id4ftZXUg-9GvteLkqgyIjgLjw'
ADMIN_ID = 439759850  # Замените на ваш ID админа

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Константы для пагинации
ITEMS_PER_PAGE = 6

# Языковые константы
LANGUAGES = {
    'ru': 'Русский',
    'uz': 'Узбекский', 
    'en': 'Английский'
}

# Тексты для разных языков
TEXTS = {
    'ru': {
        'welcome': "👋 Привет, {name}!\n\nДобро пожаловать в наш мини-магазин! Здесь вы можете заказать вкусные снеки и напитки.",
        'main_menu': "Выберите действие из меню ниже:",
        'cart': "🛒 Корзина",
        'shop': "🏪 Наш Мини-Магазин",
        'language': "🌐 Сменить язык",
        'back': "⬅️ Назад",
        'back_to_menu': "⬅️ Назад в меню",
        'cart_empty': "🛒 Ваша корзина пуста",
        'cart_title': "🛒 **Ваша корзина:**\n\n",
        'total': "💵 **Общая сумма: {total:,} сум**",
        'remove': "❌ Удалить",
        'checkout': "✅ Оформить заказ",
        'shop_title': "🏪 **Наш Мини-Магазин**\n\n",
        'page_info': "📄 Страница {current}/{total} (Всего товаров: {count})",
        'choose_product': "Выберите товар для добавления в корзину:",
        'added_to_cart': "✅ {name} добавлен в корзину!",
        'removed_from_cart': "✅ Товар удален из корзины!",
        'checkout_title': "📞 **Оформление заказа**\n\n",
        'enter_phone': "Пожалуйста, введите ваш номер телефона в формате:\n+998XXYYYYYYY\n\nПример: +998901234567",
        'enter_room': "🏨 **Отлично! Теперь введите номер вашей комнаты:**\n\nПример: 26 или 105",
        'cancel_order': "❌ Отменить заказ",
        'order_cancelled': "❌ Заказ отменен.",
        'order_completed': "✅ **Заказ оформлен!**\n\n",
        'your_order': "📦 **Ваш заказ:**\n",
        'phone': "📞 Телефон: {phone}",
        'room': "🏨 Комната: {room}",
        'delivery_time': "🕐 Заказ будет доставлен в течение 15 минут!",
        'return_to_shop': "🏪 Вернуться в магазин",
        'main_menu_btn': "📋 Главное меню",
        'invalid_phone': "❌ Неверный формат номера телефона!\n\nВведите номер в формате: +998901234567",
        'invalid_room': "❌ Неверный формат номера комнаты!\n\nВведите только цифры:",
        'empty_cart_error': "❌ Корзина пуста!",
        'language_changed': "🌐 Язык изменен на {language}",
        'choose_language': "Выберите язык:",
        'current_language': "Текущий язык: Русский",
        'product_added': "✅ Добавлено: {name}",
        'quantity': "Количество: {quantity}",
        'item_total': "Сумма: {total:,} сум",
        'in_cart': "✅ В корзине: {quantity} шт.",
        'price_per_item': "Цена: {price:,} сум",
        'admin_panel': "🛠️ **Панель администратора**\n\nВыберите действие:",
        'add_product': "➕ Добавить товар",
        'delete_product': "🗑️ Удалить товар",
        'enter_product_name': "📝 Введите название товара:",
        'enter_product_price': "💰 Теперь введите цену товара (только цифры):",
        'product_added_success': "✅ Товар успешно добавлен в магазин!",
        'select_product_to_delete': "🗑️ Выберите товар для удаления:",
        'product_deleted_success': "✅ Товар успешно удален из магазина!",
        'no_products': "❌ В магазине нет товаров для удаления."
    },
    'uz': {
        'welcome': "👋 Salom, {name}!\n\nBizning mini-do'konimizga xush kelibsiz! Bu yerda mazzali gazaklar va ichimliklar buyurtma qilishingiz mumkin.",
        'main_menu': "Quyidagi menyudan harakatni tanlang:",
        'cart': "🛒 Savat",
        'shop': "🏪 Bizning Mini-Do'kon",
        'language': "🌐 Tilni o'zgartirish",
        'back': "⬅️ Orqaga",
        'back_to_menu': "⬅️ Menyuga qaytish",
        'cart_empty': "🛒 Sizning savatingiz bo'sh",
        'cart_title': "🛒 **Sizning savatingiz:**\n\n",
        'total': "💵 **Jami summa: {total:,} so'm**",
        'remove': "❌ O'chirish",
        'checkout': "✅ Buyurtma berish",
        'shop_title': "🏪 **Bizning Mini-Do'kon**\n\n",
        'page_info': "📄 Sahifa {current}/{total} (Jami mahsulotlar: {count})",
        'choose_product': "Savatga qo'shish uchun mahsulotni tanlang:",
        'added_to_cart': "✅ {name} savatga qo'shildi!",
        'removed_from_cart': "✅ Mahsulot savatdan o'chirildi!",
        'checkout_title': "📞 **Buyurtma berish**\n\n",
        'enter_phone': "Iltimos, telefon raqamingizni quyidagi formatda kiriting:\n+998XXYYYYYYY\n\nMasalan: +998901234567",
        'enter_room': "🏨 **Ajoyib! Endi xonangiz raqamini kiriting:**\n\nMasalan: 26 yoki 105",
        'cancel_order': "❌ Buyurtmani bekor qilish",
        'order_cancelled': "❌ Buyurtma bekor qilindi.",
        'order_completed': "✅ **Buyurtma muvaffaqiyatli berildi!**\n\n",
        'your_order': "📦 **Sizning buyurtmangiz:**\n",
        'phone': "📞 Telefon: {phone}",
        'room': "🏨 Xona: {room}",
        'delivery_time': "🕐 Buyurtma 15 daqiqa ichida etkazib beriladi!",
        'return_to_shop': "🏪 Do'konga qaytish",
        'main_menu_btn': "📋 Asosiy menyu",
        'invalid_phone': "❌ Noto'g'ri telefon raqami formati!\n\nRaqamni quyidagi formatda kiriting: +998901234567",
        'invalid_room': "❌ Noto'g'ri xona raqami formati!\n\nFaqat raqamlarni kiriting:",
        'empty_cart_error': "❌ Savat bo'sh!",
        'language_changed': "🌐 Til {language} ga o'zgartirildi",
        'choose_language': "Tilni tanlang:",
        'current_language': "Joriy til: O'zbekcha",
        'product_added': "✅ Qo'shildi: {name}",
        'quantity': "Miqdor: {quantity}",
        'item_total': "Summa: {total:,} so'm",
        'in_cart': "✅ Savatda: {quantity} dona",
        'price_per_item': "Narx: {price:,} so'm",
        'admin_panel': "🛠️ **Administrator paneli**\n\nHarakatni tanlang:",
        'add_product': "➕ Mahsulot qo'shish",
        'delete_product': "🗑️ Mahsulotni o'chirish",
        'enter_product_name': "📝 Mahsulot nomini kiriting:",
        'enter_product_price': "💰 Endi mahsulot narxini kiriting (faqat raqamlar):",
        'product_added_success': "✅ Mahsulot muvaffaqiyatli do'konga qo'shildi!",
        'select_product_to_delete': "🗑️ O'chirish uchun mahsulotni tanlang:",
        'product_deleted_success': "✅ Mahsulot muvaffaqiyatli do'kondan o'chirildi!",
        'no_products': "❌ Do'konda o'chirish uchun mahsulotlar mavjud emas."
    },
    'en': {
        'welcome': "👋 Hello, {name}!\n\nWelcome to our mini-store! Here you can order delicious snacks and drinks.",
        'main_menu': "Choose an action from the menu below:",
        'cart': "🛒 Cart",
        'shop': "🏪 Our Mini-Store", 
        'language': "🌐 Change language",
        'back': "⬅️ Back",
        'back_to_menu': "⬅️ Back to menu",
        'cart_empty': "🛒 Your cart is empty",
        'cart_title': "🛒 **Your Cart:**\n\n",
        'total': "💵 **Total amount: {total:,} sums**",
        'remove': "❌ Remove",
        'checkout': "✅ Checkout",
        'shop_title': "🏪 **Our Mini-Store**\n\n",
        'page_info': "📄 Page {current}/{total} (Total products: {count})",
        'choose_product': "Select a product to add to cart:",
        'added_to_cart': "✅ {name} added to cart!",
        'removed_from_cart': "✅ Product removed from cart!",
        'checkout_title': "📞 **Checkout**\n\n",
        'enter_phone': "Please enter your phone number in the format:\n+998XXYYYYYYY\n\nExample: +998901234567",
        'enter_room': "🏨 **Great! Now enter your room number:**\n\nExample: 26 or 105",
        'cancel_order': "❌ Cancel order",
        'order_cancelled': "❌ Order cancelled.",
        'order_completed': "✅ **Order completed!**\n\n",
        'your_order': "📦 **Your order:**\n",
        'phone': "📞 Phone: {phone}",
        'room': "🏨 Room: {room}",
        'delivery_time': "🕐 Order will be delivered within 15 minutes!",
        'return_to_shop': "🏪 Return to store",
        'main_menu_btn': "📋 Main menu",
        'invalid_phone': "❌ Invalid phone number format!\n\nEnter number in format: +998901234567",
        'invalid_room': "❌ Invalid room number format!\n\nEnter only digits:",
        'empty_cart_error': "❌ Cart is empty!",
        'language_changed': "🌐 Language changed to {language}",
        'choose_language': "Choose language:",
        'current_language': "Current language: English",
        'product_added': "✅ Added: {name}",
        'quantity': "Quantity: {quantity}",
        'item_total': "Amount: {total:,} sums",
        'in_cart': "✅ In cart: {quantity} pcs",
        'price_per_item': "Price: {price:,} sums",
        'admin_panel': "🛠️ **Admin Panel**\n\nChoose action:",
        'add_product': "➕ Add product",
        'delete_product': "🗑️ Delete product",
        'enter_product_name': "📝 Enter product name:",
        'enter_product_price': "💰 Now enter product price (digits only):",
        'product_added_success': "✅ Product successfully added to store!",
        'select_product_to_delete': "🗑️ Select product to delete:",
        'product_deleted_success': "✅ Product successfully deleted from store!",
        'no_products': "❌ No products in store to delete."
    }
}

# Состояния для оформления заказа
class OrderStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_room = State()

# Состояния для админ-панели
class AdminStates(StatesGroup):
    waiting_for_product_name = State()
    waiting_for_product_price = State()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language TEXT DEFAULT 'ru',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Проверяем наличие столбца language и добавляем если его нет
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'language' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN language TEXT DEFAULT "ru"')
    
    # Таблица товаров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            category TEXT
        )
    ''')
    
    # Таблица корзины
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')
    
    # Таблица заказов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_text TEXT,
            total_price INTEGER,
            phone_number TEXT,
            room_number TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Добавляем товары из вашего списка
    products_data = [
        # MW
        ('Snickers 0,50 gr', 'Шоколадный батончик', 10000, 'Шоколад'),
        ('Baunty 0,57 gr', 'Кокосовый батончик', 12000, 'Шоколад'),
        ('Orbit classic', 'Жвачка классическая', 6000, 'Жвачка'),
        ('Orbit watermelon', 'Жвачка арбузная', 6000, 'Жвачка'),
        
        # Flash energetic
        ('Flash 0,5 l', 'Энергетик 0.5л', 15000, 'Напитки'),
        ('Flash 0,25 l', 'Энергетик 0.25л', 10000, 'Напитки'),
        
        # GODRINKS / Milly cola
        ('Milly cola 0,5 l', 'Кола 0.5л', 8000, 'Напитки'),
        ('Milly cola 1,0 l', 'Кола 1.0л', 11000, 'Напитки'),
        
        # Cheers corp
        ('Чипсы Cheers шашлык 27гр', 'Чипсы со вкусом шашлыка', 7000, 'Чипсы'),
        ('Чипсы Cheers сметана 27гр', 'Чипсы со сметаной и луком', 7000, 'Чипсы'),
        ('Чипсы Cheers лук 45гр', 'Чипсы с зеленым луком', 10000, 'Чипсы'),
    ]
    
    # Очищаем и добавляем товары только если таблица пустая
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO products (name, description, price, category) 
            VALUES (?, ?, ?, ?)
        ''', products_data)
    
    conn.commit()
    conn.close()

# Функция для получения языка пользователя
def get_user_language(user_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 'ru'

# Функция для установки языка пользователя
def set_user_language(user_id, language):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    user_exists = cursor.fetchone()
    
    if user_exists:
        cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
    else:
        cursor.execute('''
            INSERT INTO users (user_id, language) 
            VALUES (?, ?)
        ''', (user_id, language))
    
    conn.commit()
    conn.close()

# Функция для добавления пользователя в базу
def add_user_to_db(user_id, username, first_name, last_name):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    user_exists = cursor.fetchone()
    
    if user_exists:
        cursor.execute('''
            UPDATE users SET username = ?, first_name = ?, last_name = ?
            WHERE user_id = ?
        ''', (username, first_name, last_name, user_id))
    else:
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, language)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, 'ru'))
    
    conn.commit()
    conn.close()

# Главное меню
def get_main_menu(user_id):
    lang = get_user_language(user_id)
    texts = TEXTS[lang]
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text=texts['cart'], callback_data="cart"),
        InlineKeyboardButton(text=texts['shop'], callback_data="shop"),
        InlineKeyboardButton(text=texts['language'], callback_data="change_language")
    )
    builder.adjust(2, 1)
    return builder.as_markup()

# Клавиатура выбора языка
def get_language_keyboard(user_id):
    lang = get_user_language(user_id)
    texts = TEXTS[lang]
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇺🇿 Узбекский", callback_data="lang_uz"),
        InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"),
        InlineKeyboardButton(text=texts['back'], callback_data="back_to_main")
    )
    builder.adjust(1)
    return builder.as_markup()

# Админ-панель
def get_admin_panel():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add_product"),
        InlineKeyboardButton(text="🗑️ Удалить товар", callback_data="admin_delete_product"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
    )
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура для удаления товаров
def get_delete_products_keyboard():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT product_id, name, price FROM products ORDER BY name')
    products = cursor.fetchall()
    conn.close()
    
    builder = InlineKeyboardBuilder()
    
    for product_id, name, price in products:
        # Сокращаем длинные названия
        short_name = name if len(name) <= 30 else name[:27] + "..."
        builder.add(InlineKeyboardButton(
            text=f"🗑️ {short_name} - {price:,} сум", 
            callback_data=f"admin_delete_{product_id}"
        ))
    
    builder.add(InlineKeyboardButton(text="⬅️ Назад в админ-панель", callback_data="admin_panel"))
    builder.adjust(1)
    return builder.as_markup()

# Функция для получения товаров с пагинацией
def get_products_page(page: int = 0):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM products')
    total_products = cursor.fetchone()[0]
    
    total_pages = (total_products + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    offset = page * ITEMS_PER_PAGE
    cursor.execute('''
        SELECT product_id, name, price, category 
        FROM products 
        ORDER BY category, name 
        LIMIT ? OFFSET ?
    ''', (ITEMS_PER_PAGE, offset))
    
    products = cursor.fetchall()
    conn.close()
    
    return products, total_pages, total_products

# Функция для получения количества товара в корзине
def get_cart_quantity(user_id, product_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 0

# Функция для создания клавиатуры магазина с пагинацией
def get_shop_keyboard(page: int = 0, user_id: int = None):
    products, total_pages, total_products = get_products_page(page)
    lang = get_user_language(user_id) if user_id else 'ru'
    texts = TEXTS[lang]
    
    builder = InlineKeyboardBuilder()
    
    # Добавляем товары в строки по 2 кнопки
    for i in range(0, len(products), 2):
        row_products = products[i:i+2]
        row_buttons = []
        
        for product in row_products:
            product_id, name, price, category = product
            # Сокращаем длинные названия для кнопок
            short_name = name
            if len(name) > 20:
                short_name = name[:20] + "..."
            
            # Получаем количество в корзине
            quantity = get_cart_quantity(user_id, product_id) if user_id else 0
            
            if quantity > 0:
                button_text = f"✅ {short_name}\n{price:,} сум"
            else:
                button_text = f"🛒 {short_name}\n{price:,} сум"
                
            row_buttons.append(InlineKeyboardButton(
                text=button_text, 
                callback_data=f"add_to_cart_{product_id}"
            ))
        
        builder.row(*row_buttons)
        
        # Добавляем кнопки управления количеством под каждым товаром
        for product in row_products:
            product_id, name, price, category = product
            quantity = get_cart_quantity(user_id, product_id) if user_id else 0
            
            if quantity > 0:
                control_buttons = [
                    InlineKeyboardButton(text="➖", callback_data=f"decrease_{product_id}"),
                    InlineKeyboardButton(text=f"✏️ {quantity} шт", callback_data=f"view_{product_id}"),
                    InlineKeyboardButton(text="➕", callback_data=f"increase_{product_id}")
                ]
                builder.row(*control_buttons)
    
    # Кнопки пагинации
    pagination_buttons = []
    
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page-1}"))
    
    if page < total_pages - 1:
        pagination_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page_{page+1}"))
    
    if pagination_buttons:
        builder.row(*pagination_buttons)
    
    page_info = texts['page_info'].format(current=page+1, total=total_pages, count=total_products)
    
    # Кнопка корзины и назад
    builder.row(
        InlineKeyboardButton(text=texts['cart'], callback_data="cart"),
        InlineKeyboardButton(text=texts['back_to_menu'], callback_data="back_to_main")
    )
    
    return builder.as_markup(), page_info

# Функция для создания текста магазина с товарами
def get_shop_text(page: int = 0, user_id: int = None):
    products, total_pages, total_products = get_products_page(page)
    lang = get_user_language(user_id) if user_id else 'ru'
    texts = TEXTS[lang]
    
    text = texts['shop_title']
    text += f"📄 **{texts['page_info'].format(current=page+1, total=total_pages, count=total_products)}**\n\n"
    
    # Группируем товары по категориям
    categories = {}
    for product in products:
        product_id, name, price, category = product
        if category not in categories:
            categories[category] = []
        categories[category].append((product_id, name, price))
    
    # Выводим товары по категориям
    for category, category_products in categories.items():
        text += f"**🏷️ {category}**\n"
        
        for product_id, name, price in category_products:
            quantity = get_cart_quantity(user_id, product_id) if user_id else 0
            text += f"📦 **{name}**\n"
            text += f"   💰 {texts['price_per_item'].format(price=price)}\n"
            if quantity > 0:
                total_price = price * quantity
                text += f"   ✅ {texts['in_cart'].format(quantity=quantity)} = {total_price:,} сум\n"
            text += "   ────────────────────\n"
        
        text += "\n"
    
    text += texts['choose_product']
    
    return text

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    add_user_to_db(user.id, user.username, user.first_name, user.last_name)
    
    lang = get_user_language(user.id)
    texts = TEXTS[lang]
    
    welcome_text = texts['welcome'].format(name=user.first_name)
    welcome_text += f"\n\n{texts['main_menu']}"
    
    await message.answer(welcome_text, reply_markup=get_main_menu(user.id))

# Обработчик команды /admin
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    lang = get_user_language(message.from_user.id)
    texts = TEXTS[lang]
    
    await message.answer(texts['admin_panel'], reply_markup=get_admin_panel())

# Обработчик кнопки админ-панели
@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("❌ У вас нет прав для этого действия.")
        return
    
    lang = get_user_language(callback_query.from_user.id)
    texts = TEXTS[lang]
    
    await callback_query.message.edit_text(texts['admin_panel'], reply_markup=get_admin_panel())
    await callback_query.answer()

# Обработчик кнопки "Добавить товар"
@dp.callback_query(F.data == "admin_add_product")
async def admin_add_product(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("❌ У вас нет прав для этого действия.")
        return
    
    lang = get_user_language(callback_query.from_user.id)
    texts = TEXTS[lang]
    
    await state.set_state(AdminStates.waiting_for_product_name)
    await callback_query.message.edit_text(texts['enter_product_name'])
    await callback_query.answer()

# Обработчик ввода названия товара
@dp.message(AdminStates.waiting_for_product_name)
async def process_product_name(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для этого действия.")
        return
    
    await state.update_data(product_name=message.text)
    
    lang = get_user_language(message.from_user.id)
    texts = TEXTS[lang]
    
    await state.set_state(AdminStates.waiting_for_product_price)
    await message.answer(texts['enter_product_price'])

# Обработчик ввода цены товара
@dp.message(AdminStates.waiting_for_product_price)
async def process_product_price(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для этого действия.")
        return
    
    try:
        price = int(message.text)
        if price <= 0:
            raise ValueError("Цена должна быть положительным числом")
        
        data = await state.get_data()
        product_name = data['product_name']
        
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO products (name, description, price, category) 
            VALUES (?, ?, ?, ?)
        ''', (product_name, product_name, price, 'Другие товары'))
        
        conn.commit()
        conn.close()
        
        lang = get_user_language(message.from_user.id)
        texts = TEXTS[lang]
        
        await message.answer(f"{texts['product_added_success']}\n\nНазвание: {product_name}\nЦена: {price:,} сум")
        await state.clear()
        
        # Показываем админ-панель снова
        await message.answer(texts['admin_panel'], reply_markup=get_admin_panel())
        
    except ValueError:
        lang = get_user_language(message.from_user.id)
        texts = TEXTS[lang]
        await message.answer("❌ Неверный формат цены! Введите только цифры:")

# Обработчик кнопки "Удалить товар"
@dp.callback_query(F.data == "admin_delete_product")
async def admin_delete_product(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("❌ У вас нет прав для этого действия.")
        return
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM products')
    product_count = cursor.fetchone()[0]
    conn.close()
    
    lang = get_user_language(callback_query.from_user.id)
    texts = TEXTS[lang]
    
    if product_count == 0:
        await callback_query.message.edit_text(texts['no_products'], reply_markup=get_admin_panel())
    else:
        await callback_query.message.edit_text(texts['select_product_to_delete'], reply_markup=get_delete_products_keyboard())
    
    await callback_query.answer()

# Обработчик удаления конкретного товара
@dp.callback_query(F.data.startswith("admin_delete_"))
async def delete_specific_product(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("❌ У вас нет прав для этого действия.")
        return
    
    product_id = int(callback_query.data.split('_')[-1])
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    # Получаем информацию о товаре перед удалением
    cursor.execute('SELECT name, price FROM products WHERE product_id = ?', (product_id,))
    product_info = cursor.fetchone()
    
    if product_info:
        product_name, product_price = product_info
        
        # Удаляем товар
        cursor.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
        
        # Также удаляем товар из корзин всех пользователей
        cursor.execute('DELETE FROM cart WHERE product_id = ?', (product_id,))
        
        conn.commit()
        
        lang = get_user_language(callback_query.from_user.id)
        texts = TEXTS[lang]
        
        await callback_query.answer(f"{texts['product_deleted_success']}")
        
        # Обновляем сообщение с новым списком товаров
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        product_count = cursor.fetchone()[0]
        conn.close()
        
        if product_count == 0:
            await callback_query.message.edit_text(texts['no_products'], reply_markup=get_admin_panel())
        else:
            await callback_query.message.edit_text(texts['select_product_to_delete'], reply_markup=get_delete_products_keyboard())
    else:
        await callback_query.answer("❌ Товар не найден!")
    
    conn.close()

# Обработчик смены языка
@dp.callback_query(F.data == "change_language")
async def change_language(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS[lang]
    
    text = f"{texts['choose_language']}\n{texts['current_language']}"
    
    await callback_query.message.edit_text(text, reply_markup=get_language_keyboard(user_id))
    await callback_query.answer()

# Обработчик выбора языка
@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    language_code = callback_query.data.split('_')[1]
    
    if language_code in LANGUAGES:
        set_user_language(user_id, language_code)
        lang_name = LANGUAGES[language_code]
        texts = TEXTS[language_code]
        
        await callback_query.message.edit_text(
            texts['language_changed'].format(language=lang_name),
            reply_markup=get_main_menu(user_id)
        )
    await callback_query.answer()

# Обработчик кнопки "Назад"
@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS[lang]
    
    await callback_query.message.edit_text(texts['main_menu'], reply_markup=get_main_menu(user_id))
    await callback_query.answer()

# Обработчик кнопки "Корзина"
@dp.callback_query(F.data == "cart")
async def show_cart(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS[lang]
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.product_id, p.name, p.price, c.quantity 
        FROM cart c 
        JOIN products p ON c.product_id = p.product_id 
        WHERE c.user_id = ?
    ''', (user_id,))
    
    cart_items = cursor.fetchall()
    conn.close()
    
    if not cart_items:
        await callback_query.message.edit_text(texts['cart_empty'], reply_markup=get_main_menu(user_id))
        await callback_query.answer()
        return
    
    cart_text = texts['cart_title']
    total_price = 0
    
    for product_id, name, price, quantity in cart_items:
        item_total = price * quantity
        total_price += item_total
        
        cart_text += f"📦 **{name}**\n"
        cart_text += f"   {texts['quantity'].format(quantity=quantity)}\n"
        cart_text += f"   {texts['item_total'].format(total=item_total)}\n"
        cart_text += "   ────────────────────\n"
    
    cart_text += f"\n{texts['total'].format(total=total_price)}"
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text=texts['checkout'], callback_data="checkout"),
        InlineKeyboardButton(text=texts['back_to_menu'], callback_data="back_to_main")
    )
    builder.adjust(1)
    
    await callback_query.message.edit_text(cart_text, reply_markup=builder.as_markup())
    await callback_query.answer()

# Обработчик кнопки "Магазин"
@dp.callback_query(F.data == "shop")
async def show_shop(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    shop_text = get_shop_text(page=0, user_id=user_id)
    keyboard, page_info = get_shop_keyboard(page=0, user_id=user_id)
    
    await callback_query.message.edit_text(shop_text, reply_markup=keyboard)
    await callback_query.answer()

# Обработчик пагинации магазина
@dp.callback_query(F.data.startswith("page_"))
async def change_page(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    page = int(callback_query.data.split('_')[1])
    
    shop_text = get_shop_text(page=page, user_id=user_id)
    keyboard, page_info = get_shop_keyboard(page=page, user_id=user_id)
    
    await callback_query.message.edit_text(shop_text, reply_markup=keyboard)
    await callback_query.answer()

# Обработчик добавления товара в корзину
@dp.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    product_id = int(callback_query.data.split('_')[-1])
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    # Проверяем, есть ли товар уже в корзине
    cursor.execute('SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    result = cursor.fetchone()
    
    if result:
        # Увеличиваем количество
        cursor.execute('UPDATE cart SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    else:
        # Добавляем новый товар
        cursor.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)', (user_id, product_id))
    
    conn.commit()
    
    # Получаем название товара для уведомления
    cursor.execute('SELECT name FROM products WHERE product_id = ?', (product_id,))
    product_name = cursor.fetchone()[0]
    
    conn.close()
    
    lang = get_user_language(user_id)
    texts = TEXTS[lang]
    
    await callback_query.answer(texts['added_to_cart'].format(name=product_name))

# Обработчик увеличения количества товара
@dp.callback_query(F.data.startswith("increase_"))
async def increase_quantity(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    product_id = int(callback_query.data.split('_')[-1])
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE cart SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    conn.commit()
    conn.close()
    
    # Обновляем сообщение магазина
    page_match = re.search(r'page_(\d+)', callback_query.message.text)
    current_page = int(page_match.group(1)) if page_match else 0
    
    shop_text = get_shop_text(page=current_page, user_id=user_id)
    keyboard, page_info = get_shop_keyboard(page=current_page, user_id=user_id)
    
    await callback_query.message.edit_text(shop_text, reply_markup=keyboard)
    await callback_query.answer()

# Обработчик уменьшения количества товара
@dp.callback_query(F.data.startswith("decrease_"))
async def decrease_quantity(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    product_id = int(callback_query.data.split('_')[-1])
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    result = cursor.fetchone()
    
    if result and result[0] > 1:
        cursor.execute('UPDATE cart SET quantity = quantity - 1 WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    else:
        cursor.execute('DELETE FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    
    conn.commit()
    conn.close()
    
    # Обновляем сообщение магазина
    page_match = re.search(r'page_(\d+)', callback_query.message.text)
    current_page = int(page_match.group(1)) if page_match else 0
    
    shop_text = get_shop_text(page=current_page, user_id=user_id)
    keyboard, page_info = get_shop_keyboard(page=current_page, user_id=user_id)
    
    await callback_query.message.edit_text(shop_text, reply_markup=keyboard)
    await callback_query.answer()

# Обработчик оформления заказа
@dp.callback_query(F.data == "checkout")
async def start_checkout(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS[lang]
    
    # Проверяем, что корзина не пуста
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM cart WHERE user_id = ?', (user_id,))
    cart_count = cursor.fetchone()[0]
    conn.close()
    
    if cart_count == 0:
        await callback_query.answer(texts['empty_cart_error'])
        return
    await state.set_state(OrderStates.waiting_for_phone)
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=texts['cancel_order'], callback_data="cancel_order"))
    
    await callback_query.message.edit_text(texts['enter_phone'], reply_markup=builder.as_markup())
    await callback_query.answer()

# Обработчик отмены заказа
@dp.callback_query(F.data == "cancel_order")
async def cancel_order(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS[lang]
    
    await state.clear()
    await callback_query.message.edit_text(texts['order_cancelled'], reply_markup=get_main_menu(user_id))
    await callback_query.answer()

# Обработчик ввода телефона
@dp.message(OrderStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS[lang]
    
    phone_pattern = r'^\+998\d{9}$'
    if not re.match(phone_pattern, message.text):
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text=texts['cancel_order'], callback_data="cancel_order"))
        
        await message.answer(texts['invalid_phone'], reply_markup=builder.as_markup())
        return
    
    await state.update_data(phone=message.text)
    await state.set_state(OrderStates.waiting_for_room)
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=texts['cancel_order'], callback_data="cancel_order"))
    
    await message.answer(texts['enter_room'], reply_markup=builder.as_markup())

# Обработчик ввода номера комнаты
@dp.message(OrderStates.waiting_for_room)
async def process_room(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    texts = TEXTS[lang]
    
    if not message.text.isdigit():
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text=texts['cancel_order'], callback_data="cancel_order"))
        
        await message.answer(texts['invalid_room'], reply_markup=builder.as_markup())
        return
    
    room_number = message.text
    data = await state.get_data()
    phone_number = data['phone']
    
    # Получаем информацию о заказе
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.name, p.price, c.quantity 
        FROM cart c 
        JOIN products p ON c.product_id = p.product_id 
        WHERE c.user_id = ?
    ''', (user_id,))
    
    cart_items = cursor.fetchall()
    
    # Формируем текст заказа
    order_text = texts['your_order']
    total_price = 0
    
    for name, price, quantity in cart_items:
        item_total = price * quantity
        total_price += item_total
        order_text += f"• {name} x{quantity} - {item_total:,} сум\n"
    
    order_text += f"\n{texts['phone'].format(phone=phone_number)}\n"
    order_text += f"{texts['room'].format(room=room_number)}\n"
    order_text += f"\n💵 **Итого: {total_price:,} сум**"
    
    # Сохраняем заказ в базу
    cursor.execute('''
        INSERT INTO orders (user_id, order_text, total_price, phone_number, room_number)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, order_text, total_price, phone_number, room_number))
    
    # Очищаем корзину
    cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    # Отправляем подтверждение пользователю
    complete_text = texts['order_completed']
    complete_text += order_text
    complete_text += f"\n\n{texts['delivery_time']}"
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=texts['return_to_shop'], callback_data="shop"))
    builder.add(InlineKeyboardButton(text=texts['main_menu_btn'], callback_data="back_to_main"))
    builder.adjust(1)
    
    await message.answer(complete_text, reply_markup=builder.as_markup())
    
    # Отправляем уведомление админу
    admin_text = f"📦 **Новый заказ!**\n\n"
    admin_text += f"👤 Пользователь: @{message.from_user.username or 'нет'}\n"
    admin_text += f"📞 Телефон: {phone_number}\n"
    admin_text += f"🏨 Комната: {room_number}\n\n"
    admin_text += order_text
    
    await bot.send_message(ADMIN_ID, admin_text)
    
    await state.clear()

# Запуск бота
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
