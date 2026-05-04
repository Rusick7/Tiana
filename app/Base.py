import json
import html
import os

from aiogram.types import User, Chat


class Base:
    DEFAULT_STICKER = '❤'
    DEFAULT_REPL = '💬'
    DEFAULT_NEW_OUTPUT = True
    DEFAULT_NEW_INPUT = True
    DEFAULT_COMMANDS = {
        'мяу': DEFAULT_STICKER+' | %u помяукал %t',
        'мяв': DEFAULT_STICKER+' | %u мило мяукнул %t',
        'мрр': DEFAULT_STICKER+' | %u помуррчал %t',
        'мурр': DEFAULT_STICKER+' | %u помуррчал %t'
    }

    def __init__(self) -> None:
        os.makedirs("commands", exist_ok=True)
        self.new_output: bool = Base.DEFAULT_NEW_OUTPUT
        self.commands_dict: dict = Base.DEFAULT_COMMANDS
        self.new_input: bool = Base.DEFAULT_NEW_INPUT


    @staticmethod
    def get_dict(user_id: int) -> tuple[bool, bool, dict]:
        try:
            with open(f"configurations/user_{user_id}.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data['new_input'], data['new_output'], data['commands']

        except FileNotFoundError:
            return Base.DEFAULT_NEW_INPUT, Base.DEFAULT_NEW_OUTPUT, Base.DEFAULT_COMMANDS


    @staticmethod
    async def save_dict(user_id: int, data: dict) -> None:
        with open(f"commands/user_{user_id}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


    def get_commands(self, user_id: int) -> dict:
        return self.get_dict(user_id)[2]


    async def add_command(self, trigger: str, text: str, user_id: int) -> None:
        self.new_input, self.new_output, self.commands_dict = self.get_dict(user_id)

        trigger_lower = trigger.strip().lower()
        if not trigger_lower:
            raise ValueError("Триггер не может быть пустым")

        self.commands_dict[trigger_lower] = text.strip()
        await self.save_dict(user_id, {
            'new_input': self.new_input,
            'new_output': self.new_output,
            'commands': self.commands_dict
        })


    async def list_commands(self, user_id: int) -> str:
        self.new_input, self.new_output, self.commands_dict = self.get_dict(user_id)

        commands = []
        for key, value in self.commands_dict.items():
            commands.append(f'{key}: {value}')

        return '\n'.join(commands)


    async def remove_command(self, user_id: int, trigger: str) -> None:
        self.new_input, self.new_output, self.commands_dict = self.get_dict(user_id)

        trigger_lower = trigger.strip().lower()
        if trigger_lower not in self.commands_dict:
            raise KeyError(f"Триггер '{trigger_lower}' не найден")

        del self.commands_dict[trigger_lower]

        await self.save_dict(user_id, self.commands_dict)


    async def send(self, text:str, from_user_u:User,from_user_t:User, sender_chat:Chat|None) -> str:
        self.new_input, self.new_output, self.commands_dict = self.get_dict(from_user_u.id)

        if self.new_input:
            text:list = text.split(' ')
            remark = ' '.join(text[1:]) if text.__len__() > 1 else ''
        else:
            text:list = text.split('\n')
            remark = '\n'.join(text[1:]) if text.__len__() > 1 else ''

        text:str = self.commands_dict[text[0].lower()]

        try:
            u = str(self.ut(from_user_u, sender_chat))
            t = str(self.ut(from_user_t, sender_chat))
            r = str(text.replace('%u', u).replace('%t', t))

            if self.new_output:
                r = r[3:]

            if remark.__len__() > 0:
                r += f'\nС репликой: « {remark} »'

            elif remark.__len__() > 0 and self.new_output:
                r += f'\n{Base.DEFAULT_REPL} С репликой: « {remark} »'

            return r

        except Exception as e:
            print(f'error_send {e}')
            return str(text)


    @staticmethod
    def ut(from_user, sender_chat: Chat | None) -> str:
        if from_user:
            return f'<a href="tg://user?id={from_user.id}">{html.escape(from_user.first_name)}</a>'
        elif sender_chat:
            return f'<a href="tg://resolve?domain={sender_chat.username}">{html.escape(str(sender_chat.title))}</a>'
        else:
            return from_user.first_name