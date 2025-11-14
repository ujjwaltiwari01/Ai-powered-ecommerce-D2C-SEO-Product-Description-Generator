<div align="center">

# ✨ AI Product Description Generator

Generate gorgeous, marketplace-ready product descriptions with AI — in minutes! 🪄

<a href="#-quick-start"><img src="https://img.shields.io/badge/Run-Streamlit_App-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white" /></a>
<a href="#-features"><img src="https://img.shields.io/badge/Powered%20by-OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" /></a>
<a href="#-troubleshooting"><img src="https://img.shields.io/badge/Help-Troubleshooting-0ea5e9?style=for-the-badge" /></a>

</div>

---

## 🧠 What this app does (like magic!)

- 🖼️ **Sees your product image** and understands what it looks like (Vision AI)
- 🎤 **Listens to your voice note** and turns it into text (Audio → Text)
- 🧩 **Merges everything** with your product form inputs
- 🛒 **Writes marketplace-perfect content** (title, bullets, specs) for multiple stores (e.g., Amazon)
- 💾 **Lets you copy or export** what it made, so you can paste it wherever you like

> You fill a friendly form + optionally upload a picture and speak about your product → the app blends it all into stunning product descriptions.

---

## 🎯 Features

- **Step-by-step wizard** with a clean, modern UI
- **Image analysis** using GPT-4 Vision
- **Audio transcription** using Whisper (OpenAI)
- **Multi‑marketplace generation** (easily extendable)
- **Beautiful results layout** with separate boxes:
  - Title
  - Description
  - Key Features
  - Specifications
- **Works offline for UI logic** (needs internet only for OpenAI calls)

---

## 🧒 Setup so easy a 5‑year‑old can do it

Follow these tiny steps. One at a time. You got this! 👇

### 1) Install Python
- Go to https://www.python.org/downloads/
- Download Python 3.10+ and install.
- During install, tick “Add Python to PATH”.

Check it works:
```bash
python --version
```

### 2) Open the project folder
Open a terminal (PowerShell on Windows) in this folder:
```
Day 7 - Ai product discription/
```

### 3) Create a virtual environment (optional but recommended)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 4) Install packages
```bash
pip install -r requirements.txt
```

Optional (for live mic recording):
```bash
pip install streamlit-audiorec
```

### 5) Add your OpenAI API Key 🔑
Create a file named `.env` in the project folder (if it doesn’t exist) and put this line inside:
```env
OPENAI_API_KEY=sk-...your real key here...
```
If your organization enforces scoping, also add:
```env
OPENAI_ORG_ID=org_...
```

> We load `.env` with override, so the value in this file wins even if your computer has an older variable set.

### 6) Run the app 🚀
```bash
streamlit run app.py
```
Then open the shown Local URL in your browser.

### 7) Use it!
- Step 1: Fill product details
- Step 2: Pick marketplaces
- Step 3: See “Generated Descriptions”
  - Each marketplace has its own tab
  - Content is shown in neat boxes: Title, Description, Features, Specs

---

## 🧪 Tips for best results
- Use a clear, bright product image (no busy backgrounds)
- Keep voice notes short (2–10 seconds) and clear
- Add 3–7 concise bullet features in the form

---

## 🛠️ Developer Guide

### Project structure (high‑level)
```
components/
  layout.py          # Page layout & result rendering (tabs + boxed sections)
  sidebar.py         # Sidebar settings
  forms.py           # Product form UI
chains/              # Orchestration for merging AI inputs
services/
  marketplace_service.py  # Generates content per marketplace
utils/
  ai_services.py     # OpenAI integrations (Vision, Whisper, Text)
  state.py           # Session state helpers
  file_utils.py      # File handling & validation
app.py               # Streamlit entry point
```

### Key internals
- `utils/ai_services.py`
  - Lazy client init: always re‑reads `OPENAI_API_KEY`/`OPENAI_ORG_ID`
  - Vision: GPT‑4‑Vision
  - Audio: Whisper (`whisper-1`)
  - Text: GPT‑4 previews (configurable)
- `components/layout.py`
  - Results shown with `st.tabs` and `st.container(border=True)` for gorgeous boxes

---

## ❓ Troubleshooting (super helpful!)

### 401 Unauthorized (invalid API key)
- Make sure `.env` contains a real key on ONE line:
  ```env
  OPENAI_API_KEY=sk-...
  ```
- Restart the app after edits.
- If your key starts with `sk-proj-` and still fails, your project may not have access to `whisper-1`. Either:
  - enable `whisper-1` for your project in the OpenAI dashboard, or
  - try a classic key (`sk-...`) to confirm.
- If your organization enforces scoping, set:
  ```env
  OPENAI_ORG_ID=org_...
  ```

### ffmpeg / pydub warnings
- The app doesn’t require ffmpeg anymore (pydub path removed).
- You can ignore ffmpeg installation unless you explicitly want the ffmpeg CLI.

### Live mic recording not showing
- Install the optional package:
  ```bash
  pip install streamlit-audiorec
  ```

---

## ✨ Extend to more marketplaces
- Add a template and rules in `services/marketplace_service.py`
- The UI will automatically create a tab and show a boxed layout for it

---

## 📜 Scripts & Commands (quick copy)

```bash
# Create venv
python -m venv .venv && .venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Optional mic support
pip install streamlit-audiorec

# Run app
streamlit run app.py
```

---

<div align="center">

### Need help?

<a href="#-troubleshooting"><img src="https://img.shields.io/badge/See%20Troubleshooting-0ea5e9?style=for-the-badge" /></a>

</div>
