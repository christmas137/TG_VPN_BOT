from aiogram import types
from aiogram.types import InputFile
import db.database
from config import dp, bot, admin_id
from keybords import get_try_inline_keyboard, get_subscription_options_keyboard, get_key_vpn, get_key_download
from payment import send_invoice
from db.function_db import SubscriptionManager
subscription_manager = SubscriptionManager(db.database.db_path)

# Пример обработчика команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    inline_kb = get_try_inline_keyboard()

    await message.answer(text=(
        "<b>Привет! 👋 Я бот ANONYMO,</b> твой надежный помощник в мире безопасного и анонимного интернет-сёрфинга.\n"
        "С моей помощью ты можешь легко подключиться к VPN и забыть о гео-блокировках, следах в интернете и ограничениях провайдера.\n\n"
        "<b>Чтобы начать пользоваться услугами VPN, тебе нужно приобрести подписку.</b>\n\n"
        "Если у тебя есть промокод, ты можешь активировать его, отправив мне команду <code>/promo</code>.\n\n"
        "Также ты можешь узнать о наших тарифах, написав мне команду <code>/tariffs</code>.\n\n"
        "<i>Добро пожаловать в безграничный мир интернета с ANONYMO! 🌐✨</i>"
    ), parse_mode='HTML', reply_markup=inline_kb)


@dp.message_handler(commands=['shadowsocks'])
async def info_shadowsocks(message: types.Message):
    await message.answer(
        '🔐 Shadowsocks - это уникальный протокол, который обеспечивает высокий уровень безопасности во время использования интернета. Он был создан как реакция на необходимость обхода Интернет-цензуры и фильтрации в некоторых странах и регионах.\n\n'
        '🕰️ В начале 2010-х годов в Китае была усилена интернет-цензура, и многие пользователи искали способы обойти блокировки и сохранить свою анонимность. В ответ на это появился Shadowsocks - проект с открытым исходным кодом, созданный одним из разработчиков, чтобы помочь пользователям обходить цензуру и оставаться в сети анонимными.\n\n'
        '🤐 С помощью Shadowsocks, ваши онлайн-деяния остаются приватными и скрытыми. Никто не может увидеть, какие веб-сайты вы посещаете или что вы отправляете в интернете.\n\n'
        '💨 Важно также отметить, что Shadowsocks обеспечивает высокую скорость подключения. Вы можете наслаждаться быстрым и стабильным интернетом, даже когда используете VPN.\n\n'
        '🤔 Исходя из этой истории, Shadowsocks стал надежным инструментом для обхода цензуры и обеспечения безопасности в интернете. Поэтому, если вы цените свою приватность и безопасность в интернете, и при этом хотите иметь быстрый доступ к любым веб-ресурсам, то выбор Shadowsocks является отличным решением для вас. Этот протокол обеспечивает лучшее из обоих миров: безопасность и скорость! 💻🔒🚀\n\n'
        'Подробнее о протоколе можно прочитать в статье на Википедии: https://en.wikipedia.org/wiki/Shadowsocks'
    )


@dp.message_handler(commands=['download'])
async def download_info(message: types.Message):
    inline_kb = get_key_download()
    await message.answer(
        'Порядок действий:\n\n'
        'Шаг 1. Скопируй URL сервера (ss://) 🔗\n'
        'Шаг 2. Скачай приложение OutLine ⬇️\n'
        'Шаг 3. Открой и вставь URL (ss://) в OutLine ➕\n\n'
        'Если не получилось ниже приведена подробная инструкция по установке:\n\n'
        '[Iphone](https://telegra.ph/Instrukciya-po-ustanovke-Outline-na-iPhone-08-19)\n'
        '[Android](https://telegra.ph/Instrukciya-po-ustanovke-Outline-na-Android-08-19)\n'
        '[Windows](https://telegra.ph/Instrukciya-na-ustanovku-Outline-Windows-08-19)',
        parse_mode="Markdown",
        reply_markup=inline_kb
        )

