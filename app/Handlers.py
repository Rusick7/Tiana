from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import Message, ChatMemberUpdated

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
    pass

# add new command
@router.message(F.text.startswith('.спрп'))
async def add_public_command(message: Message):
    pass


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
async def rp_command(message: Message):
    if message.from_user:
        try:
            if message.reply_to_message and message.reply_to_message.from_user and not message.reply_to_message.sender_chat:
                text = await AsyncORM.get_response( trigger_str=message.text, user_id=message.from_user.id,
                                                    username=message.from_user.username,
                                                    target_username=message.reply_to_message.from_user.username,
                                                    target_user_id=message.reply_to_message.from_user.id,
                                                    chat_id=message.chat.id)

            elif '@' in message.text and message.entities:
                chat_id = None

                if message.chat.type == ChatType.PRIVATE:
                    chat_id = message.chat.id

                for entity in message.entities:
                    # if entity.type == "mention":
                    print(entity.user)

                target_username = message.text.split('@')[1].split(' ')[0]
                trigger_str = message.text.split('@')[0].split(' ')[0]

                text = await AsyncORM.get_response(trigger_str=trigger_str, chat_id=chat_id,
                                                   username=message.from_user.username,
                                                   target_username=target_username)


            else:
                print(message.text)
                return

            if text:
                await message.reply(text=text[0], parse_mode='HTML')
                print(text[0])
                print(text[1])

        except Exception as e:
            print(e)



@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(f'/start - перезапуск'
                         f'\n.урп - удаление команды'
                         f'\n.срп - создание команды'
                         f'\n.лрп - список команд')