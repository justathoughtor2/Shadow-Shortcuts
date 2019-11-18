from discord.ext import commands
import discord
import asyncpg
import asyncio


class Database(commands.Cog):
    """Database related code and tools"""
    def __init__(self, bot):
        self.bot = bot
        bot.database = self
        bot.dblogger = bot.logging_root.getLogger("database")
        loop = asyncio.get_event_loop()
        bot.dbpool = loop.run_until_complete(asyncpg.create_pool(dsn=self.bot.config.SQLDSN, min_size=5, max_size=50,
                                                                 password=self.bot.config.SQLPASS))
        self.logger = bot.dblogger
        bot.logger.info("Initialized Database cog")

    @commands.command()
    @commands.has_any_role('Shadow Guru', 'Moderators', 'Admin')
    async def sql(self, ctx, *, arguments):
        """Admin SQL Tool"""
        if not await self.bot.admin.can_run_command(ctx.author.roles, ['Shadow Guru', 'Moderators']):
            await ctx.send("{ctx.author.mention} your not authorized to do that.".format(ctx=ctx))
            return
        self.logger.info("SQL: {sql}".format(sql=str(arguments)))
        sql = str(arguments)
        async with self.bot.dbpool.acquire() as connection:
            await connection.execute(sql)

    @commands.command(aliases=['cleanpms'])
    @commands.has_any_role('Shadow Guru', 'Moderators', 'Admin')
    async def clean_pm_tracking(self, ctx, *, arguments = None):
        if not await self.bot.admin.can_run_command(ctx.author.roles, ['Shadow Guru', 'Moderators']):
            await ctx.send("{ctx.author.mention} your not authorized to do that.".format(ctx=ctx))
            return
        sql = 'TRUNCATE pm_tracking;'
        self.logger.info(f"PM Tracking cleared by {ctx.author.name} --")
        async with self.bot.dbpool.acquire() as connection:
            await connection.execute(sql)
        await ctx.send(f"{ctx.author.mention} PMs have been cleared.")
        await ctx.message.delete()

    async def log_direct_messages(self, message):
        attach_url = None
        if hasattr(message, 'attachments'):
            attach_url = str()
            for attach in message.attachments:
                attach_url += "<a href=\""+str(attach.url)+"\">Attachment</a> "
        sqlstatement = "INSERT INTO pm_tracking (user_id, user_name, message, attachment_url) VALUES ($1, $2, $3, $4)"
        self.logger.info("SQL: {sql}".format(sql=sqlstatement))
        async with self.bot.dbpool.acquire() as connection:
            await connection.execute(sqlstatement, message.author.id, str(message.author), str(message.content), str(attach_url))

    async def update_leaver_roles(self, member):
        role_list = list()
        role_str = str()
        if member.guild.id != 460948857304383488:
            self.bot.logger.info(f"Ignoring leaver not in our guild of interest {member.id} left guild {member.guild.id}.")
            return
        if hasattr(member, 'roles'):
            for role in member.roles:
                role_list.append(role.id)
        for item in role_list:
            role_str += f"{item},"
        SQL = f"INSERT INTO role_tracking(discord_id, roles) VALUES('{member.id}', '{role_str}') " \
              f"ON CONFLICT (discord_id) DO UPDATE SET roles='{role_str}';"
        async with self.bot.dbpool.acquire() as connection:
            await connection.execute(SQL)

    async def re_apply_roles(self, member):
        roles = list()
        applied_roles = list()
        if member.guild.id != 460948857304383488:
            self.bot.logger.info(f"Ignoring leaver not in our guild of interest {member.id} left guild {member.guild.id}.")
            return
        SQL = f"SELECT roles FROM role_tracking WHERE discord_id='{member.id}' LIMIT 1;"
        async with self.bot.dbpool.acquire() as connection:
            res = await connection.fetch(SQL)
        if len(res) != 0:
            res = res.pop()
        else:
            return
        res = dict(res)
        if res is not None:
            roles = res['roles']
            self.bot.logger.info(f"User {member.id} Has prior roles, reapplying.Found roles: {roles}")
            roles = roles.split(',')
            for item in roles:
                if item is not None:
                    if item == '':
                        continue
                    role = member.guild.get_role(int(item))
                    if role.name == "@everyone":
                        continue
                    if role is not None:
                        applied_roles.append(role)
                        await member.add_roles(role, reason="Re-Applying leaver's roles.")
        self.bot.logger.info(f"Leaver roles applied, for ({member.id}){member.name} Roles-applied: {applied_roles}")

    async def get_language(self, ctx):
        if isinstance(ctx.message.channel, discord.DMChannel):
            return ctx.user.locale  # If we are in a DM Attempt to respond in users locale.
        else:
            return ctx.guild.preferred_locale  # If not in DM return guild Locale

    async def get_configuration(self, ctx):
        config = dict()
        if isinstance(ctx.message.channel, discord.DMChannel):
            config['guild'] = None # DMS exist outside of guilds
        else:
            config['guild'] = ctx.guild.id  # guild ID Number
        config['lang'] = self.bot.database.get_language(ctx)  # Preferred Language for this context


def setup(bot):
    bot.add_cog(Database(bot))
