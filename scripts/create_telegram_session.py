import asyncio
import os

from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():
    api_id_str = os.environ.get("TELEGRAM_API_ID") or input("TELEGRAM_API_ID: ").strip()
    api_hash = os.environ.get("TELEGRAM_API_HASH") or input("TELEGRAM_API_HASH: ").strip()
    api_id = int(api_id_str)

    client = TelegramClient(StringSession(""), api_id, api_hash)
    await client.start()
    session_string = client.session.save()
    await client.disconnect()

    print(session_string)


if __name__ == "__main__":
    asyncio.run(main())
