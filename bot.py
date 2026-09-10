import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from pathlib import Path

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 數據文件路徑
DATA_FILE = "participants.json"

# Create bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 時間選項 - 具體賽事時間
TIME_OPTIONS = [
    discord.SelectOption(label="周六 20:30 (聯賽)", value="sat_20_30_league"),
    discord.SelectOption(label="周六 21:15 (配對賽 1)", value="sat_21_15_pair1"),
    discord.SelectOption(label="周六 22:15 (配對賽 2)", value="sat_22_15_pair2"),
    discord.SelectOption(label="周日 20:30 (聯賽)", value="sun_20_30_league"),
    discord.SelectOption(label="周日 21:15 (配對賽 1)", value="sun_21_15_pair1"),
    discord.SelectOption(label="周日 22:15 (配對賽 2)", value="sun_22_15_pair2"),
]

# 時間映射
TIME_MAPPING = {
    "sat_20_30_league": "周六 20:30 (聯賽)",
    "sat_21_15_pair1": "周六 21:15 (配對賽 1)",
    "sat_22_15_pair2": "周六 22:15 (配對賽 2)",
    "sun_20_30_league": "周日 20:30 (聯賽)",
    "sun_21_15_pair1": "周日 21:15 (配對賽 1)",
    "sun_22_15_pair2": "周日 22:15 (配對賽 2)",
}

# 時間順序
TIME_ORDER = [
    "sat_20_30_league",
    "sat_21_15_pair1",
    "sat_22_15_pair2",
    "sun_20_30_league",
    "sun_21_15_pair1",
    "sun_22_15_pair2",
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

# ==================== 數據管理函數 ====================

def load_participants():
    """讀取參與者數據"""
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_participants(data):
    """保存參與者數據"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_participant(user_id: str, user_name: str, game_id: str, martial_art: str, times: list):
    """添加參與者"""
    data = load_participants()
    data[user_id] = {
        "user_name": user_name,
        "game_id": game_id,
        "martial_art": martial_art,
        "times": times,
        "timestamp": datetime.now().isoformat()
    }
    save_participants(data)

def get_participants_by_time():
    """按時間段分組參與者"""
    data = load_participants()
    result = {}
    
    for time_key in TIME_ORDER:
        result[time_key] = []
    
    for user_id, participant in data.items():
        for time_key in participant.get('times', []):
            if time_key in result:
                result[time_key].append(participant)
    
    return result

# ==================== Discord UI 類 ====================

class TimeSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="選擇能參加的時間 (可多選)",
            min_values=1,
            max_values=6,
            options=TIME_OPTIONS
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

class SubmitButton(discord.ui.Button):
    def __init__(self, game_id: str, martial_art: str, time_select: TimeSelect):
        super().__init__(label="✅ 確認提交", style=discord.ButtonStyle.success)
        self.game_id = game_id
        self.martial_art = martial_art
        self.time_select = time_select
    
    async def callback(self, interaction: discord.Interaction):
        if not self.time_select.values:
            await interaction.response.send_message("❌ 請先選擇時間！", ephemeral=True)
            return
        
        selected_times = [TIME_MAPPING.get(v, v) for v in self.time_select.values]
        times_str = "\n".join(selected_times)
        
        # 保存數據
        add_participant(
            str(interaction.user.id),
            interaction.user.name,
            self.game_id,
            self.martial_art,
            self.time_select.values
        )
        
        embed = discord.Embed(
            title="✅ 百業戰參與者信息",
            color=discord.Color.green(),
            description="感謝您的填寫！"
        )
        embed.add_field(name="🎮 遊戲 ID", value=self.game_id, inline=False)
        embed.add_field(name="⚔️ 武學", value=self.martial_art, inline=False)
        embed.add_field(name="⏰ 可參加時間", value=times_str, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # 發送到指定頻道（如果有）
        channel_id = os.getenv('LOG_CHANNEL_ID')
        if channel_id:
            try:
                channel = bot.get_channel(int(channel_id))
                if channel:
                    await channel.send(embed=embed)
            except:
                pass

class TimeSelectView(discord.ui.View):
    def __init__(self, game_id: str, martial_art: str):
        super().__init__()
        time_select = TimeSelect()
        self.add_item(time_select)
        self.add_item(SubmitButton(game_id, martial_art, time_select))

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
            title="⏰ 選擇可參加的時間",
            color=discord.Color.blue(),
            description="請選擇您能參加的所有時間段"
        )
        
        view = TimeSelectView(self.game_id.value, self.martial_art.value)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class SimpleForm(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label="填寫百業戰參與信息", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BaiyeForm(title="百業戰參與者信息表")
        await interaction.response.send_modal(modal)

# ==================== Bot 事件 ====================

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# ==================== 斜杠命令 ====================

@bot.tree.command(name="baiye_war", description="詢問群友是否參加百業戰")
async def baiye_war(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚔️ 百業戰參與者招募",
        color=discord.Color.gold(),
        description="點擊下方按鈕填寫您的參與信息"
    )
    embed.add_field(
        name="📋 需要填寫以下信息：",
        value="• 遊戲 ID\n• 使用武學\n• 可參加時間",
        inline=False
    )
    
    embed.add_field(
        name="⏰ 可選時間段：",
        value="**周六：** 20:30 (聯賽)、21:15 (配對賽 1)、22:15 (配對賽 2)\n**周日：** 20:30 (聯賽)、21:15 (配對賽 1)、22:15 (配對賽 2)",
        inline=False
    )
    
    view = SimpleForm()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="baiye_list", description="查看百業戰參與者列表")
async def baiye_list(interaction: discord.Interaction):
    participants_by_time = get_participants_by_time()
    
    embed = discord.Embed(
        title="📋 百業戰參與者列表",
        color=discord.Color.blue(),
        description="按時間段分類的參與者"
    )
    
    has_participants = False
    
    for time_key in TIME_ORDER:
        participants = participants_by_time[time_key]
        time_label = TIME_MAPPING.get(time_key, time_key)
        
        if participants:
            has_participants = True
            participant_list = []
            for p in participants:
                participant_list.append(
                    f"• ID: {p['game_id']} ({p['martial_art']})"
                )
            
            value = "\n".join(participant_list)
            embed.add_field(
                name=f"⏰ {time_label} ({len(participants)}人)",
                value=value,
                inline=False
            )
    
    if not has_participants:
        embed.description = "目前還沒有參與者，邀請群友填寫吧！"
    
    await interaction.response.send_message(embed=embed)

# ==================== 運行機器人 ====================

bot.run(TOKEN)
