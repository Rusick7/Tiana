import asyncio

from aiofiles import os
from aiogram import Bot, Dispatcher

from app.Database.Settings import settings
from app.Handlers import router


async def main():
    if not await os.path.exists('app/Database/data'):
        await os.makedirs('app/Database/data')

    if not await os.path.exists('configurations'):
        await os.makedirs('configurations')

    if not settings.TOKEN:
        raise Exception('BOT_TOKEN environment variable not found')

    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher()

    dp.include_router(router)
    print('start')

    await dp.start_polling(bot, handle_as_tasks=False)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot closed')
    except Exception as err:
        print(err)