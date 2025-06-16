from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from asgiref.sync import sync_to_async

from django.db import transaction

from shop.models import User, Category, Product, ProductColor, Cart, CartItem
from bot.config import ADMIN_TELEGRAM_IDS


router = Router()

def register_handlers(dp):
    dp.include_router(router)

@router.message(CommandStart())
async def start_command(message: Message):
    tg_id = message.from_user.id
    user = await sync_to_async(User.objects.filter(telegram_id=tg_id).first)()
    if not user:
        await message.answer(
            "🇺🇿 Tilni tanlang / 🇷🇺 Выберите язык",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]
            ], resize_keyboard=True)
        )
        return
    lang = user.language
    text = "Assalomu alaykum!" if lang == "uz" else "Здравствуйте!"
    main_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Katalog" if lang == "uz" else "🛍 Каталог")],
            [KeyboardButton(text="🛒 Savatcha" if lang == "uz" else "🛒 Корзина")],
            [KeyboardButton(text="📝 Buyurtmalarim" if lang == "uz" else "📝 Мои заказы")]
        ],
        resize_keyboard=True
    )
    await message.answer(text, reply_markup=main_menu)

@router.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def choose_language(message: Message):
    lang = "uz" if "O'zbek" in message.text else "ru"
    tg_id = message.from_user.id
    name = message.from_user.full_name
    @sync_to_async
    def get_or_create_user():
        with transaction.atomic():
            user, created = User.objects.get_or_create(
                telegram_id=tg_id,
                defaults={
                    "name": name,
                    "language": lang,
                }
            )
            if not created:
                user.language = lang
                user.save()
            return user
    user = await get_or_create_user()
    # Ask phone number via contact button
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish / Отправить номер", request_contact=True)]],
        resize_keyboard=True
    )
    text = (
        "Iltimos, telefon raqamingizni yuboring." if lang == "uz"
        else "Пожалуйста, отправьте свой номер телефона."
    )
    await message.answer(text, reply_markup=kb)

@router.message(F.contact)
async def handle_contact(message: Message):
    contact = message.contact
    tg_id = message.from_user.id
    phone = contact.phone_number
    @sync_to_async
    def update_user_phone():
        try:
            user = User.objects.get(telegram_id=tg_id)
            user.phone = phone
            user.save()
            lang = user.language
            return lang
        except User.DoesNotExist:
            return None
    lang = await update_user_phone()
    if lang:
        main_menu = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🛍 Katalog" if lang == "uz" else "🛍 Каталог")],
                [KeyboardButton(text="🛒 Savatcha" if lang == "uz" else "🛒 Корзина")]
            ],
            resize_keyboard=True
        )
        text = (
            "Ro'yxatdan o'tdingiz! Katalogga xush kelibsiz." if lang == "uz"
            else "Вы успешно зарегистрированы! Добро пожаловать в каталог."
        )
        await message.answer(text, reply_markup=main_menu)
    else:
        await message.answer("Avval tilni tanlang / Сначала выберите язык")

@router.message(Command("me"))
async def show_profile(message: Message):
    tg_id = message.from_user.id
    user = await sync_to_async(User.objects.filter(telegram_id=tg_id).first)()
    if not user:
        await message.answer("Ro'yxatdan o'tmagansiz / Вы не зарегистрированы")
        return
    text = (
        f"👤 Ism: {user.name}\n"
        f"📞 Telefon: {user.phone}\n"
        f"Til: {'O`zbekcha' if user.language == 'uz' else 'Русский'}"
    )
    await message.answer(text)

# Helper to get user's language
async def get_user_language(tg_id):
    user = await sync_to_async(User.objects.filter(telegram_id=tg_id).first)()
    return user.language if user else "uz"

# --- Category Browsing ---

async def category_keyboard(parent_id=None, lang="uz"):
    categories = await sync_to_async(list)(Category.objects.filter(parent_id=parent_id))
    keyboard = []
    for cat in categories:
        name = cat.name_uz if lang == "uz" else cat.name_ru
        keyboard.append([InlineKeyboardButton(text=name, callback_data=f"cat_{cat.id}")])
    if parent_id:
        keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga" if lang=="uz" else "⬅️ Назад", callback_data="cat_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(F.text.in_(["🛍 Katalog", "🛍 Каталог"]))
