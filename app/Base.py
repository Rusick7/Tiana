import asyncio
import json
import html
import os

from aiogram.types import User, Chat


class Base:
    def __init__(self) -> None:
        os.makedirs("commands", exist_ok=True)
        self.commands_dict = {
            'мяу': '%u помяукал %t',
            'мяв': '%u мило мяукнул %t',
            'мрр': '%u помуррчал %t',
            'мурр': '%u помуррчал %t'
        }


    @staticmethod
    def save_dict(user_id: int, data: dict) -> None:
        with open(f"commands/user_{user_id}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


    @staticmethod
    def get_dict(user_id) -> dict:
        try:
            with open(f"commands/user_{user_id}.json", "r", encoding="utf-8") as f:
                return json.load(f)

        except FileNotFoundError:
            return {
                'мяу': '%u помяукал %t',
                'мяв': '%u мило мяукнул %t',
                'мрр': '%u помуррчал %t',
                'мурр': '%u помуррчал %t'
            }


    async def add_command(self, trigger: str, response: str, user_id: int) -> None:
        trigger_lower = trigger.strip().lower()
        if not trigger_lower:
            raise ValueError("Триггер не может быть пустым")
        self.commands_dict[trigger_lower] = response.strip()
        await asyncio.to_thread(self.save_dict, user_id, self.commands_dict)
        self.commands_dict = self.get_dict(user_id)


    async def list_commands(self, user_id: int) -> str:
        r = []
        for key, value in self.get_dict(user_id).items():
            r.append(f'{key}: {value}')
        return '\n'.join(r)


    async def remove_command(self, user_id: int, trigger: str) -> None:
        trigger_lower = trigger.strip().lower()

        if trigger_lower not in self.commands_dict:
            raise KeyError(f"Триггер '{trigger_lower}' не найден")

        del self.commands_dict[trigger_lower]

        await asyncio.to_thread(self.save_dict, user_id, self.commands_dict)
        self.commands_dict = self.get_dict(user_id)


    async def send(self, text:str|None, from_user_u:User|None,from_user_t:User|None, sender_chat:Chat|None) -> str:
        text:list = text.split('\n')
        remark = ''

        if text.__len__() > 1:
            remark = '\n'.join(text[1:])

        text:str = self.commands_dict[text[0].lower()]

        try:
            u = str(self.ut(from_user_u, sender_chat))
            t = str(self.ut(from_user_t, sender_chat))
            r = str(text.replace('%u', u).replace('%t', t))
            if remark.__len__() > 0:
                r += f'\nС репликой: {remark}'
            return r

        except:
            print(f'error_send')
            return str(text)


    @staticmethod
    def ut(from_user, sender_chat: Chat | None) -> str:
        if from_user:
            return f'<a href="tg://user?id={from_user.id}">{html.escape(str(from_user.first_name))}</a>'
        elif sender_chat.username:
            return f'<a href="tg://resolve?domain={sender_chat.username}">{html.escape(str(sender_chat.title))}</a>'
        else:
            return from_user.first_name