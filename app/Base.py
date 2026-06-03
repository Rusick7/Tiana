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

    def __init__(self) -> None:
        os.makedirs("configurations", exist_ok=True)
        self.user_state = UserState(
            new_output=Base.DEFAULT_NEW_OUTPUT,
            commands_dict=Base.DEFAULT_COMMANDS.copy())


    @staticmethod
    async def get_user_conf(user_id: int) -> UserState:
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


    @staticmethod
    async def save_dict(user_id: int, data: UserState) -> None:
        async with aiofiles.open(f"configurations/user_{user_id}.json", "w", encoding="utf-8") as f:
            await f.write(json.dumps(asdict(data), ensure_ascii=False, indent=4))


    async def get_commands(self, user_id: int) -> dict:
        self.user_state = await self.get_user_conf(user_id)
        return self.user_state.commands_dict


    async def add_command(self, trigger: str, response: str, user_id: int) -> None:
        self.user_state = await self.get_user_conf(user_id)

        trigger_lower = trigger.strip().lower()
        if not trigger_lower:
            raise ValueError("Триггер не может быть пустым")

        if '|' not in response:
            response = Base.DEFAULT_STICKER + ' | ' + response

        self.user_state.commands_dict[trigger_lower] = response.strip()
        await self.save_dict(user_id, self.user_state)


    async def list_commands(self, user_id: int) -> str:
        commands_dict = await self.get_commands(user_id)

        commands = []
        for key, value in commands_dict.items():
            if self.user_state.new_output:
                commands.append(f"{key}: {' '.join(value.split(sep=' ')[2:])}")
            else:
                commands.append(f"{key}: {value}")

        return '\n'.join(commands)


    async def remove_command(self, user_id: int, trigger: str) -> None:
        self.user_state = await self.get_user_conf(user_id)

        trigger_lower = trigger.strip().lower()
        if trigger_lower not in self.user_state.commands_dict:
            raise KeyError(f"Триггер '{trigger_lower}' не найден")

        del self.user_state.commands_dict[trigger_lower]

        await self.save_dict(user_id, self.user_state)


    async def send(self, text:str|None, from_user_u:User, from_user_t:User) -> str:
        # ---------------- получение -------------------
        try:
            parts: list[str] = text.split('\n') # команда + реплика
            remark = '\n'.join(parts[1:]) if len(parts) > 1 else '' # только реплика

            if len(parts) < 2:
                parts: list = text.split(' ')
                remark = ' '.join(parts[1:]) if len(parts) > 1 else ''

            template: str = await AsyncORM.send_response(parts[0].lower()) # ❤ | %u text %t
            # template: str = (await self.get_commands(from_user_u.id))[parts[0].lower()] # ❤ | %u text %t

        except Exception as e:
            print(f'Exception_send {e}')
            raise ValueError(f'Ошибка при получении данных: {e}')

        # ---------------- преобразование -------------------
        try:
            if self.user_state.new_output and ' | ' in template:
                template = ' '.join(template.split(sep=' ')[2:])  # %u text %t

            u: str = self.ut(from_user_u)
            t: str = self.ut(from_user_t)
            reply: str = template.replace('%u', u).replace('%t', t) #  {from} text {to}

            if len(remark) > 0 and self.user_state.new_output:
                reply += f'\nС репликой: « {remark} »' # {r} \n С репликой: « {remark} »

            elif len(remark) > 0:
                reply += f'\n{Base.DEFAULT_REPL} С репликой: « {remark} »' # {r} \n 💬 С репликой: « {remark} »

            return reply

        except Exception as e:
            print(f'send_error: {e}')
            raise e


    @staticmethod
    def ut(from_user: User) -> str:
        if from_user:
            return f'<a href="tg://user?id={from_user.id}">{html.escape(from_user.first_name)}</a>'
        # elif sender_chat:  # ссылка на группу через @username
        #     return f'<a href="tg://resolve?domain={sender_chat.username}">{html.escape(str(sender_chat.title))}</a>'
        else:
            return from_user.first_name