@dp.message_handler(commands=['servers'])
async def send_servers(message:types.Message):
    inline_kb = get_key_vpn()
    await message.answer(text="<b>Выбирай к какому серверу хочешь подключиться:</b>",
                         parse_mode="HTML",
                         reply_markup=inline_kb)


@dp.callback_query_handler(lambda query: query.data in ['germany_server', 'amsterdam_server'])
async def handle_vpn_server_choice(query: types.CallbackQuery):
    user_id = query.from_user.id
    server_choice = query.data

    # Проверяем подписку и получаем ключ VPN
    response_message = await subscription_manager.check_subscription_and_get_vpn_key(user_id, server_choice)

    # Отправляем ответ пользователю
    await query.message.answer(f"{response_message}", parse_mode='HTML')

    # Убедитесь, что ответили на callback query, чтобы у пользователя не оставалось "висящего" уведомления о нажатии
    await query.answer()

@dp.message_handler(commands=['id'])
async def get_id(message: types.Message):
    user_id = message.from_user.id
    await message.reply(f'<b>Твой Telegram id:</b> {user_id}', parse_mode="HTML")

@dp.message_handler(commands=['promo'])
async def handle_promo_command(message: types.Message):
    await message.answer(
        "🔑 <b>Активация промокода</b> 🔑\n\n"
        "Введи свой промокод для активации или продления подписки. Промокод должен состоять из <b>9 символов</b>, например, <code>AAAYYYUUU</code>.\n",
        parse_mode="HTML"
    )

@dp.message_handler(lambda message: len(message.text) == 9)
async def handle_promo_code(message: types.Message):
    user_id = message.from_user.id
    promo_code = message.text
    response = await subscription_manager.activate_promo_code(user_id, promo_code)
    await message.answer(response, parse_mode="HTML")

@dp.message_handler(commands=['tariffs'])
async def get_tariffs(message: types.Message):
    inline_kb = get_subscription_options_keyboard()
    await message.answer(text='<b>Подписка на ANONYMO предлагает вам следующее:</b>\n'
                              '- Высокая скорость до 100 МБ/с\n'
                              '- Неограниченный МБ трафик\n'
                              '- Подключение для ПК (macOS, Windows) 🖥\n'
                              '- Быстрое подключение и отсутствие сбоев\n'
                              '- Лучший защищённый протокол - Shadowsocks\n'
                              '- Два быстрых сервера: 🇩🇪 и 🇳🇱\n'
                              '- <b>Лучшая стоимость в сети:</b>\n'
                              '1 месяц  - 100 рублей\n'
                              '3 месяца - 300 рублей\n'
                              '6 месяцев - 600 рублей\n'
                              '12 месяцев - 1100 рублей',
                             parse_mode='HTML', reply_markup=inline_kb )

@dp.callback_query_handler(text="try")
async def handle_try_callback(query: types.CallbackQuery):
    sub_options_kb = get_subscription_options_keyboard()
    await query.message.answer("<b>На какой срок тебе нужен VPN?🤔💭</b>", reply_markup=sub_options_kb, parse_mode='HTML')
    await query.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('subscription_'))
async def handle_subscription_callback(query: types.CallbackQuery):
    # Извлекаем срок подписки из callback_data
    subscription_plan = query.data.split('_')[1]

    # Вызываем функцию отправки счета
    await send_invoice(query.message, subscription_plan)

    await query.answer()

@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    # Здесь можно добавить дополнительные проверки платежа
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=types.ContentTypes.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    # Извлекаем тип подписки из invoice_payload
    subscription_plan = message.successful_payment.invoice_payload
    # Извлекаем уникальный идентификатор платежа
    payment_id = message.successful_payment.provider_payment_charge_id
    # Извлекаем user_id
    user_id = message.from_user.id
    inline_kb = get_key_vpn()
    # Предположим, что subscription_manager уже инициализирован
    await subscription_manager.add_or_update_subscription(user_id, subscription_plan, payment_id)

    await message.answer("Спасибо за покупку! Твоя подписка была успешно активирована!🙌")
    await message.answer(text="<b> Теперь выбери к какому серверу хочешь подключиться:</b>",
                         parse_mode="HTML",
                         reply_markup=inline_kb)