async def show_categories(message: Message):
    lang = await get_user_language(message.from_user.id)
    kb = await category_keyboard(lang=lang)
    await message.answer("Kategoriyalar:" if lang=="uz" else "Категории:", reply_markup=kb)

@router.callback_query(F.data.startswith("cat_"))
async def category_callback(query: CallbackQuery):
    tg_id = query.from_user.id
    lang = await get_user_language(tg_id)
    data = query.data
    if data == "cat_back":
        parent_id = None
    else:
        cat_id = int(data.split("_")[1])
        parent_id = await sync_to_async(lambda: Category.objects.get(id=cat_id).parent_id)()
    kb = await category_keyboard(parent_id=parent_id, lang=lang)
    text = "Kategoriyalar:" if lang=="uz" else "Категории:"
    await query.message.edit_text(text, reply_markup=kb)
    await query.answer()

@router.callback_query(F.data.startswith("cat_"))
async def show_category(query: CallbackQuery):
    tg_id = query.from_user.id
    lang = await get_user_language(tg_id)
    data = query.data
    if data == "cat_back":
        parent_id = None
        kb = await category_keyboard(parent_id, lang)
        await query.message.edit_text("Kategoriyalar:" if lang=="uz" else "Категории:", reply_markup=kb)
        await query.answer()
        return

    cat_id = int(data.split("_")[1])
    category = await sync_to_async(Category.objects.get)(id=cat_id)
    subcats = await sync_to_async(list)(Category.objects.filter(parent=category))
    if subcats:
        kb = await category_keyboard(category.id, lang)
        await query.message.edit_text(
            category.name_uz if lang=="uz" else category.name_ru,
            reply_markup=kb
        )
    else:
        products = await sync_to_async(list)(Product.objects.filter(categories=category))
        if not products:
            await query.message.edit_text("Mahsulotlar yo'q." if lang=="uz" else "Нет товаров.", reply_markup=None)
        else:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=(p.name_uz if lang=="uz" else p.name_ru),
                    callback_data=f"prod_{p.id}"
                )] for p in products
            ] + [[InlineKeyboardButton(text="⬅️ Orqaga" if lang=="uz" else "⬅️ Назад", callback_data=f"cat_{category.parent_id or ''}")]])
            await query.message.edit_text(
                category.name_uz if lang=="uz" else category.name_ru,
                reply_markup=kb
            )
    await query.answer()

# --- Product View ---

@router.callback_query(F.data.startswith("prod_"))
async def product_callback(query: CallbackQuery):
    tg_id = query.from_user.id
    lang = await get_user_language(tg_id)
    prod_id = int(query.data.split("_")[1])
    product = await sync_to_async(Product.objects.get)(id=prod_id)
    # Use sync_to_async for related queries as well
    colors = await sync_to_async(list)(product.colors.all())
    # For first category (for back button)
    first_category = await sync_to_async(lambda: product.categories.first())()
    text = (
        f"<b>{product.name_uz if lang=='uz' else product.name_ru}</b>\n\n"
        f"{product.description_uz if lang=='uz' else product.description_ru}\n\n"
        f"{'Ranglar:' if lang=='uz' else 'Цвета:'}\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{c.name_uz if lang=='uz' else c.name_ru} - {c.price} so'm",
            callback_data=f"color_{c.id}"
        )] for c in colors
    ] + [[InlineKeyboardButton(
        text="⬅️ Orqaga" if lang=="uz" else "⬅️ Назад",
        callback_data=f"cat_{first_category.id if first_category else ''}"
    )]])
    await query.message.answer_photo(
        photo=product.main_image.url,
        caption=text,
        reply_markup=kb
    )
    await query.answer()

@router.callback_query(F.data.startswith("color_"))
async def color_callback(query: CallbackQuery):
    tg_id = query.from_user.id
    lang = await get_user_language(tg_id)
    color_id = int(query.data.split("_")[1])
    color = await sync_to_async(ProductColor.objects.select_related("product").get)(id=color_id)
    product = color.product

    # Show images for this color if available
    color_images = await sync_to_async(list)(color.images.all())
    if color_images:
        for img in color_images:
            await query.message.answer_photo(
                photo=img.image.url,
                caption=None
            )
    # Ask to add to cart
    text = (
        f"<b>{product.name_uz if lang=='uz' else product.name_ru}</b>\n"
        f"{color.name_uz if lang=='uz' else color.name_ru} - {color.price} so'm\n"
        f"{'Savatchaga qo‘shilsinmi?' if lang=='uz' else 'Добавить в корзину?'}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="➕ Savatchaga" if lang=="uz" else "➕ В корзину",
                callback_data=f"addcart_{color.id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Orqaga" if lang=="uz" else "⬅️ Назад",
                callback_data=f"prod_{product.id}"
            )
        ]
    ])
    await query.message.answer(text, reply_markup=kb)
    await query.answer()

