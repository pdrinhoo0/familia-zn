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

# 🔹 ADICIONAR ITEM
@bot.command()
async def add(ctx, item: str, quantidade: int):
    user = ctx.author.name  # 👈 agora pega só o nome
    data = load_data()

    item = item.lower()

    if item not in data:
        data[item] = {}

    if user not in data[item]:
        data[item][user] = 0

    data[item][user] += quantidade

    save_data(data)

    await ctx.send(f"✅ {quantidade} adicionados em {item}")

# 🔹 RETIRAR ITEM
@bot.command()
async def retirar(ctx, item: str, quantidade: int):
    user = ctx.author.name  # 👈 só nome
    data = load_data()

    item = item.lower()

    if item not in data or user not in data[item]:
        await ctx.send("❌ Você não possui esse item registrado.")
        return

    if data[item][user] < quantidade:
        await ctx.send("❌ Você não tem essa quantidade para retirar.")
        return

    data[item][user] -= quantidade

    # Se ficar 0, remove o usuário daquele item
    if data[item][user] == 0:
        del data[item][user]

    # Se nenhum usuário tiver mais o item, remove o item
    if not data[item]:
        del data[item]

    save_data(data)

    await ctx.send(f"➖ {quantidade} retirados de {item}")

# 🔹 MOSTRAR TABELA BONITA
@bot.command()
async def tabela(ctx):
    data = load_data()

    if not data or len(data) == 0:
        await ctx.send("📭 Nenhum dado registrado ainda.")
        return

    mensagem = ""

    for item in data:
        users = data[item]

        if not users:
            continue

        total = 0

        mensagem += "━━━━━━━━━━━━━━━━━━\n"
        mensagem += f"📦 {item.upper()}\n"
        mensagem += "━━━━━━━━━━━━━━━━━━\n"

        for user in users:
            qtd = users[user]
            total += qtd
            mensagem += f"{user:<12} {qtd}\n"

        mensagem += "━━━━━━━━━━━━━━━━━━\n"
        mensagem += f"{'TOTAL':<12} {total}\n\n"

    await ctx.send(f"```{mensagem}```")

# 🔹 RESETAR TUDO (admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def reset(ctx):
    save_data({})
    await ctx.send("🗑️ Todos os dados foram resetados com sucesso!")

bot.run(os.getenv("TOKEN"))
