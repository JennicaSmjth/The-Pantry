import discord
from discord import ui, app_commands
from discord.ext import commands

# --- CONFIGURATION ---
MY_USER_ID = 896389113576562749  
BOT_TOKEN = 'MTQ3NDM2NDE3MTg0Njk0Njg1Ng.GicMHf.iLYcwjLgkcHOUAWQW7PNRSQbH5VO0cnmkOK8gk'

class TicketModal(ui.Modal, title='Order Details'):
    # Question 1
    where_eat = ui.TextInput(
        label="Where do you eat? Clean it up!", 
        placeholder="e.g. The cafeteria, outside, etc.",
        style=discord.TextStyle.short,
        required=True
    )
    
    # Question 2 (Optional)
    special_steps = ui.TextInput(
        label="Any special order steps?", 
        placeholder="Optional steps for your order...",
        style=discord.TextStyle.paragraph,
        required=False 
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Create the Embed for your DM
        embed = discord.Embed(
            title="🍔 New Order Received",
            color=discord.Color.gold(),
            description=f"**From:** {interaction.user.mention} ({interaction.user.name})"
        )
        embed.add_field(name="Location", value=self.where_eat.value, inline=False)
        embed.add_field(name="Special Steps", value=self.special_steps.value or "None provided", inline=False)
        
        try:
            # Fetches you by ID and sends the DM
            target_user = await interaction.client.fetch_user(MY_USER_ID)
            await target_user.send(embed=embed)
            await interaction.response.send_message("Order sent! I'll look it over shortly.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Could not send DM to owner. Error: {e}", ephemeral=True)

class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.select(
        placeholder="Open me to get a Ticket!",
        options=[
            discord.SelectOption(label="Place Order", description="Tell us where you're eating", emoji="🍴"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select):
        await interaction.response.send_modal(TicketModal())

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True # Needed to fetch your user ID
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced successfully!")

bot = MyBot()

@bot.tree.command(name="setup", description="Sends the ticket selection menu")
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message("### 🛠️ Order Center\nSelect an option below to start your order.", view=TicketView())

bot.run(BOT_TOKEN)