@dp.message_handler(commands=['addpromocode'])
async def add_promo_code(message: types.Message):
    user_id = message.from_user.id
    if user_id not in admin_id:
        await message.answer("У тебя нет прав для выполнения этой команды❌")
        return
    # Разбор сообщения для получения промокода
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажи промокод командой в формате: <code>/addpromocode</code> ваш_промокод", parse_mode="HTML")
        return
    promo_code = parts[1].upper()  # Преобразование промокода к верхнему регистру для унификации
    # Добавление промокода в базу данных (псевдокод, требует реализации)
    await subscription_manager.add_promo_code(promo_code)
    await message.answer(f"Промокод {promo_code} успешно добавлен.🔑")

@dp.message_handler(commands=['mysub'])
async def my_subscription(message: types.Message):
    user_id = message.from_user.id
    subscription_info = await subscription_manager.get_subscription_info(user_id)
    if subscription_info:
        await message.answer(f"<b>Твоя подписка действительна до {subscription_info['subscription_end']}.</b>", parse_mode="HTML")
    else:
        await message.answer("<b>У тебя нет активной подписки.</b>", parse_mode="HTML")

@dp.message_handler(commands=['about'])
async def about_info(message: types.Message):
    about_text = (
        "🌐 История ANONYMO 🌐\n\n"
        "Давным-давно, в мире, где интернет становился все более важным и доступным для каждого, два энтузиаста собрались вместе, чтобы сделать онлайн-мир более открытым и безопасным. Эти два человека разделяли общее стремление - обеспечить всем доступ к открытому интернету с максимальной анонимностью и безопасностью.\n\n"
        "🤝 Наши создатели: 🤝\n\n"
        "Создатели ANONYMOVPN - это два страстных сторонника свободы интернета и онлайн-конфиденциальности. Их партнерство началось из желания поделиться этой свободой с остальными и помочь пользователям справиться с географическими ограничениями и цензурой. Они понимали, что доступ к информации и приватность онлайн - это фундаментальные права каждого человека.\n\n"
        "🔒 Принципы и обещания: 🔒\n\n"
        "ANONYMO обязуется соблюдать несколько ключевых принципов:\n\n"
        "- Свободный доступ: Мы убеждены, что интернет должен быть доступен каждому, независимо от его местоположения, и мы боремся за свободу онлайн-содержания. Мы считаем, что никто не должен быть лишен доступа к информации из-за географических ограничений.\n\n"
        "- Анонимность: Мы используем протокол, который невозможно заблокировать в России и многих других странах, чтобы гарантировать полную анонимность и конфиденциальность вашей онлайн-активности. Мы признаем важность защиты данных и личной жизни каждого пользователя.\n\n"
        "- Поддержка и решение проблем: Мы готовы решать любые возникающие проблемы и обеспечивать надежную онлайн-поддержку для наших пользователей. Мы верим, что каждый пользователь заслуживает помощи и поддержки.\n\n"
        "- Собственное приложение: В ближайшем будущем мы планируем выпустить свое собственное приложение, чтобы упростить использование ANONYMOVPN для всех. Это приложение будет обеспечивать легкий и удобный доступ к нашим услугам.\n\n"
    )
    await message.answer(about_text)

@dp.callback_query_handler(text="download_file")
async def download_file_callback(query: types.CallbackQuery):
    file_path = 'H:\\dev\\bots\\vpn_bot\\bot\\Outline-Client.exe'
    file = InputFile(file_path)

    await bot.send_document(chat_id=query.from_user.id, document=file)

    await query.answer("Файл отправлен.")