import discord
from discord import ui, app_commands
from discord.ext import commands
from datetime import datetime # Added this for the date

# --- EDIT THESE THREE THINGS ONLY ---
MY_USER_ID = YOUR_USER_ID  
BOT_TOKEN = 'YOUR_BOT_TOKEN'

FOOD_MENU = [
    {"name": "Fried Rice", "emoji": "🍚", "desc": "15,000 Kyat"},
    {"name": "Steak", "emoji": "🥩", "desc": "25,000 Kyat"},
    {"name": "Burger", "emoji": "🍔", "desc": "20,000 Kyat"}, # <---- After each line there's a comma
    {"name": "KFC", "emoji": "🍗", "desc": "20,000 Kyat"} # <---- Last no comma
]

# ---------------------------------------------------------
# BOT LOGIC
# ---------------------------------------------------------

class TicketModal(ui.Modal):
    def __init__(self, food_choice):
        super().__init__(title=f"Ordering: {food_choice}")
        self.food_choice = food_choice

    where_eat = ui.TextInput(label="Where do you eat?", placeholder="e.g. Cafeteria", required=True)
    special_steps = ui.TextInput(label="Any special order steps?", placeholder="Optional...", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        # Grabs the current time when they hit "Submit"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        embed = discord.Embed(title="🍔 New Order Received", color=discord.Color.gold())
        embed.add_field(name="Item", value=self.food_choice, inline=True)
        embed.add_field(name="User", value=interaction.user.mention, inline=True)
        embed.add_field(name="Location", value=self.where_eat.value, inline=False)
        embed.add_field(name="Special Steps", value=self.special_steps.value or "None", inline=False)
        embed.set_footer(text=f"Order Time: {now}") # <--- Date added here!
        
        user = await interaction.client.fetch_user(MY_USER_ID)
        await user.send(embed=embed)
        await interaction.response.send_message(f"Order for {self.food_choice} sent!", ephemeral=True)

class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        select = ui.Select(placeholder="Pick your lunch! 🍕")
        for item in FOOD_MENU:
            select.add_option(label=item["name"], value=item["name"], emoji=item["emoji"], description=item["desc"])
        
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        food = interaction.data['values'][0]
        await interaction.response.send_modal(TicketModal(food))

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Bot is online!")

bot = MyBot()

@bot.tree.command(name="setup", description="Sends the ticket selection menu")
async def setup(interaction: discord.Interaction):
    if not (interaction.user.id == MY_USER_ID or interaction.user.guild_permissions.administrator):
        return await interaction.response.send_message("❌ No permission.", ephemeral=True)

    embed = discord.Embed(
        title="⚒️ Order Center", 
        description="Select an option below to start your order.", 
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"System Managed by {interaction.user.name}")

    await interaction.response.send_message(embed=embed, view=TicketView())

bot.run(BOT_TOKEN)
