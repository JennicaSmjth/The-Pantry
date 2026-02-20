import discord
from discord import ui
from discord.ext import commands

# 1. THE POPUP (MODAL)
class TicketModal(ui.Modal, title='Please fill this out'):
    # These match your screenshot fields
    whats_up = ui.TextInput(
        label="What's up", 
        style=discord.TextStyle.paragraph,
        placeholder="So what's the problem",
        required=True
    )
    it_help = ui.TextInput(
        label="Could IT at school have helped you?", 
        placeholder="Yes or No",
        max_length=3,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        # This is the Embed that gets sent after they hit Submit
        embed = discord.Embed(
            title="🎫 New Ticket Submitted",
            color=discord.Color.green(),
            description=f"**User:** {interaction.user.mention}\n**ID:** {interaction.user.id}"
        )
        embed.add_field(name="Issue Description", value=self.whats_up.value, inline=False)
        embed.add_field(name="Could IT Help?", value=self.it_help.value, inline=False)
        embed.set_footer(text="Ticket System • [PLACEHOLDER]")

        # Sends a private confirmation to the user
        await interaction.response.send_message(embed=embed, ephemeral=True)

# 2. THE DROPDOWN (VIEW)
class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Keeps the buttons working forever

    @ui.select(
        placeholder="Open me to get a Ticket!",
        options=[
            discord.SelectOption(label="General Support", description="Need help with something?", emoji="🎫"),
            discord.SelectOption(label="Report Player", description="Someone being mean?", emoji="🚩"),
        ]
    )
    async def select_callback(self, interaction, select):
        # This opens the popup immediately when they click an option
        await interaction.response.send_modal(TicketModal())

# 3. THE BOT SETUP
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def setup_tickets(ctx):
    """Run !setup_tickets to send the dropdown message"""
    await ctx.send("### 🛠️ Support Center\nNeed help? Use the menu below to open a ticket.", view=TicketView())

# PASTE YOUR TOKEN BELOW
bot.run('YOUR_BOT_TOKEN_HERE')
