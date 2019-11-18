from discord.ext import commands
import discord
import traceback


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.events = self
        bot.logger.info("Initialized Events Cog")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        await ctx.message.add_reaction("😢")
        if isinstance(exception, discord.ext.commands.errors.CommandNotFound):
            await ctx.author.send("{author.mention} {exception}".format(author=ctx.author, exception=exception))
            await ctx.message.add_reaction('✋')
        elif isinstance(exception, discord.ext.commands.errors.BadArgument):
            await ctx.send("{author.mention} Bad Argument exception: {exception}".format(author=ctx.author, exception=exception))
        elif isinstance(exception, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("{author.mention} Required argument missing: {exception}".format(author=ctx.author, exception=exception))
        elif isinstance(exception, discord.NotFound):
            await ctx.send("{author.mention} Got a discord.NotFound error: {exception}".format(author=ctx.author, exception=exception))
        elif isinstance(exception, discord.ext.commands.CheckFailure):
            await ctx.send(f"{ctx.author.mention} You are not authorized to perform this command. {exception}")
        self.bot.logger.info(
            "Error encountered processing command enacting message: {ctx.message} enacting user: {ctx.author.name} Exception: {exception}\nTraceback:{traceback}".format(
                ctx=ctx, exception=exception, traceback=traceback.format_tb(exception.__traceback__)))
        await ctx.send("Error encountered processing command enacting message: {ctx.message} enacting user: {ctx.author.name} Exception: {exception}\nTraceback:{traceback}".format(
                ctx=ctx, exception=exception, traceback=traceback.format_tb(exception.__traceback__)))


    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info("Bot Starting up.. Logged in as:" + str(self.bot.user.name) + " ID: " + str(self.bot.user.id))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.bot.database.update_leaver_roles(member)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.database.re_apply_roles(member)

    @commands.Cog.listener()
    async def on_message(self, message):
        self.bot.logger.debug("Recieved message from {message.author} Content {message.content}".format(message=message))
        if isinstance(message.channel, discord.DMChannel):
            if message.author.id == self.bot.user.id:
                return
            elif message.author.bot:
                return
            await self.bot.database.log_direct_messages(message)
            await message.author.send("{message.author.mention} your message has been logged, This is an automated bot.".format(message=message))
        if not hasattr(message.author, 'roles'):
            role_names = []
        else:
            role_names = message.author.roles
        if message.author.id == self.bot.user.id:
            return
        elif message.role_mentions != list():
            if not await self.bot.admin.can_run_command(role_names):
                self.bot.logger.info(f"Role mentions: {message.role_mentions}")
                await message.channel.send(f"{message.author.mention} Please don't mass tag, unless an absolute emergency. Thanks.")
        elif ("L:104" in message.content.lower()) and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                        message=f"{message.author.mention} hit the :grey_question:  then scroll down and hit ***Shutdown Shadow***,  wait 2-5 minutes then restart your client http://botstatic.stavlor.net/reboot.gif",
                                        trigger="L:104")
        elif ("L 104" in message.content.lower()) and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                        message=f"{message.author.mention} hit the :grey_question:  then scroll down and hit ***Shutdown Shadow***,  wait 2-5 minutes then restart your client http://botstatic.stavlor.net/reboot.gif",
                                        trigger="L 104")
        elif (" 104" in message.content.lower()) and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                        message=f"{message.author.mention} hit the :grey_question:  then scroll down and hit ***Shutdown Shadow***,  wait 2-5 minutes then restart your client http://botstatic.stavlor.net/reboot.gif",
                                        trigger="104")
        elif ("shadow is off" in message.content.lower()) and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                        message=f"{message.author.mention} hit the :grey_question:  then scroll down and hit ***Shutdown Shadow***,  wait 2-5 minutes then restart your client http://botstatic.stavlor.net/reboot.gif",
                                        trigger="104")
        elif "800x600" in message.content.lower() and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                        message="{ctx.author.mention} Please see the following to fix issues with 800x600 resolution http://botstatic.stavlor.net/800x600.png",
                                        trigger="800x600")
        elif "input lag" in message.content.lower() and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                        message="{ctx.author.mention} Please see the following tips for solving input lag issues http://botstatic.stavlor.net/inputlag.png",
                                        trigger="input lag")
        elif "password expired" in message.content.lower() and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                        message="""{ctx.author.mention} Ready-To-Go Password Update
If you used the Ready-To-Go setting when setting up your account, any version prior to Windows 10 1903 has an expired password notice approximately 1-3 months after activation. This bug has been fixed by Windows. To fix, simply update to the latest Windows version. (1903) - 

If you have any issues updating the default password is blank “” if your password is expired.""",
                                        trigger="password expired")
        elif "expired password" in message.content.lower() and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                                             message="""{ctx.author.mention} Ready-To-Go Password Update
            If you used the Ready-To-Go setting when setting up your account, any version prior to Windows 10 1903 has an expired password notice approximately 1-3 months after activation. This bug has been fixed by Windows. To fix, simply update to the latest Windows version. (1903) - 

            If you have any issues updating the default password is blank “” if your password is expired.""",
                                                             trigger="password expired")
        elif "waiting for video" in message.content.lower() and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                        message="{ctx.author.mention} Please see the following to fix waiting for video http://botstatic.stavlor.net/waiting_for_video.png",
                                        trigger="waiting for video")
        elif "video error" in message.content.lower() and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                        message="{ctx.author.mention} Please see the following to fix waiting for video http://botstatic.stavlor.net/waiting_for_video.png",
                                        trigger="waiting for video")
        elif "long to boot up" in message.content.lower() and not await bot.admin.can_run_command(role_names):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                        message="{ctx.author.mention} Please see the following to fix waiting for video http://botstatic.stavlor.net/waiting_for_video.png",
                                        trigger="waiting for video")
        elif "3/3" in message.content.lower() and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autorespone.auto_response_message(ctx=message,
                                        message="{ctx.author.mention} Please see the following to fix waiting for video http://botstatic.stavlor.net/waiting_for_video.png",
                                        trigger="3/3")
        elif "shadow is off" in message.content.lower() and not (await self.bot.admin.can_run_command(role_names)):
            await self.bot.autoresponse.auto_response_message(ctx=message,
                                                              message="{ctx.author.mention} Please follow the following steps to resolve your issue, Please access your help menu :grey_question: then scroll down and hit ***Shutdown Shadow***, then wait 2-5 minutes and restart your client to resolve your issue http://botstatic.stavlor.net/reboot.gif ",
                                                              trigger="shadow is off")
        elif "good bot" in message.content.lower():
            await message.add_reaction("🍪")
            await message.add_reaction("👍")



def setup(bot):
    bot.add_cog(Events(bot))
