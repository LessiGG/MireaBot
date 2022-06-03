from datetime import datetime, timedelta
from random import randint
from typing import Optional

import discord

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions
from discord.ext.menus import MenuPages, ListPageSource

from ..db import db

bloodTrail = "<:bloodTrail:901536501555413052>"


class HelpMenu(ListPageSource):
	def __init__(self, ctx, data):
		self.ctx = ctx

		super().__init__(data, per_page=10)

	async def write_page(self, menu, offset, fields=[]):
		len_data = len(self.entries)

		embed = Embed(title="Таблица лидеров по XP",
					  colour=self.ctx.author.colour)
		embed.set_thumbnail(url=self.ctx.guild.icon_url)
		embed.set_footer(text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} из {len_data:,} участников.")

		for name, value in fields:
			embed.add_field(name=name, value=value, inline=False)

		return embed

	async def format_page(self, menu, entries):
		offset = (menu.current_page*self.per_page) + 1

		fields = []
		table = ("\n".join(f"{idx+offset}. {self.ctx.bot.guild.get_member(entry[0]).display_name} (XP: {entry[1]} | Уровень: {entry[2]})"
				for idx, entry in enumerate(entries)))

		fields.append(("Ранги", table))

		return await self.write_page(menu, offset, fields)


class Exp(Cog):
	def __init__(self, bot):
		self.bot = bot

	async def process_xp(self, message):
		xp, lvl, xplock = db.record("SELECT XP, Level, XPLock FROM exp WHERE UserID = ?", message.author.id)

		if datetime.utcnow() > datetime.fromisoformat(xplock):
			await self.add_xp(message, xp, lvl)

	async def add_xp(self, message, xp, lvl):
		xp_to_add = randint(10, 20)
		new_lvl = int(((xp+xp_to_add)//42) ** 0.55)

		db.execute("UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ?",
				   xp_to_add, new_lvl, (datetime.utcnow()+timedelta(seconds=60)).isoformat(), message.author.id)

		if new_lvl > lvl:
			await self.levelup_channel.send(f"Поздравляю, {message.author.mention} - ты достиг {new_lvl:,} уровня! Так держать! {bloodTrail}")
			await self.check_lvl_rewards(message, new_lvl)

	async def check_lvl_rewards(self, message, lvl):
		if lvl >= 50: # Red
			if (new_role := message.guild.get_role(911676745621594162)) not in message.author.roles:
				await message.author.add_roles(new_role)
				await message.author.remove_roles(message.guild.get_role(911676612196577360))

		elif 40 <= lvl < 50: 
			if (new_role := message.guild.get_role(911676612196577360)) not in message.author.roles:
				await message.author.add_roles(new_role)
				await message.author.remove_roles(message.guild.get_role(911676537332449410))

		elif 30 <= lvl < 40: 
			if (new_role := message.guild.get_role(911676537332449410)) not in message.author.roles:
				await message.author.add_roles(new_role)
				await message.author.remove_roles(message.guild.get_role(911676406952525894))

		elif 20 <= lvl < 30: 
			if (new_role := message.guild.get_role(911676406952525894)) not in message.author.roles:
				await message.author.add_roles(new_role)
				await message.author.remove_roles(message.guild.get_role(911676278204157962))

		elif 10 <= lvl < 20: 
			if (new_role := message.guild.get_role(911676278204157962)) not in message.author.roles:
				await message.author.add_roles(new_role)
				await message.author.remove_roles(message.guild.get_role(911676177314357268))

		if 5 <= lvl < 9: # 5-9
			if (new_role := message.guild.get_role(911676177314357268)) not in message.author.roles:
				await message.author.add_roles(new_role)

	@command(name="level", aliases = ["Уровень", "лвл", "lvl"], brief = "Узнай какой у тебя уровень.")
	async def display_level(self, ctx, target: Optional[discord.Member]):
		target = target or ctx.author

		xp, lvl = db.record("SELECT XP, Level FROM exp WHERE UserID = ?", target.id) or (None, None)

		if lvl is not None:
			await ctx.send(f"{target.display_name} на {lvl:,} уровне и имеет {xp:,} XP.")

		else:
			await ctx.send("Этого пользователя нет в системе уровней.")

	@command(name="rank", aliases = ["ранг"], brief = "Узнай какой у тебя ранг.")
	async def display_rank(self, ctx, target: Optional[discord.Member]):
		target = target or ctx.author

		ids = db.column("SELECT UserID FROM exp ORDER BY XP DESC")

		try:
			await ctx.send(f"{target.display_name} имеет ранг {ids.index(target.id)+1} из {len(ids)}.")

		except ValueError:
			await ctx.send("Этого пользователя нет в системе уровней.")

	@command(name="leaderboard", aliases=["лидеры"], brief = "Посмотри таблицу лидеров.")
	async def display_leaderboard(self, ctx):
		records = db.records("SELECT UserID, XP, Level FROM exp ORDER BY XP DESC")

		menu = MenuPages(source=HelpMenu(ctx, records),
						 clear_reactions_after=True,
						 timeout=60.0)
		await menu.start(ctx)

	
	@command(name = "givexp", brief = "Добавь опыта выбранному пользователю.")
	@has_permissions(manage_guild=True)
	async def give_xp(self, ctx, xp, member: discord.Member):
		if ctx.author.id == 394453038263304192 or ctx.author.id == 324532025887555585:
			xp = xp
			member = member or ctx.author
			db.execute("UPDATE exp SET XP = XP + ? WHERE UserID = ?",
					   xp, member.id)
			await ctx.send(f"Пользователю {member.display_name} добавлено {xp} xp.")
		else:
			await ctx.send("Че, самый умный?) <:KEKW:751551451498676295>")


	@command(name = "takexp", brief = "Забери опыт у выбранного пользователя.")
	@has_permissions(manage_guild=True)
	async def take_xp(self, ctx, xp, member: discord.Member):
		if ctx.author.id == 394453038263304192 or ctx.author.id == 324532025887555585:
			xp = xp
			member = member or ctx.author
			db.execute("UPDATE exp SET XP = XP - ? WHERE UserID = ?",
					   xp, member.id)
			await ctx.send(f"Пользователь {member.display_name} потерял {xp} xp.")
		else:
			await ctx.send("Че, самый умный?) <:KEKW:751551451498676295>")


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.levelup_channel = self.bot.get_channel(905736639488356362)
			self.bot.cogs_ready.ready_up("exp")

	@Cog.listener()
	async def on_message(self, message):
		if not message.author.bot:
			await self.process_xp(message)


def setup(bot):
	bot.add_cog(Exp(bot))