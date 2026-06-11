from datetime import datetime, timezone, timedelta

from aiogram import Router, F, Bot
from aiogram.enums import ChatType
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import Message, ChatMemberUpdated, ChatPermissions

# from app.Base import Base
from Database.Orm.AsyncOrm import AsyncORM

router = Router()
# base = Base()



# =================================================
# MAIN FUNCTIONS
# =================================================

# add User and Chat to Database
@router.message(Command('start'))
async def cmd_start(message: Message):
    if message.from_user:
        await message.answer(f"Hello, {message.from_user.full_name}!",)
        await AsyncORM.add_user(message.from_user.id, message.from_user.full_name)
        if message.chat.type != ChatType.PRIVATE:
            await AsyncORM.add_chat(message.chat.id, message.chat.title)

# join in group
@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated):
    user_name = event.new_chat_member.user.first_name # Получаем имя пользователя
    chat_name = event.chat.title

    # Отправляем приветствие в чат
    await event.answer(f"Привет, {user_name}! Добро пожаловать в чат {chat_name}!")
    iau = await AsyncORM.add_user(event.new_chat_member.user.id, event.new_chat_member.user.full_name)
    iac = await AsyncORM.add_chat(event.chat.id, event.chat.title)
    if iau or iac:
        print(f"\033[34m| {event.new_chat_member.user.id} | {event.new_chat_member.user.full_name} |"
              f"| {event.chat.id} | {event.chat.title} |\033[0m")

# add new command
@router.message(F.text.startswith('.срп'))
async def add_command(message: Message):
    await AsyncORM.add_command(message.chat.id, message.from_user.id, )

# add new command
@router.message(F.text.startswith('.спрп'))
async def add_public_command(message: Message):
    pass


@router.message(F.text.startswith('.мут'))
async def mute_user(message: Message, bot: Bot):
    # Получаем ID чата и ID нарушителя
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id

    check_res = await checker(message)

    # Указываем время, до которого будет действовать мут (например, на 10 минут)
    until_date = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Устанавливаем запрещающие права (передаем False)
    permissions = ChatPermissions(
        can_send_messages=False,
        can_send_audios=False,
        can_send_documents=False,
        can_send_photos=False,
        can_send_videos=False,
        can_send_video_notes=False,
        can_send_voice_notes=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False
    )

    try:
        # Применяем ограничения в Telegram
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=permissions,
            until_date=until_date
        )

        await message.reply(
            f"Пользователь {message.reply_to_message.from_user.full_name} замучен на 10 минут."
        )

    except Exception as e:
        await message.reply(f"Не удалось ограничить пользователя. Ошибка: {e}")

@router.message(Command("unmute"))
async def unmute_user(message: Message, bot: Bot):
    if not message.reply_to_message:
        await message.reply("Ответьте на сообщение пользователя, которого хотите размутить.")
        return

    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id

    # Разрешаем отправку сообщений (передаем True)
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_audios=True,
        can_send_documents=True,
        can_send_photos=True,
        can_send_videos=True,
        can_send_video_notes=True,
        can_send_voice_notes=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )

    try:
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=permissions
        )
        await message.reply(f"С пользователя {message.reply_to_message.from_user.full_name} сняты ограничения.")
    except Exception as e:
        await message.reply(f"Ошибка при снятии ограничений: {e}")



# # add new command
# @router.message(F.text.startswith('.срп'))
# async def add_new_trigger(message: Message) -> None:
#     dop=0
#     if '|' in message.text:
#         dop = 1
#
#     lines = message.text.split('\n')
#     if len(lines) < 3 + dop:
#         lines = message.text.split(' ')
#         if len(lines) < 3 + dop and dop!=1:
#             await message.reply(
#                 "Неверный формат. Используйте:\n" +
#                 ".срп\n<команда>\n<шаблон ответа с %u и %t>"
#             )
#             return
#         elif len(lines) < 3 + dop and dop==1:
#             await message.reply(
#                 "Неверный формат. Используйте:\n" +
#                 ".срп\n<стикер>\n<команда>\n<шаблон ответа с %u и %t>"
#             )
#             return
#
#     if dop==1:
#         trigger = lines[2].strip()
#         response = lines[1] + ' | ' + '\n'.join(lines[3:]).strip()
#     else:
#         trigger = lines[1].strip()
#         response = ' '.join(lines[2:]).strip()
#
#     if not trigger or not response:
#         await message.reply("Команда или шаблон не должны быть пустыми")
#         return
#
#     try:
#         redact = False
#         if trigger in (await AsyncORM.get_commands(message.from_user.id)).keys():
#             redact = True
#
#         await base.add_command(trigger, response, message.from_user.id)
#
#         if redact:
#             await message.reply(f"Команда {trigger} изменен")
#         else:
#             await message.reply(f"Команда {trigger} добавлен")
#     except Exception as e:
#         print(e)
#         await message.reply(f"Ошибка при сохранении")