@router.callback_query(F.data.startswith("addcart_"))
async def add_to_cart_callback(query: CallbackQuery):
    tg_id = query.from_user.id
    lang = await get_user_language(tg_id)
    color_id = int(query.data.split("_")[1])
    color = await sync_to_async(ProductColor.objects.select_related("product").get)(id=color_id)
    product = color.product
    user = await sync_to_async(User.objects.get)(telegram_id=tg_id)
    cart, _ = await sync_to_async(Cart.objects.get_or_create)(user=user)

    item, created = await sync_to_async(CartItem.objects.get_or_create)(
        cart=cart,
        product=product,
        color=color,
        defaults={"quantity": 1}
    )
    if not created:
        item.quantity += 1
        await sync_to_async(item.save)()
    text = (
        f"✅ Savatchaga qo‘shildi!" if lang=="uz" else "✅ Добавлено в корзину!"
    )
    main_menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍 Katalog" if lang=="uz" else "🛍 Каталог")],
        [KeyboardButton(text="🛒 Savatcha" if lang=="uz" else "🛒 Корзина")]
    ], resize_keyboard=True)
    await query.message.answer(text, reply_markup=main_menu)
    await query.answer()

# --- Cart View ---

@router.message(F.text.in_(["🛒 Savatcha", "🛒 Корзина"]))
async def show_cart(message: Message):
    tg_id = message.from_user.id
    lang = await get_user_language(tg_id)
    user = await sync_to_async(User.objects.get)(telegram_id=tg_id)
    cart = getattr(user, "cart", None)
    items = await sync_to_async(lambda: list(cart.items.select_related("product", "color")))() if cart else []
    if not cart or not items:
        await message.answer("Savatchangiz bo‘sh." if lang=="uz" else "Ваша корзина пуста.")
        return
    lines = []
    total = 0
    for idx, item in enumerate(items, start=1):
        prod_name = item.product.name_uz if lang=="uz" else item.product.name_ru
        color_name = item.color.name_uz if lang=="uz" else item.color.name_ru
        price = item.color.price * item.quantity
        total += price
        lines.append(
            f"{idx}. {prod_name} ({color_name}) x{item.quantity} - {price} so'm"
        )
    lines.append(f"\n<b>{'Jami' if lang=='uz' else 'Итого'}: {total} so'm</b>")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Tozalash" if lang=="uz" else "Очистить",
                callback_data="cart_clear"
            ),
            InlineKeyboardButton(
                text="Buyurtma berish" if lang=="uz" else "Оформить заказ",
                callback_data="cart_order"
            )
        ]
    ])
    await message.answer("\n".join(lines), reply_markup=kb)

# --- Cart Clear ---

@router.callback_query(F.data == "cart_clear")
async def clear_cart_callback(query: CallbackQuery):
    tg_id = query.from_user.id
    lang = await get_user_language(tg_id)
    user = await sync_to_async(User.objects.get)(telegram_id=tg_id)
    cart = getattr(user, "cart", None)
    if cart:
        await sync_to_async(lambda: cart.items.all().delete())()
    await query.message.edit_text("Savatcha tozalandi!" if lang=="uz" else "Корзина очищена!")
    await query.answer()

# --- Order (initiate only, does not complete payment) ---

