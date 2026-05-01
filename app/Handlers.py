from aiogram import Router, F

from aiogram.types import Message
from aiogram.filters import Command

from app.Base import Base

router = Router()
base = Base()


@router.message(Command('start'))
async def command_start(message: Message):
    await message.answer(f"Hello, {message.from_user.full_name}!",)
    print(f"message = {message}")


@router.message(F.reply_to_message, F.text)
async def text(message: Message):
    if message.text.split('\n')[0].lower() in base.get_dict(message.from_user.id).keys():
        try:
            await message.bot.send_message(
                chat_id = message.chat.id,
                reply_to_message_id = message.reply_to_message.message_id,
                text = await base.send(
                    message.text,
                    message.from_user,
                    message.reply_to_message.from_user,
                    message.sender_chat),
                parse_mode='HTML'
            )
        except Exception as e:
            print(e)


@router.message(F.text.startswith('.срп'))
async def add_new_trigger(message: Message):
    lines = message.text.split('\n')
    if len(lines) < 3:
        await message.reply(
            "Неверный формат. Используйте:\n" +
            ".срп\n" +
            "<команда>\n" +
            "<шаблон ответа с %u и %t>"
        )
        return

    trigger = lines[1].strip()
    response = lines[2].strip()

    if not trigger or not response:
        await message.reply("Команда или шаблон не должны быть пустыми")
        return

    try:
        await base.add_command(trigger, response, message.from_user.id)
        await message.reply(f"Команда {trigger} добавлен")
    except Exception as e:
        print(e)
        await message.reply(f"Ошибка при сохранении")


@router.message(F.text == '.лрп')
async def list_triggers(message: Message):
    try:
        await message.reply(await base.list_commands(message.from_user.id))
    except Exception as e:
        print(e)
        await message.reply(f"Ошибка при получении")


@router.message(F.text.startswith('.урп'))
async def remove_trigger(message: Message):
    lines = message.text.split('\n')
    if len(lines) < 2:
        await message.reply(
            "Неверный формат. Используйте:\n" +
            ".урп\n" +
            "<команда>"
        )
        return

    trigger = lines[1].strip()
    if not trigger:
        await message.reply("Команда не указана")
        return

    try:
        await base.remove_command(message.from_user.id, trigger)
        await message.reply(f"Команда {trigger} удалён")

    except KeyError:
        await message.reply(f"Команда не найден. Список команд\n{list_triggers}")

    except Exception as e:
        print(e)
        await message.reply("Ошибка при удалении")



@router.message(Command('help'))
async def Help(message: Message):
    await message.answer(f'/start - перезапуск'
                         f'\n.урп - удаление команды'
                         f'\n.срп - создание команды'
                         f'\n.лрп - список команд')