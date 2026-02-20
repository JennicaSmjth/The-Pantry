import discord
from discord import ui, app_commands
from discord.ext import commands

# --- EDIT THESE THREE THINGS ONLY ---
MY_USER_ID = YOUR_USER_ID  
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Add or remove food here! Just follow the pattern.
FOOD_MENU = [
    {"name": "Burger", "emoji": "🍔", "desc": "Classic beef burger"},
    {"name": "Pizza", "emoji": "🍕", "desc": "Pepperoni slice"},
    {"name": "Taco", "emoji": "🌮", "desc": "Soft shell beef taco"},
    {"name": "Nuggets", "emoji": "🍗", "desc": "6pc Chicken nuggets"}
]

# ---------------------------------------------------------
# DON'T WORRY ABOUT THE CODE BELOW - IT JUST WORKS!
# ---------------------------------------------------------

class TicketModal(ui.Modal):
    def __init__(self, food_choice):
        # The title changes based on what you picked in the dropdown
        super().__init__(title=f"Ordering: {food_choice}")
        self.food_choice = food_choice

    # Your two specific popup questions
    where_eat = ui.TextInput(label="Where do you eat? Clean it up!", placeholder="e.g. Cafeteria", required=True)
    special_steps = ui.TextInput(label="Any special order steps?", placeholder="Optional...", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        # This builds the summary that gets sent to YOUR DMs
        embed = discord.Embed(title="🍔 New Order Received", color=discord.Color.gold())
        embed.add_field(name="Item", value=self.food_choice, inline=True)
        embed.add_field(name="User", value=interaction.user.mention, inline=True)
        embed.add_field(name="Location", value=self.where_eat.value, inline=False)
        embed.add_field(name="Special Steps", value=self.special_steps.value or "None", inline=False)
        
        try:
            user = await interaction.client.fetch_user(MY_USER_ID)
            await user.send(embed=embed)
            await interaction.response.send_message(f"Order for {self.food_choice} sent!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error sending DM to owner: {e}", ephemeral=True)

class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Build the dropdown from the FOOD_MENU list at the top
        select = ui.Select(placeholder="Pick your lunch! 🍕")
        for item in FOOD_MENU:
            select.add_option(label=item["name"], value=item["name"], emoji=item["emoji"], description=item["desc"])
        
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        food = interaction.data['values'][0]
        # This opens the popup after you pick a food item
        await interaction.response.send_modal(TicketModal(food))

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True # Needed to find your User ID
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Syncs commands with Discord on startup
        await self.tree.sync()
        print("Bot is online and commands are synced!")

bot = MyBot()

@bot.tree.command(name="update", description="Syncs the latest food menu and commands")
async def update(interaction: discord.Interaction):
    if interaction.user.id != MY_USER_ID:
        return await interaction.response.send_message("❌ Only the owner can use this.", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    try:
        await bot.tree.sync()
        await interaction.followup.send("✅ **Sync Complete!** Latest menu is ready.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ **Sync Error:** {e}", ephemeral=True)

@bot.tree.command(name="setup", description="Sends the ticket selection menu")
async def setup(interaction: discord.Interaction):
    # Posts the dropdown menu in the channel
    await interaction.response.send_message("### 🛠️ Order Center\nSelect an option below to start your order.", view=TicketView())

bot.run(BOT_TOKEN)
