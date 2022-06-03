from asyncio import sleep
from datetime import datetime
from glob import glob

from discord import Intents
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Embed, DMChannel
from discord.errors import Forbidden
from discord.ext.commands import Context
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
								  CommandOnCooldown)
from discord.ext.commands import when_mentioned_or

from ..db import db 

OWNER_IDS = [394453038263304192]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

def get_prefix(bot, message):
	prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
	return when_mentioned_or(prefix)(bot, message)


class Ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)
		print(f"{cog} cog ready")

	def all_ready(self):
		return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
	def __init__(self):
		self.ready = False 
		self.cogs_ready = Ready()
		self.guild = None
		self.scheduler = AsyncIOScheduler()

		db.autosave(self.scheduler)
		super().__init__(
			 command_prefix = get_prefix,
			 owner_ids = OWNER_IDS,
			 intents = Intents.all()
		)

	def setup(self):
		for cog in COGS:
			self.load_extension(f"lib.cogs.{cog}")
			print(f"{cog} cog loaded.")

		print("setup complete")


	def update_db(self):
		db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
					 ((guild.id,) for guild in self.guilds))

		db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
					 ((member.id,) for member in self.guild.members if not member.bot))

		to_remove = []
		stored_members = db.column("SELECT UserID FROM exp")
		for id_ in stored_members:
			if not self.guild.get_member(id_):
				to_remove.append(id_)

		db.multiexec("DELETE FROM exp WHERE UserID = ?",
					 ((id_,) for id_ in to_remove))

		db.commit()


	def run(self, version):
		self.VERSION = version

		print("running setup...")
		self.setup()

		with open("./lib/bot/token.0", "r", encoding = "utf-8") as tf:
			self.TOKEN = tf.read()

		print("running MireBot...")
		super().run(self.TOKEN, reconnect = True)

	async def process_commands(self, message):
		ctx = await self.get_context(message, cls = Context)

		if ctx.command is not None and ctx.guild is not None:
			if self.ready:
				await self.invoke(ctx)

			else:
				await ctx.send("Я не готов принимать команды, подожди пожалуйста!")

	async def on_connect(self):
		print("MireBot is connected.")

	async def on_disconnect(self):
		print("MireBot is disconnected.")

	async def on_error(self, err, *args, **kwargs):
		if err == "on_command_error":
			await args[0].send("Что-то пошло не так.")

		# await self.estebot.send("Произошла ошибка.")
		raise

	async def on_command_error(self, ctx, exc):
		if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
			pass

		elif isinstance(exc, MissingRequiredArgument):
			await ctx.send("Не хватает какого-то аргумента.")

		elif isinstance(exc, CommandOnCooldown):
			await ctx.send(f"Эта команда пока не доступна. Попробуйте через {exc.retry_after:,.2f} секунд.")

		elif hasattr(exc, "original"):
			if isinstance(exc.original, Forbidden):
				await ctx.send("Мне не хватает прав на выполнение этой команды.")

			else:
				raise exc.original

		else:
			raise exc

	async def on_ready(self):
		if not self.ready:
			self.guild = self.get_guild(855541369452232745)
			self.estebot = self.get_channel(855552658977849364)
			self.chat = self.get_channel(855541369899450408)
			self.bugfixes = self.get_channel(905794702715015209)
			self.scheduler.start()

			self.update_db()

			while not self.cogs_ready.all_ready():
				await sleep(0.5)

			await self.estebot.send("Я в сети!")
			self.ready = True
			print("MireBot is online")

		else:
			print("MireBot is reconnected")

	async def on_message(self, message):
		if not message.author.bot:
			if isinstance(message.channel, DMChannel):
				if len(message.content) < 25:
					await message.channel.send("Сообщение должно содержать хотя-бы 25 символов.")

				else:
					member = self.guild.get_member(message.author.id)
					embed = Embed(title=f"Сообщение от пользователя {member}",
								  colour=member.colour,
								  timestamp=datetime.utcnow())

					embed.set_thumbnail(url=member.avatar_url)

					fields = [("Пользователь", member.display_name, False),
							  ("Сообщение", message.content, False)]

					for name, value, inline in fields:
						embed.add_field(name=name, value=value, inline=inline)

					await self.bugfixes.send(embed=embed)
					await message.channel.send("Сообщение переслано модератору.")

			else:
				await self.process_commands(message)


bot = Bot()