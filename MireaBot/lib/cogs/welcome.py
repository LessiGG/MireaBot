import discord
from datetime import datetime
from discord import Forbidden
from discord.ext.commands import Cog

from ..db import db

emoji1 = " :inbox_tray: "
emoji2 = " :outbox_tray: "

class Welcome(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("welcome")

	@Cog.listener()
	async def on_member_join(self, member):
		db.execute("INSERT INTO exp (UserID) VALUES (?)", member.id)
		await self.bot.get_channel(905789838073163827).send(f"Добро пожаловать на сервер **{member.guild.name}**, {member.mention}! Отправляйся в <#855541369899450408> чтобы поздороваться!")
		channel = self.bot.get_channel(905750858577354753)
		creation_date = str(member.created_at)
		creation_date = creation_date[:-10]
		emb = discord.Embed(colour = discord.Color.green(),
	 						description = "{} **Пользователь {} присоединился к серверу.**"
	 						.format(emoji1, member.mention), timestamp = datetime.utcnow())
		emb.set_author(name = member, icon_url = member.avatar_url)
		emb.add_field(name = "Аккаунт создан", value = "{}".format(creation_date))
		emb.set_footer(text = f"ID: {member.id}")
		emb.set_thumbnail(url = member.avatar_url)
		await channel.send(embed = emb)


		try:
			await member.send(f"Добро пожаловать на сервер **{member.guild.name}**! Надеемся, тебе тут понравится и ты останешься с нами!")

		except Forbidden:
			pass

		await member.add_roles(member.guild.get_role(905790191451643944))

	@Cog.listener()
	async def on_member_remove(self, member):
		db.execute("DELETE FROM exp WHERE UserID = ?", member.id)
		channel = self.bot.get_channel(905750858577354753)
		emb = discord.Embed(colour = discord.Color.red(),
	 						description = "{} **Пользователь {} покинул сервер.**"
	 						.format(emoji2, member.mention), timestamp = datetime.utcnow())
		emb.set_author(name = member, icon_url = member.avatar_url)
		emb.set_footer(text = f"ID: {member.id}")
		emb.set_thumbnail(url = member.avatar_url)
		await channel.send(embed = emb)


def setup(bot):
	bot.add_cog(Welcome(bot))