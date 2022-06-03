from datetime import datetime
from typing import Optional

from discord import Embed, Member
from discord.ext.commands import Cog
from discord.ext.commands import command

class Info(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="userinfo", aliases=["юзер"], brief = "Узнай информацию о пользователе.")
	async def user_info(self, ctx, target: Optional[Member]):
		target = target or ctx.author

		embed = Embed(title="Информация о пользователе",
					  colour=target.colour,
					  timestamp=datetime.utcnow())

		embed.set_thumbnail(url=target.avatar_url)

		fields = [("Имя", str(target), True),
				  ("ID", target.id, True),
				  ("Высшая роль", target.top_role.mention, True),
				  ("Состояние", str(target.status).title(), True),
				  ("Статус", f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}", True),
				  ("Аккаунт создан", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				  ("Присоединился к серверу", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				  ("Буст сервера", bool(target.premium_since), True)]

		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)

		await ctx.send(embed=embed)

	@command(name="serverinfo", aliases=["guildinfo", "сервер"], brief = "Узнай информацию о сервере.")
	async def server_info(self, ctx):
		embed = Embed(title="Информация о сервере",
					  colour=ctx.guild.owner.colour,
					  timestamp=datetime.utcnow())

		embed.set_thumbnail(url=ctx.guild.icon_url)

		statuses = [len(list(filter(lambda m: str(m.status) == "В сети", ctx.guild.members))),
					len(list(filter(lambda m: str(m.status) == "Не активен", ctx.guild.members))),
					len(list(filter(lambda m: str(m.status) == "Не беспокоить", ctx.guild.members))),
					len(list(filter(lambda m: str(m.status) == "Не в сети", ctx.guild.members)))]

		fields = [("ID", ctx.guild.id, True),
				  ("Владелец", ctx.guild.owner, True),
				  ("Регион", ctx.guild.region, True),
				  ("Создан", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				  ("Участники", len(ctx.guild.members), True),
				  ("Люди", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
				  ("Боты", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
				  ("Забаненные пользователи", len(await ctx.guild.bans()), True),
				  ("Статусы", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", True),
				  ("Тектовые каналы", len(ctx.guild.text_channels), True),
				  ("Голосовые каналы", len(ctx.guild.voice_channels), True),
				  ("Категории", len(ctx.guild.categories), True),
				  ("Роли", len(ctx.guild.roles), True),
				  ("Приглашения", len(await ctx.guild.invites()), True),
				  ("\u200b", "\u200b", True)]

		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)

		await ctx.send(embed=embed)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("info")


def setup(bot):
	bot.add_cog(Info(bot))