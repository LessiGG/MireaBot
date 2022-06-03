from datetime import datetime, timedelta
from random import choice

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

from ..db import db

numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
		   "6⃣", "7⃣", "8⃣", "9⃣", "🔟")

class Reactions(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.polls = []
		self.giveaways = []


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:

			self.roles = {"👽":self.bot.guild.get_role(911667740048261201), # Among Us
						  "🎮":self.bot.guild.get_role(911667668212416582), # JackBox
				     	  "💀":self.bot.guild.get_role(905572884473348096), # Дотеры
				     	  "🖍️":self.bot.guild.get_role(898340077439184916), # Художники
				     	  "🧙‍♀️":self.bot.guild.get_role(926905352337907823) # Overwatch
						 }

			self.reaction_message = await self.bot.get_channel(905740881854861352).fetch_message(905740967812935691)
			self.starboard_channel = self.bot.get_channel(780909043551043674)
			self.bot.cogs_ready.ready_up("reactions")


	@command(name="createpoll", aliases=["опрос"], brief = "Создай новый опрос.")
	@has_permissions(manage_guild=True)
	async def create_poll(self, ctx, seconds: int, question: str, *options):
		if len(options) > 10:
			await ctx.send("Максимум может быть 10 вариантов ответов.")

		else:
			embed = Embed(title="Опрос",
						  description=question,
						  colour=ctx.author.colour,
						  timestamp=datetime.utcnow())

			fields = [("Варианты ответа", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
					  ("Инструкция", "Нажмите на реакцию чтобы проголосовать!", False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			message = await ctx.send(embed=embed)

			for emoji in numbers[:len(options)]:
				await message.add_reaction(emoji)

			self.polls.append((message.channel.id, message.id))

			self.bot.scheduler.add_job(self.complete_poll, "date", run_date=datetime.now()+timedelta(seconds=seconds),
									   args=[message.channel.id, message.id])

	@command(name="giveaway", brief = "Устрой розыгрыш.")
	@has_permissions(manage_guild=True)
	async def create_giveaway(self, ctx, seconds: int, *, description: str):
		time = str(datetime.now()+timedelta(seconds=seconds))
		embed = Embed(title="Розыгрыш",
					  description=description,
					  colour=ctx.author.colour,
					  timestamp=datetime.utcnow())

		fields = [("Результаты розыгрыша:", f"{time[:-6]}", False),
				  ("Инструкция", "Нажмите на реакцию чтобы поучаствовать в розыгрыше!", False)]

		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)

		message = await ctx.send(embed=embed)
		await message.add_reaction("✅")

		self.giveaways.append((message.channel.id, message.id))

		self.bot.scheduler.add_job(self.complete_giveaway, "date", run_date=datetime.now()+timedelta(seconds=seconds),
								   args=[message.channel.id, message.id])

	async def complete_poll(self, channel_id, message_id):
		message = await self.bot.get_channel(channel_id).fetch_message(message_id)

		most_voted = max(message.reactions, key=lambda r: r.count)

		await message.channel.send(f"Опрос завершен. Вариант {most_voted.emoji} побеждает набрав голосов: {most_voted.count-1:,}!")
		self.polls.remove((message.channel.id, message.id))

	async def complete_giveaway(self, channel_id, message_id):
		message = await self.bot.get_channel(channel_id).fetch_message(message_id)

		if len((entrants := [u for u in await message.reactions[0].users().flatten() if not u.bot])) > 0: #and not u.id == 879934912696836136
			winner = choice(entrants)
			await message.channel.send(f"Поздравляю, {winner.mention} - ты выиграл в розыгрыше!")
			self.giveaways.remove((message.channel.id, message.id))

		else:
			await message.channel.send("Розыгрыш окончен - никто не принял участие.")
			self.giveaways.remove((message.channel.id, message.id))


	@Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if self.bot.ready and payload.message_id == self.reaction_message.id:
				await payload.member.add_roles(self.roles[payload.emoji.name], reason="Реакция на роль.")
				
		elif payload.message_id in (poll[1] for poll in self.polls):
			message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

			for reaction in message.reactions:
				if (not payload.member.bot
					and payload.member in await reaction.users().flatten()
					and reaction.emoji != payload.emoji.name):
					await message.remove_reaction(reaction.emoji, payload.member)

	@Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if self.bot.ready and payload.message_id == self.reaction_message.id:
			member = self.bot.guild.get_member(payload.user_id)
			await member.remove_roles(self.roles[payload.emoji.name], reason="Реакция на роль убрана.")

def setup(bot):
	bot.add_cog(Reactions(bot))