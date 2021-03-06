import discord
import difflib
import InsightExc


class DiscordCommands(object):
    def __init__(self):
        self.commands = {}
        self.commands_prefixed = {}
        self.all_commands = []
        self.prefix = ['!', '?']
        self.make_commands()

    def make_commands(self):
        self.commands['about'] = ['about', 'info']
        self.commands['help'] = ['help', 'commands']
        self.commands['create'] = ['create', 'new']
        self.commands['settings'] = ['settings', 'modify', 'options', 'config']
        self.commands['sync'] = ['sync', 'ignorelists', 'list', 'blacklist']
        self.commands['start'] = ['start', 'resume']
        self.commands['stop'] = ['stop', 'pause']
        self.commands['remove'] = ['remove', 'delete']
        self.commands['status'] = ['status']
        self.commands['8ball'] = ['ball', '8ball', 'magic', '8']
        self.commands['dscan'] = ['dscan', 'localscan', 'shipscan', 'scan']
        self.commands['lock'] = ['lock']
        self.commands['unlock'] = ['unlock']
        self.commands['quit'] = ['quit']
        self.commands['admin'] = ['admin']

        for k, v in self.commands.items():
            new_vals = []
            for p in self.prefix:
                for c in v:
                    command = '{}{}'.format(p, c)
                    new_vals.append(command)
                    self.all_commands.append(command)
            self.commands_prefixed[k] = new_vals

    def __lookup(self, message_txt: str, command_list):
        return any((message_txt.lower()).startswith(i.lower()) for i in command_list)

    def __similar(self, message_txt):
        return difflib.get_close_matches(message_txt.lower(), self.all_commands)

    async def about(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('about'))

    async def help(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('help'))

    async def create(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('create'))

    async def settings(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('settings'))

    async def sync(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('sync'))

    async def start(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('start'))

    async def stop(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('stop'))

    async def remove(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('remove'))

    async def status(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('status'))

    async def eightball(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('8ball'))

    async def dscan(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('dscan'))

    async def lock(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('lock'))

    async def unlock(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('unlock'))

    async def quit(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('quit'))

    async def admin(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.commands_prefixed.get('admin'))

    async def is_command(self, message_object: discord.Message):
        return self.__lookup(message_object.content, self.prefix)

    async def notfound(self, message_object: discord.Message):
        for pref in self.prefix:
            if message_object.content == pref:
                return
        similar_commands = self.__similar(message_object.content)
        resp_text = "The command '{}' was not found.\n\n".format(str(message_object.content))
        if len(similar_commands) == 0:
            resp_text += "No similar commands could be found matching what you entered.\n\n"
        else:
            resp_text += "Did you mean?\n\n"
            for c in similar_commands:
                resp_text += "'{}'\n".format(str(c))
        resp_text += "\nRun the '!help' command to see a list of available commands."
        if len(resp_text) >= 750:
            raise InsightExc.userInput.CommandNotFound
        else:
            raise InsightExc.userInput.CommandNotFound(str(resp_text))