@router.callback_query(F.data == "cart_order")
async def cart_order_callback(query: CallbackQuery):
    tg_id = query.from_user.id
    lang = await get_user_language(tg_id)
    user = await sync_to_async(User.objects.get)(telegram_id=tg_id)
    cart = getattr(user, "cart", None)
    items = await sync_to_async(lambda: list(cart.items.all()))() if cart else []
    if not cart or not items:
        await query.message.edit_text("Savatchangiz bo‘sh." if lang=="uz" else "Ваша корзина пуста.")
        await query.answer()
        return
    from shop.models import Order, OrderItem
    order = await sync_to_async(Order.objects.create)(user=user, status="created")
    for item in items:
        await sync_to_async(OrderItem.objects.create)(
            order=order,
            product=item.product,
            color=item.color,
            quantity=item.quantity,
            price=item.color.price
        )
    await sync_to_async(lambda: cart.items.all().delete())()
    await query.message.edit_text(
        "Buyurtmangiz qabul qilindi! Operator tez orada bog‘lanadi." if lang=="uz"
        else "Ваш заказ принят! Оператор скоро свяжется с вами."
    )
    await query.answer()

# --- Remove Item from Cart ---

@router.callback_query(F.data.startswith("cartitem_del_"))
async def remove_cart_item_callback(query: CallbackQuery):
    tg_id = query.from_user.id
    lang = await get_user_language(tg_id)
    cartitem_id = int(query.data.split("_")[2])
    try:
        user = await sync_to_async(User.objects.get)(telegram_id=tg_id)
        cart = user.cart
        cart_item = await sync_to_async(cart.items.get)(id=cartitem_id)
        await sync_to_async(cart_item.delete)()
        text = ("Mahsulot savatchadan olib tashlandi!" if lang == "uz" else "Товар удален из корзины!")
    except (User.DoesNotExist, AttributeError, CartItem.DoesNotExist):
        text = ("Xatolik! Savatcha topilmadi." if lang == "uz" else "Ошибка! Корзина не найдена.")
    await query.message.answer(text)
    await query.answer()

# --- Change Item Quantity ---

@router.callback_query(F.data.startswith("cartitem_qty_"))
async def change_cart_item_qty_callback(query: CallbackQuery):
    tg_id = query.from_user.id
    lang = await get_user_language(tg_id)
    _, _, cartitem_id, action = query.data.split("_")
    try:
        user = await sync_to_async(User.objects.get)(telegram_id=tg_id)
        cart = user.cart
        cart_item = await sync_to_async(cart.items.get)(id=cartitem_id)
        if action == "inc":
            cart_item.quantity += 1
            await sync_to_async(cart_item.save)()
            text = ("Miqdori oshirildi." if lang == "uz" else "Количество увеличено.")
        elif action == "dec":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                await sync_to_async(cart_item.save)()
                text = ("Miqdori kamaytirildi." if lang == "uz" else "Количество уменьшено.")
            else:
                await sync_to_async(cart_item.delete)()
                text = ("Mahsulot savatchadan olib tashlandi!" if lang == "uz" else "Товар удален из корзины!")
        else:
            text = ("Noma'lum amal!" if lang == "uz" else "Неизвестное действие!")
    except (User.DoesNotExist, AttributeError, CartItem.DoesNotExist):
        text = ("Xatolik! Savatcha topilmadi." if lang == "uz" else "Ошибка! Корзина не найдена.")
    await query.message.answer(text)
    await query.answer()

# --- Improved Cart View with Controls ---

@router.message(F.text.in_(["🛒 Savatcha", "🛒 Корзина"]))
async def show_cart(message: Message):
    tg_id = message.from_user.id
    lang = await get_user_language(tg_id)
    user = await sync_to_async(User.objects.get)(telegram_id=tg_id)
    cart = getattr(user, "cart", None)
    items = await sync_to_async(lambda: list(cart.items.select_related("product", "color")))() if cart else []
    if not cart or not items:
        await message.answer("Savatchangiz bo‘sh." if lang=="uz" else "Ваша корзина пуста.")
        return
    lines = []
    total = 0
    inline_keyboard = []
    for idx, item in enumerate(items, start=1):
        prod_name = item.product.name_uz if lang=="uz" else item.product.name_ru
        color_name = item.color.name_uz if lang=="uz" else item.color.name_ru
        price = item.color.price * item.quantity
        total += price
        lines.append(
            f"{idx}. {prod_name} ({color_name}) x{item.quantity} - {price} so'm"
        )
        inline_keyboard.append([
            InlineKeyboardButton(
                text="➖", callback_data=f"cartitem_qty_{item.id}_dec"
            ),
            InlineKeyboardButton(
                text=f"{item.quantity}",
                callback_data="noop"
            ),
            InlineKeyboardButton(
                text="➕", callback_data=f"cartitem_qty_{item.id}_inc"
            ),
            InlineKeyboardButton(
                text="❌", callback_data=f"cartitem_del_{item.id}"
            )
        ])
    lines.append(f"\n<b>{'Jami' if lang=='uz' else 'Итого'}: {total} so'm</b>")
    inline_keyboard.append([
        InlineKeyboardButton(
            text="Tozalash" if lang=="uz" else "Очистить",
            callback_data="cart_clear"
        ),
        InlineKeyboardButton(
            text="Buyurtma berish" if lang=="uz" else "Оформить заказ",
            callback_data="cart_order"
        )
    ])
    kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    await message.answer("\n".join(lines), reply_markup=kb)

