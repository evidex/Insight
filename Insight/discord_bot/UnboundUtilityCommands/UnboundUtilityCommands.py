from . import Dscan, EightBall, Quit, Admin, AdminResetNames, Backup, Reboot, Update
import discord
import discord_bot


class UnboundUtilityCommands(object):
    def __init__(self, insight_client):
        assert isinstance(insight_client, discord_bot.Discord_Insight_Client)
        self.client: discord_bot.Discord_Insight_Client = insight_client
        self.threadpool_unbound = self.client.threadpool_unbound
        self.dscan = Dscan.Dscan(self)
        self.eightBall = EightBall.EightBall(self)
        self.quit = Quit.Quit(self)
        self.admin = Admin.Admin(self)
        self.admin_resetnames = AdminResetNames.AdminResetNames(self)
        self.admin_backup = Backup.Backup(self)
        self.admin_reboot = Reboot.Reboot(self)
        self.admin_update = Update.Update(self)

    def strip_command(self, message_object: discord.Message):
        try:
            return message_object.content.split(' ', 1)[1]
        except IndexError:
            return ''

    async def command_dscan(self, message_object: discord.Message):
        await self.dscan.run_command(message_object, self.strip_command(message_object))

    async def command_8ball(self, message_object: discord.Message):
        await self.eightBall.run_command(message_object, self.strip_command(message_object))

    async def command_quit(self, message_object: discord.Message):
        await self.quit.run_command(message_object, self.strip_command(message_object))

    async def command_admin(self, message_object: discord.Message):
        await self.admin.run_command(message_object, self.strip_command(message_object))
