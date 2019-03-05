from discord.ext import commands
import discord
import aiohttp
import traceback


class Admin(commands.Cog):
    """Admin level bot commands cog"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.admin = self
        self._last_member = None

    @commands.command(hidden=True)
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send('```py\n{traceback.format_exc()}\n```'.format(traceback=traceback))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.send('```py\n{traceback.format_exc()}\n```'.format(traceback=traceback))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    async def _reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send('```py\n{traceback.format_exc()}\n```'.format(traceback=traceback))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @staticmethod
    async def can_run_command(role_check, allowed=None):
        role_check = [role.name for role in role_check]
        if allowed is None:
            allowed = ['Shadow Guru', 'Moderators', 'Shadow Staff', 'Clay\'s Lieutenants', 'Admin', 'Silent Admin',
                       'Administrator', 'Bot User']
        for item in allowed:
            if item in role_check:
                return True
        return False

    @staticmethod
    async def tail(filename, lines):
        import subprocess
        output = subprocess.getoutput("tail -n {lines} {filename}".format(filename=filename, lines=lines))
        return output

    async def get_status(self):
        import lxml.html
        async with aiohttp.ClientSession() as session:
            html = await self.bot.admin.fetch(session, 'https://status.shadow.tech')
            doc = lxml.html.fromstring(html)
            status_text = doc.xpath('//strong[@id="statusbar_text"]')[0].text_content()
        if "All Systems Operational" == status_text:
            return "Normal"
        else:
            return status_text

    @staticmethod
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()

    @commands.command(description="Auto-Responders debug", name="timertest")
    async def _timertest(self, ctx):
        if self.can_run_command(ctx.author.roles, ['Shadow Guru', 'Moderator']):
            timers = " "
            for item in self.last_message.keys():
                timers += "{:10s} - {:10s}\n".format(item, bot.last_message[item].isoformat())
            await ctx.send("Timer debug:\n```{timers}```".format(timers=timers))
        else:
            await ctx.send("{author} You aren't authorized to do that.".format(author=ctx.author.mention))

    @commands.command(description="Add Shadower role to a user", name='ar')
    async def add_role(self, ctx, *, user: discord.Member = None):
        if self.can_run_command(ctx.author.roles, ['Shadow Guru', 'Moderator']):
            if user is None:
                await ctx.send("{author} User is a required parameter.".format(author=ctx.author.mention))
            else:
                if "Shadowers" not in [role.name for role in user.roles]:
                    shadowers = ctx.guild.get_role(461298541978058769)
                    await user.add_roles(shadowers)
                    await ctx.message.add_reaction('✅')
                else:
                    await ctx.send("{author} User {user.mention} appears to already have this role.".format(
                        author=ctx.author.mention, user=user))
        else:
            await ctx.send("{author} You aren't authorized to do that.".format(author=ctx.author.mention))

    @commands.command(description="Grant a user bot access", name='grantbot')
    async def add_role_bot(self, ctx, *, user: discord.Member = None):
        if self.can_run_command(ctx.author.roles, ['Shadow Guru', 'Moderator']):
            if user is None:
                await ctx.send("{author} User is a required parameter.".format(author=ctx.author.mention))
            else:
                if "Bot User" not in [role.name for role in user.roles]:
                    shadowers = ctx.guild.get_role(551917324949651477)
                    await user.add_roles(shadowers)
                    await ctx.message.add_reaction('✅')
                else:
                    await ctx.send("{author} User {user.mention} appears to already have this role.".format(
                        author=ctx.author.mention, user=user))
        else:
            await ctx.send("{author} You aren't authorized to do that.".format(author=ctx.author.mention))

    @commands.command(description="Revoke a user bot access", name='revokebot')
    async def revoke_role_bot(self, ctx, *, user: discord.Member = None):
        if self.can_run_command(ctx.author.roles, ['Shadow Guru', 'Moderator']):
            if user is None:
                await ctx.send("{author} User is a required parameter.".format(author=ctx.author.mention))
            else:
                if "Bot User" in [role.name for role in user.roles]:
                    shadowers = ctx.guild.get_role(551917324949651477)
                    await user.remove_roles(shadowers)
                    await ctx.message.add_reaction('✅')
                else:
                    await ctx.send("{author} User {user.mention} appears to not have this role.".format(author=ctx.author.mention, user=user))
        else:
            await ctx.send("{author} You aren't authorized to do that.".format(author=ctx.author.mention))

    @commands.command(description="Roles test", name='roletest')
    async def _roletest(self, ctx):
        if self.can_run_command(ctx.author.roles, ['Shadow Guru', 'Moderator']):
            guild = ctx.guild
            await ctx.send("Beginning role debug")
            for role in guild.roles:
                await ctx.send("``{role.id}: {role.name}``".format(role=role))
        else:
            await ctx.send("{author} You aren't authorized to do that.".format(author=ctx.author.mention))


def setup(bot):
    bot.add_cog(Admin(bot))