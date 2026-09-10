import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 時間選項
TIME_OPTIONS = [
    discord.SelectOption(label="上午 (08:00-12:00)", value="morning"),
    discord.SelectOption(label="下午 (12:00-17:00)", value="afternoon"),
    discord.SelectOption(label="晚上 (17:00-23:00)", value="evening"),
    discord.SelectOption(label="不確定", value="uncertain"),
]

# 武學選項
MARTIAL_ARTS = [
    discord.SelectOption(label="劍法", value="sword"),
    discord.SelectOption(label="刀法", value="blade"),
    discord.SelectOption(label="拳法", value="fist"),
    discord.SelectOption(label="掌法", value="palm"),
    discord.SelectOption(label="指法", value="finger"),
    discord.SelectOption(label="其他", value="other"),
]

class TimeSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="選擇能參加的時間",
            min_values=1,
            max_values=3,
            options=TIME_OPTIONS
        )
    
    async def callback(self, interaction: discord.Interaction):
        times = {
            "morning": "上午",
            "afternoon": "下午",
            "evening": "晚上",
            "uncertain": "不確定"
        }
        selected_times = ", ".join([times[v] for v in self.values])
        await interaction.response.defer()

class MartialArtsSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="選擇使用的武學",
            min_values=1,
            max_values=1,
            options=MARTIAL_ARTS
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

class BaiyeForm(discord.ui.Modal):
    game_id = discord.ui.TextInput(
        label="遊戲 ID",
        placeholder="請輸入您的遊戲 ID",
        required=True,
        min_length=1,
        max_length=50
    )
    
    martial_art = discord.ui.TextInput(
        label="武學",
        placeholder="例如：劍法、刀法等",
        required=True,
        min_length=1,
        max_length=30
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✅ 百業戰參與者信息",
            color=discord.Color.green(),
            description="感謝您的填寫！"
        )
        embed.add_field(name="遊戲 ID", value=self.game_id.value, inline=False)
        embed.add_field(name="武學", value=self.martial_art.value, inline=False)
        embed.add_field(name="用戶", value=f"{interaction.user.mention}", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # 發送到指定頻道（如果有）
        channel_id = os.getenv('LOG_CHANNEL_ID')
        if channel_id:
            channel = bot.get_channel(int(channel_id))
            if channel:
                await channel.send(embed=embed)

class TimeSelectView(discord.ui.View):
    def __init__(self, game_id: str, martial_art: str):
        super().__init__()
        self.game_id = game_id
        self.martial_art = martial_art
        self.add_item(TimeSelect())
    
    async def on_submit(self, interaction: discord.Interaction):
        times = {
            "morning": "上午",
            "afternoon": "下午",
            "evening": "晚上",
            "uncertain": "不確定"
        }
        selected_times = ", ".join([times[v] for v in self.children[0].values])
        
        embed = discord.Embed(
            title="✅ 百業戰參與者信息",
            color=discord.Color.green(),
            description="感謝您的填寫！"
        )
        embed.add_field(name="遊戲 ID", value=self.game_id, inline=False)
        embed.add_field(name="武學", value=self.martial_art, inline=False)
        embed.add_field(name="可參加時間", value=selected_times, inline=False)
        embed.add_field(name="用戶", value=f"{interaction.user.mention}", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # 發送到指定頻道（如果有）
        channel_id = os.getenv('LOG_CHANNEL_ID')
        if channel_id:
            channel = bot.get_channel(int(channel_id))
            if channel:
                await channel.send(embed=embed)

class SimpleForm(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label="填寫百業戰參與信息", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BaiyeForm(title="百業戰參與者信息表")
        await interaction.response.send_modal(modal)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="baiye_war", description="詢問群友是否參加百業戰")
async def baiye_war(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚔️ 百業戰參與者招募",
        color=discord.Color.gold(),
        description="點擊下方按鈕填寫您的參與信息"
    )
    embed.add_field(
        name="需要填寫以下信息：",
        value="• 遊戲 ID\n• 使用武學\n• 可參加時間",
        inline=False
    )
    
    view = SimpleForm()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="baiye_list", description="查看百業戰參與者列表")
async def baiye_list(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📋 百業戰參與者列表",
        color=discord.Color.blue(),
        description="此功能需要與後端資料庫連接"
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Run the bot
bot.run(TOKEN)