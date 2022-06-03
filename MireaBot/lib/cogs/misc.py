from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from ..db import db

class Misc(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="prefix", aliases = ["префикс"], brief = "Поменяй префикс сервера.")
	@has_permissions(manage_guild=True)
	async def change_prefix(self, ctx, new: str):
		if len(new) > 2:
			await ctx.send("Префикс не может быть больше двух символов.")

		else:
			db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, ctx.guild.id)
			await ctx.send(f"Установлен префикс {new}.")

	@change_prefix.error
	async def change_prefix_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Вам не хватает прав.")
	
	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("misc")


def setup(bot):
	bot.add_cog(Misc(bot))