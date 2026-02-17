import discord
from discord.ext import commands
import os
import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "dados.json"

# Criar arquivo se não existir
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command()
async def add(ctx, item: str, quantidade: int):
    user = str(ctx.author)
    data = load_data()

    item = item.lower()

    if item not in data:
        data[item] = {}

    if user not in data[item]:
        data[item][user] = 0

    data[item][user] += quantidade

    save_data(data)

    await ctx.send(f"✅ {quantidade} adicionados em {item} para {user}")

@bot.command()
async def tabela(ctx):
    data = load_data()

    if not data:
        await ctx.send("📭 Nenhum dado registrado ainda.")
        return

    mensagem = ""

    for item, users in data.items():
        total = sum(users.values())
        mensagem += f"\n📦 {item.upper()}\n"

        for user, qtd in users.items():
            mensagem += f"{user} = {qtd}\n"

        mensagem += f"TOTAL = {total}\n"

    await ctx.send(mensagem)

bot.run(os.getenv("TOKEN"))

