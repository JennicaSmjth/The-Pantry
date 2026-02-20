import discord
from discord import ui, app_commands
from discord.ext import commands

# --- EDIT THESE THREE THINGS ONLY ---
MY_USER_ID = YOUR_USER_ID  # <---- The persom will recieve the orders in DM but admins can use the commands
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Add or remove food here! Just follow the pattern.
FOOD_MENU = [
    {"name": "Burger", "emoji": "🍔", "desc": "Classic beef burger"},
    {"name": "Pizza", "emoji": "🍕", "desc": "Pepperoni slice"},
    {"name": "Taco", "emoji": "🌮", "desc": "Soft shell beef taco"}, # <---- Add comma after each
    {"name": "Nuggets", "emoji": "🍗", "desc": "6pc Chicken nuggets"} # <---- Last one has no comma
]

# ---------------------------------------------------------
# DON'T WORRY ABOUT THE CODE BELOW - IT JUST WORKS!
# ---------------------------------------------------------

class TicketModal(ui.Modal):
    def __init__(self, food_choice):
        super().__init__(title=f"Ordering: {food_choice}")
        self.food_choice = food_choice

    # Text inputs for the popup
    where_eat = ui.TextInput(label="Where do you eat? Clean it up!", placeholder="e.g. Cafeteria", required=True)
    special_steps = ui.TextInput(label="Any special order steps?", placeholder="Optional...", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        # Format the order summary to send to your DMs
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
        
        # Build the dropdown menu from the FOOD_MENU list
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
        print("Bot is online and commands are synced!")

bot = MyBot()

# Function to check for Owner OR Administrator
def is_owner_or_admin():
    async def predicate(interaction: discord.Interaction):
        is_owner = interaction.user.id == MY_USER_ID
        is_admin = interaction.user.guild_permissions.administrator
        if is_owner or is_admin:
            return True
        await interaction.response.send_message("❌ Only the Bot Owner or an Administrator can use this.", ephemeral=True)
        return False
    return app_commands.check(predicate)

@bot.tree.command(name="update", description="Syncs the latest food menu and commands")
@is_owner_or_admin()
async def update(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        await bot.tree.sync()
        await interaction.followup.send("✅ **Sync Complete!** Latest menu and permissions updated.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ **Sync Error:** {e}", ephemeral=True)

@bot.tree.command(name="setup", description="Sends the ticket selection menu")
@is_owner_or_admin()
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message("### 🛠️ Order Center\nSelect an option below to start your order!", view=TicketView())

bot.run(BOT_TOKEN)
