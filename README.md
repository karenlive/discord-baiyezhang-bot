# Discord 百業戰機器人

這是一個 Discord 機器人，用於幫助詢問群友是否參加百業戰活動。

## 功能

- 📝 **詢問表單**：收集參與者的遊戲 ID、使用武學和可參加時間
- ⏰ **時間選項**：提供上午、下午、晚上的時間選擇
- ⚔️ **武學選擇**：支援多種武學類型
- 📋 **參與者列表**：記錄所有參與者信息

## 快速開始

### 1. 建立 Discord 應用

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)
2. 點擊 "New Application"
3. 給您的應用取個名字
4. 在左側選擇 "Bot"，點擊 "Add Bot"
5. 在 "TOKEN" 部分點擊 "Copy" 複製您的 Bot Token

### 2. 設置 Bot 權限

1. 在 "OAuth2" → "URL Generator" 頁面
2. 選擇以下 Scopes：
   - `bot`
3. 選擇以下 Permissions：
   - Send Messages
   - Send Messages in Threads
   - Embed Links
   - Read Message History
   - Use Slash Commands
4. 複製生成的 URL，在瀏覽器中打開以將 Bot 加入您的伺服器

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

### 4. 設置環境變數

1. 複製 `.env.example` 為 `.env`
2. 編輯 `.env` 文件，填入您的 Discord Bot Token：

```
DISCORD_TOKEN=your_bot_token_here
LOG_CHANNEL_ID=your_channel_id_here  # (可選)
```

### 5. 運行機器人

```bash
python bot.py
```

## 使用方法

### 命令

#### `/baiye_war`
詢問群友是否參加百業戰。使用者點擊按鈕後會彈出表單填寫以下信息：
- **遊戲 ID**：玩家的遊戲帳號 ID
- **武學**：玩家使用的武學類型
- **可參加時間**：玩家可參加的時間段

#### `/baiye_list`
查看已記錄的百業戰參與者列表

### 選項

**可參加時間選項：**
- 上午 (08:00-12:00)
- 下午 (12:00-17:00)
- 晚上 (17:00-23:00)
- 不確定

**武學選項：**
- 劍法
- 刀法
- 拳法
- 掌法
- 指法
- 其他

## 自定義

### 修改時間選項

在 `bot.py` 中編輯 `TIME_OPTIONS` 列表：

```python
TIME_OPTIONS = [
    discord.SelectOption(label="您的選項", value="your_value"),
    # ...
]
```

### 修改武學選項

在 `bot.py` 中編輯 `MARTIAL_ARTS` 列表：

```python
MARTIAL_ARTS = [
    discord.SelectOption(label="武學名稱", value="martial_value"),
    # ...
]
```

### 設置日誌頻道

如果希望所有回應記錄到特定頻道，在 `.env` 中設置 `LOG_CHANNEL_ID`：

```
LOG_CHANNEL_ID=123456789
```

## 結構

```
discord-baiyezhang-bot/
├── bot.py                 # 主機器人文件
├── requirements.txt       # Python 依賴
├── .env.example          # 環境變數範本
├── .gitignore            # Git 忽略規則
└── README.md             # 說明文件
```

## 故障排除

### Bot 不響應命令
- 確認 Bot 已加入伺服器
- 檢查 Bot 是否具有發送消息的權限
- 重新啟動 Bot 並運行 `/baiye_war` 命令

### Token 錯誤
- 確認 `.env` 文件中的 Token 正確
- 從 Discord Developer Portal 重新複製 Token

### 缺少依賴
```bash
pip install -r requirements.txt --upgrade
```

## 許可證

MIT

## 支持

如有問題，請提交 Issue 或 Pull Request。