# --- No-op handler for disabled buttons ---

@router.callback_query(F.data == "noop")
async def noop_callback(query: CallbackQuery):
    await query.answer()

@router.callback_query(F.data == "cart_order")
async def cart_order_callback(query: CallbackQuery):
    tg_id = query.from_user.id
    lang = await get_user_language(tg_id)
    user = await sync_to_async(User.objects.get)(telegram_id=tg_id)
    cart = getattr(user, "cart", None)
    items = await sync_to_async(lambda: list(cart.items.all()))() if cart else []
    if not cart or not items:
        await query.message.edit_text("Savatchangiz bo‘sh." if lang=="uz" else "Ваша корзина пуста.")
        await query.answer()
        return
    from shop.models import Order, OrderItem
    order = await sync_to_async(Order.objects.create)(user=user, status="created")
    order_lines = []
    for item in items:
        await sync_to_async(OrderItem.objects.create)(
            order=order,
            product=item.product,
            color=item.color,
            quantity=item.quantity,
            price=item.color.price
        )
        prod_name = item.product.name_uz if lang == "uz" else item.product.name_ru
        color_name = item.color.name_uz if lang == "uz" else item.color.name_ru
        order_lines.append(f"{prod_name} ({color_name}) x{item.quantity} - {item.color.price * item.quantity} so'm")
    await sync_to_async(lambda: cart.items.all().delete())()
    await query.message.edit_text(
        "Buyurtmangiz qabul qilindi! Operator tez orada bog‘lanadi." if lang=="uz"
        else "Ваш заказ принят! Оператор скоро свяжется с вами."
    )
    await query.answer()
    # Notify admins
    bot: Bot = query.bot
    admin_text = (f"🆕 Yangi buyurtma!\n\n" if lang=="uz" else "🆕 Новый заказ!\n\n")
    admin_text += (
        f"Foydalanuvchi: {user.name}\n"
        f"Tel: {user.phone}\n"
        f"Telegram ID: {user.telegram_id}\n\n"
        f"Buyurtma:\n" if lang=="uz" else
        f"Пользователь: {user.name}\n"
        f"Тел: {user.phone}\n"
        f"Telegram ID: {user.telegram_id}\n\n"
        f"Заказ:\n"
    )
    admin_text += "\n".join(order_lines)
    admin_text += f"\n\nOrder ID: {order.id}"
    for admin_id in ADMIN_TELEGRAM_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=admin_text)
        except Exception as e:
            pass  

@router.message(F.text.in_(["📝 Buyurtmalarim", "📝 Мои заказы"]))
async def show_order_history(message: Message):
    tg_id = message.from_user.id
    lang = await get_user_language(tg_id)
    user = await sync_to_async(User.objects.get)(telegram_id=tg_id)
    orders = await sync_to_async(lambda: list(user.orders.order_by('-created_at')[:5]))()
    if not orders:
        await message.answer("Buyurtmalaringiz yo'q." if lang=="uz" else "У вас нет заказов.")
        return
    for order in orders:
        lines = []
        items = await sync_to_async(lambda: list(order.items.select_related("product", "color")))()
        for item in items:
            prod_name = item.product.name_uz if lang == "uz" else item.product.name_ru
            color_name = item.color.name_uz if lang == "uz" else item.color.name_ru
            lines.append(f"{prod_name} ({color_name}) x{item.quantity} - {item.price * item.quantity} so'm")
        order_text = (
            f"📝 Buyurtma #{order.id}\n" if lang == "uz" else f"📝 Заказ #{order.id}\n"
        )
        order_text += "\n".join(lines)
        order_text += f"\n{'Holat' if lang == 'uz' else 'Статус'}: {order.get_status_display()}"
        await message.answer(order_text)