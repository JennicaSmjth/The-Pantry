import discord
from discord import ui, app_commands
from discord.ext import commands
from datetime import datetime

# --- EDIT THESE TWO THINGS ONLY ---
MY_USER_ID = YOUR_USERID # Theres no need for adding quote marks  
BOT_TOKEN = 'YOUR_BOT_TOKEN' 

# --- FOOD MENU ---
FOOD_MENU = [
    {"name": "Fried Rice", "emoji": "🍚", "desc": "Price: 15,000 Kyat"},
    {"name": "Steak", "emoji": "🥩", "desc": "Price: 25,000 Kyat"},
    {"name": "Burger", "emoji": "🍔", "desc": "Price: 20,000 Kyat"}, # <---- Add a comma after each line (Each line is a new menu item in the drop down)
    {"name": "KFC", "emoji": "🍗", "desc": "Price: 20,000 Kyat"} # <---- For the last one don't add a comma
]

class ConfirmPayView(ui.View):
    def __init__(self, modal_data, user, time, owner_name):
        super().__init__(timeout=60)
        self.modal_data = modal_data
        self.user = user
        self.time = time
        self.owner_name = owner_name

    @ui.button(label="I promise to pay", style=discord.ButtonStyle.green, emoji="🤝")
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(title="📝 New Order Confirmed", color=discord.Color.green())
        embed.add_field(name="Customer", value=self.modal_data.customer_name.value, inline=True)
        embed.add_field(name="User", value=self.user.mention, inline=True)
        embed.add_field(name="Item", value=f"{self.modal_data.quantity.value}x {self.modal_data.food_choice}", inline=False)
        embed.add_field(name="Location", value=self.modal_data.where_eat.value, inline=False)
        
        if self.modal_data.special_steps.value:
            embed.add_field(name="Notes", value=self.modal_data.special_steps.value, inline=False)
        
        embed.set_footer(text=f"Time: {self.time}")

        admin = await interaction.client.fetch_user(MY_USER_ID)
        await admin.send(embed=embed)
        
        # FIXED: Uses f-string and the owner_name we passed in
        await interaction.followup.send(f"✅ Order sent! Meetup with {self.owner_name} and confirm payment!", ephemeral=True)

class TicketModal(ui.Modal):
    def __init__(self, food_choice, owner_name):
        super().__init__(title=f"Order: {food_choice}")
        self.food_choice = food_choice
        self.owner_name = owner_name

    customer_name = ui.TextInput(label="Your Name", placeholder="Who is this for?", required=True)
    quantity = ui.TextInput(label="Quantity", placeholder="How many?", min_length=1, max_length=2, required=True)
    where_eat = ui.TextInput(label="Where are you?", placeholder="e.g. Cafeteria, Mr, Andy's Room", required=True)
    special_steps = ui.TextInput(label="Extra info?", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        now = datetime.now().strftime("%I:%M %p")
        # We pass the owner name down to the final button view
        view = ConfirmPayView(self, interaction.user, now, self.owner_name)
        await interaction.followup.send(f"You're ordering **{self.quantity.value}x {self.food_choice}**. Confirm below!", view=view, ephemeral=True)

class TicketView(ui.View):
    def __init__(self, owner_name):
        super().__init__(timeout=None)
        self.owner_name = owner_name
        select = ui.Select(placeholder="🍱 Select your food...")
        for item in FOOD_MENU:
            select.add_option(label=item["name"], value=item["name"], emoji=item["emoji"], description=item["desc"])
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketModal(interaction.data['values'][0], self.owner_name))

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Logged in as {self.user}")

bot = MyBot()

@bot.tree.command(name="setup", description="Open the pantry menu")
async def setup(interaction: discord.Interaction):
    if interaction.user.id != MY_USER_ID:
        return await interaction.response.send_message("❌ Admin only.", ephemeral=True)

    # CHECK FOR DUPLICATE MENU
    async for message in interaction.channel.history(limit=50):
        if message.author == interaction.client.user and message.embeds:
            if "The Pantry | Order Here" in message.embeds[0].title:
                return await interaction.response.send_message("⚠️ Nah, there's already an active menu here!", ephemeral=True)

    owner = await interaction.client.fetch_user(MY_USER_ID)
    embed = discord.Embed(
        title="🥪 The Pantry | Order Here", 
        description="Pick what you'd like from the menu below. After you fill out the details, click confirm to place your order!", 
        color=discord.Color.blue()
    )
    # CLEAN FOOTER: No ID numbers, just your name
    embed.set_footer(text=f"System Managed by {owner.name}")
    await interaction.response.send_message(embed=embed, view=TicketView(owner.name))

bot.run(BOT_TOKEN)
