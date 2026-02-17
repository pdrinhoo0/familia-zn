import discord
from discord.ext import commands
import os
import json
import shutil
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "dados.json"
BACKUP_FOLDER = "backups"
MAX_BACKUPS = 5

CANAL_BACKUP_ID = 1473419060908789821  # ✅ ID DO SEU CANAL

if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

async def criar_backup():
    if not os.path.exists(DATA_FILE):
        return

    data_atual = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    backup_nome = f"{BACKUP_FOLDER}/backup_{data_atual}.json"

    shutil.copy(DATA_FILE, backup_nome)

    # Enviar para canal do Discord
    canal = bot.get_channel(CANAL_BACKUP_ID)
    if canal:
        await canal.send(
            f"📦 Backup automático criado:",
            file=discord.File(backup_nome)
        )

    # Manter apenas os últimos 5
    backups = sorted(os.listdir(BACKUP_FOLDER))
    if len(backups) > MAX_BACKUPS:
        os.remove(os.path.join(BACKUP_FOLDER, backups[0]))

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

async def save_data(data):
    await criar_backup()  # 🔥 cria backup antes de salvar
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# 🔹 ADICIONAR ITEM
@bot.command()
async def add(ctx, item: str, quantidade: int):
    user = ctx.author.name
    data = load_data()

    item = item.lower()

    if item not in data:
        data[item] = {}

    if user not in data[item]:
        data[item][user] = 0

    data[item][user] += quantidade

    await save_data(data)

    await ctx.send(f"✅ {quantidade} adicionados em {item}")

# 🔹 RETIRAR ITEM
@bot.command()
async def retirar(ctx, item: str, quantidade: int):
    user = ctx.author.name
    data = load_data()

    item = item.lower()

    if item not in data or user not in data[item]:
        await ctx.send("❌ Você não possui esse item registrado.")
        return

    if data[item][user] < quantidade:
        await ctx.send("❌ Você não tem essa quantidade para retirar.")
        return

    data[item][user] -= quantidade

    if data[item][user] == 0:
        del data[item][user]

    if not data[item]:
        del data[item]

    await save_data(data)

    await ctx.send(f"➖ {quantidade} retirados de {item}")

# 🔹 MOSTRAR TABELA BONITA
@bot.command()
async def tabela(ctx):
    data = load_data()

    if not data:
        await ctx.send("📭 Nenhum dado registrado ainda.")
        return

    mensagem = ""

    for item in data:
        users = data[item]
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
    await criar_backup()
    await save_data({})
    await ctx.send("🗑️ Todos os dados foram resetados com sucesso!")

bot.run(os.getenv("TOKEN"))
