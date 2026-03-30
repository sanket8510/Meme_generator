# 🎭 Multimodal Meme Generator
### Diffusion Models + Text Transformers | Generative AI
**Group 31 – Div B | Sanket Mahajan & Onkar Sathe | Guide: Prof. Vivek Patil**

---

## 📁 Project Structure

```
meme_generator/
│
├── app.py               ← FastAPI backend (main server)
├── meme_pipeline.py     ← Core AI pipeline (Transformer + Diffusion)
├── requirements.txt     ← Python dependencies
├── .env.example         ← API key template
├── .gitignore
│
├── frontend/
│   └── index.html       ← Full UI (open in browser)
│
└── output/              ← Generated memes saved here (auto-created)
```

---

## ⚙️ Step-by-Step Setup in VS Code

### STEP 1 — Prerequisites
Make sure you have installed:
- **Python 3.10+** → https://www.python.org/downloads/
- **VS Code** → https://code.visualstudio.com/
- **Live Server extension** (for frontend) → search in VS Code Extensions

---

### STEP 2 — Open Project in VS Code
```
File → Open Folder → select the `meme_generator` folder
```

---

### STEP 3 — Create a Virtual Environment
Open the VS Code terminal (`Ctrl + ~`) and run:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

### STEP 4 — Install Dependencies
```bash
pip install -r requirements.txt
```
This installs: FastAPI, Uvicorn, Anthropic SDK, Pillow, Requests.

---

### STEP 5 — Set Up API Keys

Copy `.env.example` to `.env`:
```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

Open `.env` and fill in your keys:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
HF_TOKEN=hf_xxxxxxxxxxxxxxxx   ← optional but recommended
```

**Get your keys:**
- Anthropic API key → https://console.anthropic.com/  (free credits available)
- HuggingFace token → https://huggingface.co/settings/tokens  (free account)

---

### STEP 6 — Load Environment Variables

```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your_key_here"
$env:HF_TOKEN="your_hf_token_here"

# Windows (CMD)
set ANTHROPIC_API_KEY=your_key_here
set HF_TOKEN=your_hf_token_here

# Mac / Linux
export ANTHROPIC_API_KEY=your_key_here
export HF_TOKEN=your_hf_token_here
```

OR install python-dotenv and add this to the top of `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```
Then run: `pip install python-dotenv`

---

### STEP 7 — Start the Backend Server
```bash
uvicorn app:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Test it: open http://localhost:8000 in your browser — you should see:
```json
{"message": "Multimodal Meme Generator API is running!"}
```

---

### STEP 8 — Open the Frontend

**Option A — VS Code Live Server (recommended):**
1. Right-click `frontend/index.html`
2. Click **"Open with Live Server"**
3. Browser opens at `http://127.0.0.1:5500/frontend/index.html`

**Option B — Direct file open:**
1. Open `frontend/index.html` directly in your browser

---

### STEP 9 — Generate a Meme! 🎉
1. Type any prompt (e.g., *"Monday morning meetings"*)
2. Click **⚡ Generate**
3. Wait ~15–30 seconds for the AI pipeline to run
4. Your meme appears with captions, tone analysis, and download button!

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/generate` | Generate a meme |
| GET | `/output/{filename}` | Serve generated meme |

**Example API call:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Debugging code at 2am"}'
```

---

## 🧠 How the Pipeline Works

```
User Prompt
    ↓
[STEP 1] Claude (Transformer) — understands tone, extracts intent
    ↓
[STEP 2] Stable Diffusion (HuggingFace API) — generates meme image
    ↓
[STEP 3] Claude (Transformer) — generates witty captions
    ↓
[STEP 4] Pillow — overlays text on image → saves PNG
    ↓
Final Meme Output
```

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| `401 Unauthorized` | Check your ANTHROPIC_API_KEY is correct |
| Image is a gradient (not AI) | Add your HF_TOKEN to .env — HuggingFace model may be loading |
| CORS error in browser | Make sure backend is running on port 8000 |
| Port already in use | Change port: `uvicorn app:app --port 8001` |

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Text Understanding | Claude (Anthropic) — Transformer |
| Image Generation | Stable Diffusion XL (HuggingFace) — Diffusion |
| Caption Overlay | Pillow (PIL) |
| Backend | FastAPI + Uvicorn (Python) |
| Frontend | Vanilla HTML/CSS/JS |
