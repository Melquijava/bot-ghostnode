import discord
from discord.ext import commands
from discord.ui import View, Button
import os
import asyncio
from dotenv import load_dotenv

# Carrega as variáveis do .env
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

# Link do plano vitalício
LINK_VITALICIO = "https://systems-bsi.pay.yampi.com.br/r/9FPOES8JNZ"

# Configurações de categoria e equipe
CATEGORY_NAME = "⇓━━━━━━━━  Atendimento ━━━━━━━━⇓"
STAFF_ROLE_NAME = "ADMs"
CANAL_ENVIO_COMPROVANTE = "📥│envio-comprovante"

class PlanoView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="💎 Plano Vitalício", style=discord.ButtonStyle.success, custom_id="comprar_vitalicio"))
        self.add_item(Button(label="🆘 Suporte", style=discord.ButtonStyle.secondary, custom_id="suporte"))

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    bot.add_view(PlanoView())

    canal = bot.get_channel(1368291167854133358)
    if canal:
        embed = discord.Embed(
            title="🎟️ Central de Acesso - GhostNode",
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
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    custom_id = interaction.data["custom_id"]

    if custom_id == "suporte":
        nome_canal = f"suporte-{user.name}".replace(" ", "-").lower()
        canal_existente = discord.utils.get(guild.text_channels, name=nome_canal)

        if canal_existente:
            await interaction.response.send_message(f"⚠️ Você já possui um canal de suporte aberto: {canal_existente.mention}", ephemeral=True)
            return

        canal = await guild.create_text_channel(nome_canal, category=categoria, overwrites=overwrites)
        await canal.send(f"{user.mention}, este é seu canal de suporte. A equipe irá te responder em breve.")
        await interaction.response.send_message(f"✅ Canal de suporte criado: {canal.mention}", ephemeral=True)
        return

    if custom_id == "comprar_vitalicio":
        nome_canal = f"vitalicio-{user.name}".replace(" ", "-").lower()
        canal_existente = discord.utils.get(guild.text_channels, name=nome_canal)

        if canal_existente:
            await interaction.response.send_message(f"⚠️ Você já possui um ticket aberto: {canal_existente.mention}", ephemeral=True)
            return

        canal = await guild.create_text_channel(nome_canal, category=categoria, overwrites=overwrites)
        await asyncio.sleep(1)

        comprovante_canal = discord.utils.get(guild.text_channels, name=CANAL_ENVIO_COMPROVANTE)
        canal_mencionado = comprovante_canal.mention if comprovante_canal else "📥│envio-comprovante"

        embed = discord.Embed(
            title="🛒 Etapas para Concluir sua Compra",
            description=(
                f"👋 Olá {user.mention}!\n\n"
                f"💳 **Realize o pagamento no link abaixo:**\n👉 {LINK_VITALICIO}\n\n"
                f"📨 Após o pagamento, envie o comprovante no canal {canal_mencionado} para liberação do acesso."
            ),
            color=discord.Color.green()
        )
        embed.set_thumbnail(url="https://i.imgur.com/opzZdBF.jpeg")

        await canal.send(f"{user.mention}", embed=embed)
        await interaction.response.send_message(f"✅ Ticket criado: {canal.mention}", ephemeral=True)

@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="🎟️ Central de Acesso - GhostNode",
        description="Escolha seu plano ou peça suporte:",
        color=discord.Color.blue()
    )
    embed.set_image(url="https://i.imgur.com/opzZdBF.jpeg")
    await ctx.send(embed=embed, view=PlanoView())

bot.run(TOKEN)
print("🔍 Variáveis disponíveis:", dict(os.environ))
print("📦 TOKEN:", os.getenv("TOKEN"))
print("🔍 Railway detectou:", list(os.environ.keys()))