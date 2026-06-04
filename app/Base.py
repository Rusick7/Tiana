import html
import json
import os
from dataclasses import dataclass, asdict

import aiofiles
from aiogram.types import User, Chat

from Database.Orm.AsyncOrm import AsyncORM


@dataclass
class UserState:
    commands_dict: dict
    new_output: bool = False


class Base:
    DEFAULT_STICKER = '❤'
    DEFAULT_REPL = '💬'
    DEFAULT_NEW_OUTPUT = True
    DEFAULT_new_input_command = True
    DEFAULT_COMMANDS = {
        'мяу': DEFAULT_STICKER+' | %u помяукал %t',
        'мяв': DEFAULT_STICKER+' | %u мило мяукнул %t',
        'мрр': DEFAULT_STICKER+' | %u помуррчал %t',
        'мурр': DEFAULT_STICKER+' | %u помуррчал %t'
    }

    @classmethod
    def __init__(cls) -> None:
        os.makedirs("configurations", exist_ok=True)
        cls.user_state = UserState(
            new_output=Base.DEFAULT_NEW_OUTPUT,
            commands_dict=Base.DEFAULT_COMMANDS.copy())


    @classmethod
    async def get_user_conf(cls, user_id: int) -> UserState:
        try:
            async with aiofiles.open(f"configurations/user_{user_id}.json", "r", encoding="utf-8") as f:
                data = json.loads(await f.read())
                return UserState(
                    commands_dict=data['commands_dict'],
                    new_output=data['new_output'])

        except FileNotFoundError:
            return UserState(
                new_output=Base.DEFAULT_NEW_OUTPUT,
                commands_dict=Base.DEFAULT_COMMANDS.copy())


    @classmethod
    async def save_dict(cls, user_id: int, data: UserState) -> None:
        async with aiofiles.open(f"configurations/user_{user_id}.json", "w", encoding="utf-8") as f:
            await f.write(json.dumps(asdict(data), ensure_ascii=False, indent=4))


    @classmethod
    async def get_commands(cls, user_id: int) -> dict:
        cls.user_state = await cls.get_user_conf(user_id)
        return cls.user_state.commands_dict


    @classmethod
    async def add_command(cls, trigger: str, response: str, user_id: int) -> None:
        cls.user_state = await cls.get_user_conf(user_id)

        trigger_lower = trigger.strip().lower()
        if not trigger_lower:
            raise ValueError("Триггер не может быть пустым")

        if '|' not in response:
            response = Base.DEFAULT_STICKER + ' | ' + response

        cls.user_state.commands_dict[trigger_lower] = response.strip()
        await cls.save_dict(user_id, cls.user_state)


    @classmethod
    async def list_commands(cls, user_id: int) -> str:
        commands_dict = await cls.get_commands(user_id)

        commands = []
        for key, value in commands_dict.items():
            if cls.user_state.new_output:
                commands.append(f"{key}: {' '.join(value.split(sep=' ')[2:])}")
            else:
                commands.append(f"{key}: {value}")

        return '\n'.join(commands)


    @classmethod
    async def remove_command(cls, user_id: int, trigger: str) -> None:
        cls.user_state = await cls.get_user_conf(user_id)

        trigger_lower = trigger.strip().lower()
        if trigger_lower not in cls.user_state.commands_dict:
            raise KeyError(f"Триггер '{trigger_lower}' не найден")

        del cls.user_state.commands_dict[trigger_lower]

        await cls.save_dict(user_id, cls.user_state)


    @classmethod
    async def send_reply(cls, text:str, from_user_u:User, from_user_t:User) -> str|None:
        # ---------------- получение -------------------
        try:
            parts: list[str] = text.split('\n') # команда + реплика
            remark = '\n'.join(parts[1:]) if len(parts) > 1 else '' # только реплика

            if len(parts) < 2:
                parts: list = text.split(' ')
                remark = ' '.join(parts[1:]) if len(parts) > 1 else ''

            template: str = (await AsyncORM.send_response(parts[0].lower()))[0] # ❤ | %u text %t
            if not template:
                raise ValueError(f'Нет команды')
            # template: str = (await cls.get_commands(from_user_u.id))[parts[0].lower()] # ❤ | %u text %t

        except Exception as e:
            print(f'Exception_send {e}')
            raise ValueError(f'Ошибка при получении данных: {e}')

        # ---------------- преобразование -------------------
        try:
            reply:str = cls.comp(template, from_user_u, from_user_t) # {from} text {to}

            if len(remark) > 0 and cls.user_state.new_output:
                reply += f'\nС репликой: « {remark} »' # {r} \n С репликой: « {remark} »

            elif len(remark) > 0:
                reply += f'\n{Base.DEFAULT_REPL} С репликой: « {remark} »' # {r} \n 💬 С репликой: « {remark} »

            return reply

        except Exception as e:
            print(f'send_error: {e}')
            raise e


    @classmethod
    def ut(cls, from_user: User) -> str:
        if from_user:
            return f'<a href="tg://user?id={from_user.id}">{html.escape(from_user.first_name)}</a>'
        # elif sender_chat:  # ссылка на группу через @username
        #     return f'<a href="tg://resolve?domain={sender_chat.username}">{html.escape(str(sender_chat.title))}</a>'
        else:
            return from_user.first_name


    @classmethod
    def comp(cls, response, from_user_u, from_user_t) -> str:
        if cls.user_state.new_output and ' | ' in response:
            response = ' '.join(response.split(sep=' ')[2:])  # %u text %t

        u: str = cls.ut(from_user_u)
        t: str = cls.ut(from_user_t)
        return response.replace('%u', u).replace('%t', t) # {from} text {to}


    @classmethod
    async def send(cls, text:str, from_user_id: int = None, chat_id: int = None):
        parts = [part.strip() for part in text.strip().split('\n')] # Убираем лишние пробелы и делим текст на строки

        if len(parts) < 2: # если команда в 1 строку
            parts = [part.strip() for part in text.strip().split(' ')]

        command, args = parts[0], parts[1:]

        res: tuple|None = await AsyncORM.send_response(
            trigger_str=command.lower(),
            user_id=from_user_id,
            chat_id=chat_id,
            *args
        )

        if not res:
            return None
        response, func_res = res

        # template: str = (await cls.get_commands(from_user_u.id))[parts[0].lower()] # ❤ | %u text %t



        if cls.user_state.new_output and ' | ' in template:
            template = ' '.join(template.split(sep=' ')[2:])  # %u text %t

        u: str = cls.ut(from_user_u)
        t: str = cls.ut(from_user_t)
        reply: str = template.replace('%u', u).replace('%t', t) #  {from} text {to}

        if len(remark) > 0 and cls.user_state.new_output:
            reply += f'\nС репликой: « {remark} »' # {r} \n С репликой: « {remark} »

        elif len(remark) > 0:
            reply += f'\n{Base.DEFAULT_REPL} С репликой: « {remark} »' # {r} \n 💬 С репликой: « {remark} »

        return reply

