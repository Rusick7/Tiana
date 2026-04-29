import asyncio
from os import getenv
from aiogram import Bot, Dispatcher
from app.Handlers import router


async def main():
    # await async_main()
    TOKEN = getenv('BOT_TOKEN')
    if not TOKEN:
        return
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    print('start')
    await dp.start_polling(bot, handle_as_tasks=False)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot closed')