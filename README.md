# LightningMapTW

即時閃電觀測地圖服務 — 台灣專屬版

---

## 📌 專案介紹

本專案透過中央氣象局公開資料，即時下載並解析閃電觀測 KMZ 檔，並使用 Python 的 `matplotlib` 和 `cartopy` 繪製出台灣地區的即時閃電分布圖。  
提供輕量化 HTTP 服務，供外部系統（如網站或聊天機器人）直接存取快取後的閃電地圖圖片。

---

## ✨ 功能特色

- ⏱ 每小時自動抓取並更新最新閃電資料快取圖片
- 🗺 黑底地圖搭配時間漸變色，顯示閃電發生先後順序
- 🌐 提供 HTTP 服務，直接回傳 PNG 圖片
- ⚙️ 易於部署與擴展，適合整合至各類氣象應用

---

## 🗂 目錄結構

```
LightningMapTW/
├── main.py      # 主程式
├── README.md    # 專案說明文件（即本檔）
├── LICENSE      # 授權條款
```

---

## 🚀 快速開始

### 1. 複製專案到本地

```bash
git clone https://github.com/Eugene526/LightningMapTW.git
cd LightningMapTW
```

### 2. 建議啟用虛擬環境（可選）

```bash
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
```

### 3. 安裝依賴套件

```bash
pip install aiohttp matplotlib cartopy lxml
```

### 4. 設定中央氣象局 API Key  
直接在 `main.py` 裡修改 `API_KEY` 變數  
或使用環境變數更安全：

```bash
export CWA_API_KEY="你的API_KEY"   # macOS / Linux
set CWA_API_KEY="你的API_KEY"      # Windows CMD
$env:CWA_API_KEY="你的API_KEY"     # Windows PowerShell
```

### 5. 執行程式

```bash
python main.py
```

### 6. 用瀏覽器開啟查看

打開網址：`http://localhost:4444/`  
即可查看即時閃電地圖 🌩

---

## ❓ 常見問題 FAQ

### Q1. 為什麼我看不到圖片？
- 第一次啟動可能需要幾秒下載資料與產生圖像
- 確認 terminal 中是否有錯誤訊息
- 檢查 API Key 是否填寫正確、網路是否可連接中央氣象局

---

### Q2. `cartopy` 安裝失敗怎麼辦？
`cartopy` 需要一些系統套件支援，推薦使用以下方式：

```bash
# macOS/Linux（需先安裝 proj、geos、gdal）
brew install proj geos gdal
pip install cartopy

# 或使用 conda（推薦）
conda install -c conda-forge cartopy
```

---

### Q3. 可以調整更新頻率嗎？
可以！請打開 `main.py`，修改這一行中的秒數：

```python
await asyncio.sleep(1 * 60 * 60)  # 每 1 小時更新
```

---

### Q4. 可以接到 Discord 或 Line 機器人嗎？
當然可以！  
只要前往 `http://localhost:4444/` 即可取得最新圖片，支援任何外部整合（Flask、Ngrok、Render、Replit 等都行）

---

## 🙌 聯絡方式

有任何建議或回報錯誤，歡迎開 Issue，或私訊作者Discord: eugene526。  
希望這個工具能幫助你更輕鬆觀測閃電⚡！

---

## 🪪 授權條款

本專案採用 MIT 授權，請自由使用、修改與散播。
