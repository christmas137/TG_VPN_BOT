from aiogram import types
from aiogram.types import LabeledPrice
from config import bot, PROVIDER_TOKEN



SUBSCRIPTION_PRICES = {
    "1m": (10000, "1 месяц - 100 рублей"),  # 10000 копеек = 100 рублей
    "3m": (30000, "3 месяца - 300 рублей"),
    "6m": (60000, "6 месяцев - 600 рублей"),
    "12m": (110000, "12 месяцев - 1100 рублей"),
}

async def send_invoice(message: types.Message, subscription_plan: str):
    # Здесь вы можете определить стоимость в зависимости от выбранного плана подписки
    price_amount, price_label = SUBSCRIPTION_PRICES.get(subscription_plan, (0, "Unknown"))

    prices = [LabeledPrice(label=price_label, amount=price_amount)]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title='Подписка на ANONYMO VPN',
        description=f'Вы выбрали подписку на {subscription_plan}.',
        provider_token=PROVIDER_TOKEN,
        currency='RUB',
        prices=prices,
        start_parameter='create_invoice',
        payload=subscription_plan
    )
