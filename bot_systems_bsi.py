import discord
from discord.ext import commands
from discord.ui import View, Button
import json
import os
from dotenv import load_dotenv

# Carrega as variáveis do .env (funciona localmente, ignorado no Railway)
load_dotenv()

# Valida a variável de ambiente
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ A variável de ambiente 'TOKEN' não está definida!")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Links dos planos
LINK_MENSAL = "https://pay.kirvano.com/2bf6b08a-c55f-4859-9638-b73bb8402156"
LINK_VITALICIO = "https://pay.kirvano.com/028fb6ed-615b-4c8c-894d-17219dc417aa"

# Configurações de categoria e equipe
CATEGORY_NAME = "━━━━━━❰･ᴀᴛᴇɴᴅɪᴍᴇɴᴛᴏ･❱━━━━━"
STAFF_ROLE_NAME = "ADMs"
CODIGOS_FILE = "codigos_100k.json"

class PlanoView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="🧾 Plano Mensal", style=discord.ButtonStyle.primary, custom_id="comprar_mensal"))
        self.add_item(Button(label="💎 Plano Vitalício", style=discord.ButtonStyle.success, custom_id="comprar_vitalicio"))
        self.add_item(Button(label="🆘 Suporte", style=discord.ButtonStyle.secondary, custom_id="suporte"))

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    bot.add_view(PlanoView())

    canal = bot.get_channel(1368291167854133358)
    if canal:
        embed = discord.Embed(
            title="🎟️ Central de Acesso - Systems_BSI",
            description="Escolha seu plano ou peça suporte:",
            color=discord.Color.blue()
        )
        embed.set_image(url="https://i.imgur.com/opzZdBF.jpeg")
        await canal.send(embed=embed, view=PlanoView())

@bot.event
async def on_interaction(interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user

    categoria = discord.utils.get(guild.categories, name=CATEGORY_NAME)
    if not categoria:
        categoria = await guild.create_category(CATEGORY_NAME)

    staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    custom_id = interaction.data["custom_id"]

    if custom_id == "suporte":
        canal = await guild.create_text_channel(f"suporte-{user.name}", category=categoria, overwrites=overwrites)
        await canal.send(f"{user.mention}, este é seu canal de suporte. A equipe irá te responder em breve.")
        await interaction.response.send_message(f"✅ Canal de suporte criado: {canal.mention}", ephemeral=True)
        return

    if custom_id in ["comprar_mensal", "comprar_vitalicio"]:
        tipo = "mensal" if custom_id == "comprar_mensal" else "vitalicio"
        link = LINK_MENSAL if tipo == "mensal" else LINK_VITALICIO

        try:
            with open(CODIGOS_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            await interaction.response.send_message("❌ O arquivo de códigos não foi encontrado.", ephemeral=True)
            return

        if not data.get(tipo):
            await interaction.response.send_message("❌ Nenhum código disponível no momento. Contate o suporte.", ephemeral=True)
            return

        codigo = data[tipo].pop(0)
        with open(CODIGOS_FILE, "w") as f:
            json.dump(data, f, indent=2)

        canal = await guild.create_text_channel(f"{tipo}-{user.name}", category=categoria, overwrites=overwrites)
        await canal.send(
            f"👋 Olá {user.mention}!\n\n"
            f"Para acessar o servidor **GhostNode**, realize o pagamento no link abaixo:\n"
            f"👉 {link}\n\n"
            f"Após o pagamento, use este código no servidor GhostNode para liberar o acesso:\n"
            f"🔐 Código: `{codigo}`"
        )
        await interaction.response.send_message(f"✅ Ticket criado com código de acesso: {canal.mention}", ephemeral=True)

@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="🎟️ Central de Acesso - Systems_BSI",
        description="Escolha seu plano ou peça suporte:",
        color=discord.Color.blue()
    )
    embed.set_image(url="https://i.imgur.com/opzZdBF.jpeg")
    await ctx.send(embed=embed, view=PlanoView())

bot.run(TOKEN)
print("🔍 Variáveis disponíveis:", dict(os.environ))
print("📦 TOKEN:", os.getenv("TOKEN"))
print("🔍 Railway detectou:", list(os.environ.keys()))