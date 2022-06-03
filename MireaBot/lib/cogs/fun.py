import random
from random import randint
from discord.ext import commands
from discord.ext.commands import Cog, command, BucketType, cooldown
from ..db import db


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(name="translate", aliases=["перевод"],
             brief="Переведи сообщение написанное по-русски в английской раскладке.")
    async def translate(self, ctx, *, message):
        letters = {'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', "u": "г", "i": "ш", "o": "щ", "[": "х",
                   "p": "з",
                   "]": "ъ", "a": "ф", "s": "ы", "d": "в", "f": "а", "g": "п", "h": "р", "j": "о", "k": "л", "l": "д",
                   ";": "ж", "'": "э", "z": "я", "x": "ч", "c": "с", "v": "м", "b": "и", "n": "т", "m": "ь", ",": "б",
                   ".": "ю", "`": "ё", "?": ",", "&": "?"}

        message = message.lower()
        res = ''
        for l in message:
            if l in letters:
                res += letters[l]
            else:
                res += l
        await ctx.send(res)

    @command(name="dice", aliases=["roll", "кубик"], brief="Брось кубик в стиле D&D!")
    @cooldown(1, 60, BucketType.user)
    async def roll_dice(self, ctx, dice_value: str):
        dice, value = (int(term) for term in dice_value.split("d"))

        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]

            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

        else:
            await ctx.send(f"Слишком много кубиков, я столько не брошу!")

    @command(name="coinflip", aliases=["coin", "flip", "монетка"], brief='Подбрось монетку.')
    @cooldown(1, 60, BucketType.user)
    async def flip_a_coin(self, ctx):
        coin = random.choice(["орёл", "решка"])
        if coin == "орёл":
            await ctx.send("Выпал орёл!")
        else:
            await ctx.send("Выпала решка!")

    @command(name="ping", brief="Узнать пинг бота.")
    @cooldown(1, 60, BucketType.user)
    async def ping(self, ctx):
        await ctx.send(f"**Pong!** (Ладно, пинг бота {round(self.bot.latency * 1000)} ms)")

    @command(name="random", aliases=["рандом", "число"], brief="Получи случайное число от 1 до n.")
    @cooldown(1, 60, BucketType.user)
    async def random(self, ctx, n):
        if int(n) < 1:
            await ctx.send("Вы ввели число меньше 1!")
        else:
            number = random.randint(1, int(n))
            await ctx.send(f"Вы загадали число от 1 до {str(n)}, выпало число {str(number)}")

    @command(name='addjoke', brief="Добавь новую шутку цитату!")
    async def add_joke(self, ctx, *, phrase):
        with open("./data/jokes.txt", "a", encoding="ANSI") as f:
            f.write(f"{phrase}\n")
        xp = random.randint(50, 100)
        member = ctx.message.author
        db.execute("UPDATE exp SET XP = XP + ? WHERE UserID = ?",
                   xp, member.id)
        await ctx.send(f"Пользователю {member.display_name} добавлено {xp} xp за добавление шутки.")

    @command(name="deljoke", brief="Удалить шутку из списка.")
    async def remove_joke(self, ctx, *, words):
        with open("./data/jokes.txt", "r", encoding="ANSI") as f:
            stored = [w.strip() for w in f.readlines()]

        with open("./data/jokes.txt", "w", encoding="ANSI") as f:
            f.write("".join([f"{w}\n" for w in stored if w not in words]))
        await ctx.send("Шутка удалена.")

    @command(name="joke", aliases=["шутка", "анекдот"], brief="Получи случайную шутку из списка!")
    @cooldown(5, 60, BucketType.user)
    async def joke(self, ctx):
        await ctx.send(random.choice(list(open('./data/jokes.txt'))))

    @command(name="_8ball", aliases=["8ball"], brief="Задайте вопрос магическому шару!")
    @cooldown(1, 30, BucketType.user)
    async def _8ball(self, ctx, *, question):
        responces = ["Бесспорно",
                     "Предрешено",
                     "Никаких сомнений",
                     "Определённо да",
                     "Можешь быть уверен в этом",
                     "Мне кажется — «да»",
                     "Вероятнее всего",
                     "Хорошие перспективы",
                     "Знаки говорят — «да»",
                     "Скорее да чем нет",
                     "Пока не ясно, попробуй снова",
                     "Спроси позже",
                     "Лучше не рассказывать",
                     "Сейчас нельзя предсказать",
                     "Сконцентрируйся и спроси опять",
                     "Даже не думай",
                     "Мой ответ — «нет»",
                     "По моим данным — «нет»",
                     "Перспективы не очень хорошие",
                     "Весьма сомнительно"]
        await ctx.send(f"Вопрос: {question} \nОтвет: {random.choice(responces)}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
