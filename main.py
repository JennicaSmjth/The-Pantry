import discord
from discord import ui, app_commands
from discord.ext import commands
from datetime import datetime

# --- EDIT THESE TWO THINGS ONLY ---
MY_USER_ID = USER_ID  # <---- Put your User ID here (Numbers only, no quotes)
BOT_TOKEN = 'YOUR_NEW_TOKEN'    # <---- Put your Bot Token here (Must keep the 'quotes')

# --- FOOD MENU (Edit items here) ---
# 1. Every line needs a comma at the end EXCEPT the very last one.
# 2. Use "name" for the food, "emoji" for the icon, and "desc" for the price.
FOOD_MENU = [
    {"name": "Fried Rice", "emoji": "🍚", "desc": "15,000 Kyat"},
    {"name": "Steak", "emoji": "🥩", "desc": "25,000 Kyat"},
    {"name": "Burger", "emoji": "🍔", "desc": "20,000 Kyat"},
    {"name": "KFC", "emoji": "🍗", "desc": "20,000 Kyat"} # <---- Last item has no comma
]

# --- SPAM PREVENTION ---
# This stops users from clicking 'Submit' more than once every 5 seconds.
order_cooldown = commands.CooldownMapping.from_cooldown(1, 5.0, commands.BucketType.user)

class ConfirmPayView(ui.View):
    """The 'I Promise to Pay' Button (Your Checkbox)"""
    def __init__(self, modal_data, user, time):
        super().__init__(timeout=60)
        self.modal_data = modal_data
        self.user = user
        self.time = time

    @ui.button(label="I promise to pay", style=discord.ButtonStyle.green, emoji="🤝")
    async def confirm(self, interaction: discord.Interaction):
        # This builds the final receipt that gets sent to your DMs
        embed = discord.Embed(title="💰 NEW CONFIRMED ORDER", color=discord.Color.green())
        embed.add_field(name="Customer Name", value=self.modal_data.customer_name.value, inline=True)
        embed.add_field(name="Discord User", value=self.user.mention, inline=True)
        embed.add_field(name="Order", value=f"{self.modal_data.quantity.value}x {self.modal_data.food_choice}", inline=False)
        embed.add_field(name="Location", value=self.modal_data.where_eat.value, inline=False)
        embed.add_field(name="Special Steps", value=self.modal_data.special_steps.value or "None", inline=False)
        embed.set_footer(text=f"Confirmed at: {self.time}")

        admin = await interaction.client.fetch_user(MY_USER_ID)
        await admin.send(embed=embed)
        
        # This removes the button so they can't click it twice
        await interaction.response.edit_message(content="✅ Order sent to the kitchen!", view=None)

class TicketModal(ui.Modal):
    """The Popup Form"""
    def __init__(self, food_choice):
        super().__init__(title=f"Order: {food_choice}")
        self.food_choice = food_choice

    customer_name = ui.TextInput(label="Your Name", placeholder="Enter your real name", required=True)
    quantity = ui.TextInput(label="Quantity", placeholder="How many portions?", min_length=1, max_length=2, required=True)
    where_eat = ui.TextInput(label="Where do you eat?", placeholder="e.g. Table 4, Cafeteria", required=True)
    special_steps = ui.TextInput(label="Special Steps", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        # Check if the user is spamming
        retry_after = order_cooldown.update_rate_limit(interaction)
        if retry_after:
            return await interaction.response.send_message(f"⚠️ Slow down! Wait {round(retry_after, 1)}s.", ephemeral=True)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        view = ConfirmPayView(self, interaction.user, now)
        await interaction.response.send_message("Please confirm your order below to complete the process.", view=view, ephemeral=True)

class TicketView(ui.View):
    """The Dropdown Menu"""
    def __init__(self):
        super().__init__(timeout=None)
        select = ui.Select(placeholder="Pick your lunch! 🍕")
        for item in FOOD_MENU:
            select.add_option(label=item["name"], value=item["name"], emoji=item["emoji"], description=item["desc"])
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        # Opens the modal when they pick an item
        await interaction.response.send_modal(TicketModal(interaction.data['values'][0]))

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Logged in as {self.user}")

bot = MyBot()

@bot.tree.command(name="setup", description="Spawn the Order Center")
async def setup(interaction: discord.Interaction):
    # Only the owner or an Admin can run this
    if not (interaction.user.id == MY_USER_ID or interaction.user.guild_permissions.administrator):
        return await interaction.response.send_message("❌ Admin only.", ephemeral=True)

    embed = discord.Embed(
        title="🍱 Order Center", 
        description="Select your food from the menu below and confirm your order.", 
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"System Managed by {interaction.user.name}")
    await interaction.response.send_message(embed=embed, view=TicketView())

bot.run(BOT_TOKEN)
