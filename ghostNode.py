import discord
from discord.ext import commands
from discord.ui import View, Select

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# LINK de pagamento do Mercado Pago (já pronto)
MERCADO_PAGO_LINK = "https://mpago.la/11LidBF"

# Nome da categoria onde os tickets vão ser criados
CATEGORY_NAME = "🎫 Tickets"
# Nome da role da equipe de suporte
STAFF_ROLE_NAME = "ADMs"

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🧾 Comprar Acesso", value="compra", description="Comprar acesso ao servidor GhostNode"),
            discord.SelectOption(label="🆘 Suporte", value="suporte", description="Falar com a equipe de suporte"),
        ]
        super().__init__(placeholder="Selecione uma opção...", options=options, custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        # Verifica se a categoria existe ou cria
        categoria = discord.utils.get(guild.categories, name=CATEGORY_NAME)
        if categoria is None:
            categoria = await guild.create_category(CATEGORY_NAME)

        # Role da equipe de suporte
        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)

        # Criar o canal
        canal_nome = f"{self.values[0]}-{user.name}"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        canal = await guild.create_text_channel(
            name=canal_nome,
            category=categoria,
            overwrites=overwrites
        )

        if self.values[0] == "compra":
            await canal.send(
                f"Olá {user.mention}, para acessar o servidor **GhostNode**, realize o pagamento no link abaixo:\n\n"
                f"👉 {MERCADO_PAGO_LINK} \n\n"
                "Assim que o pagamento for aprovado, o acesso será liberado automaticamente pelo próprio link!"
            )
        elif self.values[0] == "suporte":
            await canal.send(
                f"{user.mention}, este é seu canal de suporte. A equipe vai te responder em breve!"
            )

        await interaction.response.send_message(f"✅ Ticket criado: {canal.mention}", ephemeral=True)

@bot.command()
async def ticket(ctx):
    embed = discord.Embed(
        title="🎟️ Central de Tickets - Systems_BSI",
        description="Selecione abaixo o motivo do seu ticket:",
        color=discord.Color.blue()
    )
    embed.set_image(url="https://imgur.com/a/5YPzcOU")

    await ctx.send(embed=embed, view=TicketView())

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    
    # 🧠 Adiciona a view global para funcionar corretamente com menus suspensos
    bot.add_view(TicketView())

    # 🔁 ENVIA AUTOMATICAMENTE A MENSAGEM COM O MENU AO INICIAR
    canal_id = 1368291167854133358  # ⬅️ coloque aqui o ID do canal desejado

    canal = bot.get_channel(canal_id)
    if canal:
        embed = discord.Embed(
            title="🎟️ Central de Tickets - Systems_BSI",
            description="Selecione abaixo o motivo do seu ticket:",
            color=discord.Color.blue()
        )
        embed.set_image(url="https://i.imgur.com/qKHxZL2.png")  # personalize se quiser

        await canal.send(embed=embed, view=TicketView())
    else:
        print("❌ Canal não encontrado. Verifique o ID.")
        
import os
bot.run(os.getenv("TOKEN"))