# @router.message(F.text == '.лрп')
# async def list_triggers(message: Message):
#     try:
#         await message.reply(await base.list_commands(message.from_user.id))
#     except Exception as e:
#         print(e)
#         await message.reply(f"Ошибка при получении")


# @router.message(F.text.startswith('.урп'))
# async def remove_trigger(message: Message):
#     lines = message.text.split(' ')
#     if len(lines) < 2:
#         lines = message.text.split('\n')
#         if len(lines) < 2:
#             await message.reply(
#                 "Неверный формат. Используйте:\n" +
#                 ".урп <команда>"
#             )
#             return
#
#     trigger = ' '.join(lines[1:]).strip()
#     if not trigger:
#         await message.reply("Команда не указана")
#         return
#
#     try:
#         await base.remove_command(message.from_user.id, trigger)
#         await message.reply(f"Команда {trigger} удалён")
#
#     except KeyError:
#         await message.reply(f"Команда не найден. Список команд\n{list_triggers}")
#
#     except Exception as e:
#         print(e)
#         await message.reply("Ошибка при удалении")



# =================================================
# COMMANDS
# =================================================

@router.message(F.text)
async def text_from_user(message: Message):
    try:
        if not message.from_user:
            return

        check_res = await checker(message)
        if not check_res:
            return

        if check_res['cid']:
            saved_mess = await AsyncORM.save_message(message.chat.id, message.from_user.id, message.text)
            if not saved_mess:
                print(f"\033[34m| {message.chat.id} | {message.from_user.id} | {message.text} |\033[0m")

        user_id, username, target_user_id, target_username, chat_id, args = check_res
        if not (user_id or username) and (target_user_id or target_username):
            return

        response_data = await AsyncORM.get_response(trigger_str=message.text, chat_id=chat_id, user_id=user_id,
                                                    username=username, target_user_id=target_user_id,
                                                    target_username=target_username, *args)

        if not response_data and response_data[0]:
            return

        await message.reply(text=response_data[0], parse_mode='HTML')
        print(response_data[0])
        print(response_data[1])

    except Exception as e:
        print(e)



@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(f'/start - перезапуск'
                         f'\n.урп - удаление команды'
                         f'\n.срп - создание команды'
                         f'\n.лрп - список команд')


async def checker(message: Message) -> dict|None:
    text = message.text or ""
    res:dict[str, str|int|list|None] = {
        'uid': None, 'uname': None,
        't_uid': None, 't_uname': None,
        'cid': None, 'trigger_str': None, 'args': []
    }

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        res['cid'] = message.chat.id

    if message.from_user:
        res['uid'] = message.from_user.id
        res['uname'] = message.from_user.username

    if '@' in text:
        parts = text.split('@', 1)
        left_words = parts[0].strip().split()
        right_words = parts[1].strip().split()

        if left_words:
            res['trigger_str'] = left_words[0]
        if right_words:
            res['t_uname'] = right_words[0]
            res['args'] = right_words[1:]
    else:
        words = text.split()
        if words:
            res['trigger_str'] = words[0]
            res['args'] = words[1:]

    # Если это ответ на сообщение, приоритетно берем таргет оттуда
    if message.reply_to_message and message.reply_to_message.from_user and not message.reply_to_message.sender_chat:
        res['t_uid'] = message.reply_to_message.from_user.id
        res['t_uname'] = message.reply_to_message.from_user.username

    return res


@router.message(F.text)
async def text_from_user(message: Message):
    try:
        check_res = await checker(message)
        if not message.from_user and not check_res:
            return

        # Логируем / сохраняем сообщение в БД
        if check_res['cid']:
            saved_mess = await AsyncORM.save_message(message.chat.id, message.from_user.id, message.text)
            if not saved_mess:
                print(f"\033[34m| {message.chat.id} | {message.from_user.id} | {message.text} |\033[0m")

        if not (check_res['uid'] or check_res['uname']) and not (check_res['t_uid'] or check_res['t_uname']):
            return

        # Запрос к БД (передаем аргументы из словаря по ключам)
        response_data = await AsyncORM.get_response(
            trigger_str=check_res['trigger_str'],
            chat_id=check_res['cid'],
            user_id=check_res['uid'],
            username=check_res['uname'],
            target_user_id=check_res['t_uid'],
            target_username=check_res['t_uname'],
            args=check_res['args']  # Передаем как именованный аргумент-список
        )

        # Проверяем, что ответ от БД получен и он не пустой
        if response_data and response_data[0]:
            await message.reply(text=response_data[0], parse_mode='HTML')
            if len(response_data) > 1:
                print(response_data[1])

    except Exception as e:
        print(f"Ошибка в хендлере: {e}")