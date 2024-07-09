import asyncio
from outline_vpn.outline_vpn import OutlineVPN, OutlineServerErrorException
from bot.config import GERMANY_API_URL, GERMANY_CERT_SHA256, AMSTERDAM_API_URL, AMSTERDAM_CERT_SHA256

class VPNManager:
    def __init__(self):
        self.germany_vpn = OutlineVPN(api_url=GERMANY_API_URL, cert_sha256=GERMANY_CERT_SHA256)
        self.amsterdam_vpn = OutlineVPN(api_url=AMSTERDAM_API_URL, cert_sha256=AMSTERDAM_CERT_SHA256)

    def generate_vpn_key(self, server_choice: str, data_limit: int = None) -> str:
        if server_choice == "germany_server":
            vpn = self.germany_vpn
            name = "Germany"
        elif server_choice == "amsterdam_server":
            vpn = self.amsterdam_vpn
            name = "Amsterdam"
        else:
            raise ValueError("Invalid server choice")

        try:
            new_key = vpn.create_key(name=name, data_limit=data_limit)
            # Возвращаем словарь с URL и ID ключа
            return {"access_url": new_key.access_url, "key_id": new_key.key_id}
        except OutlineServerErrorException as e:
            print(f"Failed to generate VPN key: {e}")
            return None

    async def delete_vpn_key(self, key_id: str, server_choice: str):
            vpn = self.germany_vpn if server_choice == "germany_server" else self.amsterdam_vpn
            loop = asyncio.get_event_loop()
            # Асинхронно выполняем синхронный метод удаления ключа
            await loop.run_in_executor(None, lambda: vpn.delete_key(key_id))
