import aiosqlite
from datetime import datetime
from dateutil.relativedelta import relativedelta
from db.database import db_path
from db.vpn_manager import VPNManager


class SubscriptionManager:

    def __init__(self, db_path):
        self.db_path = db_path
        self.vpn_manager = VPNManager()

    async def add_or_update_subscription(self, user_id, subscription_type, key_id):
        subscription_lengths = {
            "1m": 1,  # 1 месяц
            "3m": 3,  # 3 месяца
            "6m": 6,  # 6 месяцев
            "12m": 12  # 12 месяцев
        }

        months = subscription_lengths.get(subscription_type, 1)  # По умолчанию 1 месяц

        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.cursor()

            # Переключаемся на использование UTC времени для текущего времени
            current_utc_time = datetime.utcnow()

            # Проверяем наличие активной подписки
            await cursor.execute("SELECT subscription_end FROM subscriptions WHERE user_id = ?", (user_id,))
            subscription = await cursor.fetchone()

            if subscription:
                # Если подписка найдена, расчитываем new_end_date на основе существующей end_date
                current_end_date = datetime.strptime(subscription[0], "%Y-%m-%d %H:%M:%S")
                if current_end_date < current_utc_time:
                    current_end_date = current_utc_time
                new_end_date = current_end_date + relativedelta(months=months)

                # Обновляем end_date, subscription_plan и subscription_status в базе данных
                await cursor.execute(
                    "UPDATE subscriptions SET subscription_end = ?, subscription_plan = ?, subscription_status = 1 WHERE user_id = ?",
                    (new_end_date.strftime("%Y-%m-%d %H:%M:%S"), subscription_type, user_id))
            else:
                # Если подписка не найдена, создаем новую запись с началом от текущей UTC даты
                new_end_date = current_utc_time + relativedelta(months=months)
                await cursor.execute(
                    "INSERT INTO subscriptions (user_id, subscription_start, subscription_end, subscription_plan, subscription_status, payment_id) VALUES (?, ?, ?, ?, 1, ?)",
                    (
                    user_id, current_utc_time.strftime("%Y-%m-%d %H:%M:%S"), new_end_date.strftime("%Y-%m-%d %H:%M:%S"),
                    subscription_type, key_id))

            await conn.commit()

    async def activate_promo_code(self, user_id: int, promo_code: str):
        promo_code = promo_code.upper()

        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.cursor()

            # Проверяем статус промокода
            await cursor.execute("SELECT is_activated FROM promo_codes WHERE promo_code = ?", (promo_code,))
            result = await cursor.fetchone()

            if result is not None:
                is_activated = result[0]

                if not is_activated:  # Если промокод не активирован (False), значит можно активировать
                    await cursor.execute("UPDATE promo_codes SET is_activated = 1 WHERE promo_code = ?", (promo_code,))
                    await conn.commit()
                    await self.add_or_update_subscription(user_id, "1m", f"Promo: {promo_code}")
                    return "<b>Промокод был успешно активирован</b>🎉🎉🎉\n <b>Вам добавлен 1 месяц подписки</b>✨"
                else:  # Если промокод уже активирован (True)
                    return "<b>Данный промокод уже был кем-то активирован</b>👽"
            else:
                return "<b>Увы..Такого промокода нет</b>😔"

    async def add_promo_code(self, promo_code: str):
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.cursor()
             # Проверка на существование промокода
            await cursor.execute("SELECT * FROM promo_codes WHERE promo_code = ?", (promo_code,))
            if await cursor.fetchone():
                 return "Промокод уже существует."
             # Добавление нового промокода
            await cursor.execute("INSERT INTO promo_codes (promo_code, is_activated) VALUES (?, 0)", (promo_code,))
            await conn.commit()
            return "Промокод успешно добавлен."

    async def handle_vpn_key_creation(self, user_id: int, server_choice: str, existing_vpn_key: str,
                                      vpn_key_url_column: str, vpn_key_id_column: str) -> str:

        if existing_vpn_key:
            # Возвращаем существующий ключ
            return f"<b>Твой ключ VPN:</b> <code>{existing_vpn_key}</code>"
        else:
            # Генерация нового ключа VPN
            new_vpn_key_data = self.vpn_manager.generate_vpn_key(server_choice)
            if new_vpn_key_data:
                new_vpn_key_url, new_vpn_key_id = new_vpn_key_data["access_url"], new_vpn_key_data["key_id"]
                async with aiosqlite.connect(self.db_path) as conn:
                    # Обновляем запись в базе данных с новым URL и ID ключа
                    await conn.execute(
                        f"UPDATE subscriptions SET {vpn_key_url_column} = ?, {vpn_key_id_column} = ? WHERE user_id = ?",
                        (new_vpn_key_url, new_vpn_key_id, user_id))
                    await conn.commit()
                return f"<b>Твой новый ключ VPN:</b> <code>{new_vpn_key_url}</code>"
            else:
                return "Не удалось создать ключ VPN."

    async def check_subscription_and_get_vpn_key(self, user_id: int, server_choice: str) -> str:
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT vpn_key_germ, vpn_key_amst, id_key_germ, id_key_amst, subscription_end FROM subscriptions WHERE user_id = ?",
                (user_id,)
            )
            subscription = await cursor.fetchone()

            if subscription:
                vpn_key_germ, vpn_key_amst, id_key_germ, id_key_amst, subscription_end = subscription
                subscription_end_date = datetime.strptime(subscription_end, "%Y-%m-%d %H:%M:%S")
                server_choice_column = 'vpn_key_germ' if server_choice == 'germany_server' else 'vpn_key_amst'
                vpn_key_id_column = 'id_key_germ' if server_choice == 'germany_server' else 'id_key_amst'
                existing_vpn_key = vpn_key_germ if server_choice == 'germany_server' else vpn_key_amst

                if datetime.now() < subscription_end_date:
                    return await self.handle_vpn_key_creation(user_id, server_choice, existing_vpn_key,
                                                              server_choice_column, vpn_key_id_column)
                else:
                    return (
                        "🔒 <b>Упс, кажется, у тебя нет активной подписки на VPN.</b>\n\n"
                        "Подключи подписку прямо сейчас, чтобы получить доступ к серверам по всему миру и наслаждаться безопасным интернет-сёрфингом без границ! 🌐✨\n\n"
                        "Подробнее о тарифах и подписке можешь узнать, отправив команду <code>/tariffs</code>."
                    )
            else:
                return (
                    "🔒 <b>Упс, кажется, у тебя нет активной подписки на VPN.</b>\n\n"
                    "Подключи подписку прямо сейчас, чтобы получить доступ к серверам по всему миру и наслаждаться безопасным интернет-сёрфингом без границ! 🌐✨\n\n"
                    "Подробнее о тарифах и подписке можешь узнать, отправив команду <code>/tariffs</code>."
                )

    async def get_subscription_info(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT subscription_end FROM subscriptions WHERE user_id = ? AND subscription_status = 1", (user_id,))
            row = await cursor.fetchone()
            if row:
                return {"subscription_end": row[0]}
            return None

    async def update_expired_subscriptions_and_delete_keys(self):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id, id_key_germ, id_key_amst FROM subscriptions WHERE subscription_end < CURRENT_DATE AND subscription_status = 1")
            expired_subscriptions = await cursor.fetchall()

            for sub in expired_subscriptions:
                user_id, id_key_germ, id_key_amst = sub
                # Удаление ключей VPN для каждой просроченной подписки
                if id_key_germ:
                    await self.vpn_manager.delete_vpn_key(id_key_germ, "germany_server")
                if id_key_amst:
                    await self.vpn_manager.delete_vpn_key(id_key_amst, "amsterdam_server")

            # Обновление статуса подписок после удаления ключей
            await db.execute(
                "UPDATE subscriptions SET subscription_status = 0, vpn_key_germ = NULL, vpn_key_amst = NULL, id_key_germ = NULL, id_key_amst = NULL WHERE subscription_end < CURRENT_DATE AND subscription_status = 1")
            await db.commit()