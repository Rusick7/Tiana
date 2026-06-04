from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

from app.Base import Base
from Database.Orm.AsyncOrm import AsyncORM

router = Router()
base = Base()


@router.message(Command('start'))
async def cmd_start(message: Message):
    if message.from_user:
        await message.answer(f"Hello, {message.from_user.full_name}!",)
        await AsyncORM.add_user(message.from_user.id, message.from_user.full_name)
        if message.chat.type != ChatType.PRIVATE:
            await AsyncORM.add_chat(message.chat.id, message.chat.title)

@router.message(F.reply_to_message, F.text)
async def rp_command(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user and message.from_user and message.text and not message.reply_to_message.sender_chat:
        try:
            text = await base.send_reply(
                message.text,
                message.from_user,
                message.reply_to_message.from_user),

            if not text: return
            text:str

            await message.bot.send_message(
                chat_id = message.chat.id,
                reply_to_message_id = message.reply_to_message.message_id,
                text=text,
                parse_mode='HTML'
            )
        except Exception as e:
            print(e)

@router.message(not F.reply_to_message, F.text)
async def rp_command(message: Message):
    if message.from_user and message.text:
        try:
            await message.bot.send_message(
                chat_id = message.chat.id,
                reply_to_message_id = message.message_id,
                text = await base.send(
                    text= message.text,
                    from_user_id=message.from_user.id,
                    chat_id=message.chat.id
                )
            )
        except Exception as e:
            print(e)


@router.message(F.text.startswith('.срп'))
async def add_new_trigger(message: Message) -> None:
    dop=0
    if '|' in message.text:
        dop = 1

    lines = message.text.split('\n')
    if len(lines) < 3 + dop:
        lines = message.text.split(' ')
        if len(lines) < 3 + dop and dop!=1:
            await message.reply(
                "Неверный формат. Используйте:\n" +
                ".срп\n<команда>\n<шаблон ответа с %u и %t>"
            )
            return
        elif len(lines) < 3 + dop and dop==1:
            await message.reply(
                "Неверный формат. Используйте:\n" +
                ".срп\n<стикер>\n<команда>\n<шаблон ответа с %u и %t>"
            )
            return

    if dop==1:
        trigger = lines[2].strip()
        response = lines[1] + ' | ' + '\n'.join(lines[3:]).strip()
    else:
        trigger = lines[1].strip()
        response = ' '.join(lines[2:]).strip()

    if not trigger or not response:
        await message.reply("Команда или шаблон не должны быть пустыми")
        return

    try:
        redact = False
        if trigger in (await base.get_commands(message.from_user.id)).keys():
            redact = True

        await base.add_command(trigger, response, message.from_user.id)

        if redact:
            await message.reply(f"Команда {trigger} изменен")
        else:
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
    lines = message.text.split(' ')
    if len(lines) < 2:
        lines = message.text.split('\n')
        if len(lines) < 2:
            await message.reply(
                "Неверный формат. Используйте:\n" +
                ".урп <команда>"
            )
            return

    trigger = ' '.join(lines[1:]).strip()
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
async def cmd_help(message: Message):
    await message.answer(f'/start - перезапуск'
                         f'\n.урп - удаление команды'
                         f'\n.срп - создание команды'
                         f'\n.лрп - список команд')