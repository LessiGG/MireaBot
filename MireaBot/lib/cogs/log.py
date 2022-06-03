from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command

class Log(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.log_channel = self.bot.get_channel(905750858577354753)
			self.bot.cogs_ready.ready_up("log")

	@Cog.listener()
	async def on_user_update(self, before, after):
		if before.name != after.name:
			embed = Embed(title="Смена ника",
						  colour=after.colour,
						  timestamp=datetime.utcnow())

			fields = [("До", before.name, False),
					  ("После", after.name, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			await self.log_channel.send(embed=embed)

		if before.discriminator != after.discriminator:
			embed = Embed(title="Смена дискриминатора",
						  colour=after.colour,
						  timestamp=datetime.utcnow())

			fields = [("До", before.discriminator, False),
					  ("После", after.discriminator, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			await self.log_channel.send(embed=embed)

		if before.avatar_url != after.avatar_url:
			embed = Embed(title="Смена аватара",
						  description=f"Новый аватар пользователя {after.display_name} снизу, старый справа.",
						  colour=self.log_channel.guild.get_member(after.id).colour,
						  timestamp=datetime.utcnow())

			embed.set_thumbnail(url=before.avatar_url)
			embed.set_image(url=after.avatar_url)

			await self.log_channel.send(embed=embed)

	@Cog.listener()
	async def on_member_update(self, before, after):
		if before.display_name != after.display_name:
			embed = Embed(title="Смена ника",
						  colour=after.colour,
						  timestamp=datetime.utcnow())

			fields = [("До", before.display_name, False),
					  ("После", after.display_name, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			await self.log_channel.send(embed=embed)

		elif before.roles != after.roles:
			embed = Embed(title="Смена ролей",
						  colour=after.colour,
						  description = f"Пользователь {after.display_name} обновил роли.",
						  timestamp=datetime.utcnow())

			fields = [("До", ", ".join([r.mention for r in before.roles]), False),
					  ("После", ", ".join([r.mention for r in after.roles]), False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			await self.log_channel.send(embed=embed)

	@Cog.listener()
	async def on_message_edit(self, before, after):
		if not after.author.bot:
			if before.content != after.content:
				embed = Embed(title="Редактирование сообщения",
							  description=f"Выполнил {after.author.display_name}.",
							  colour=after.author.colour,
							  timestamp=datetime.utcnow())

				fields = [("До", before.content, False),
						  ("После", after.content, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)

	@Cog.listener()
	async def on_message_delete(self, message):
		if not message.author.bot:
			embed = Embed(title="Удаление сообщения",
						  description=f"Выполнил {message.author.display_name}.",
						  colour=message.author.colour,
						  timestamp=datetime.utcnow())

			fields = [("Содержание", message.content, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			await self.log_channel.send(embed=embed)


def setup(bot):
	bot.add_cog(Log(bot))