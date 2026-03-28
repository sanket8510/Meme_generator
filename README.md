# 🎭 Multimodal Meme Generator
### Using Diffusion Models + Text Transformers | Generative AI

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=for-the-badge&logo=fastapi)
![LLaMA](https://img.shields.io/badge/LLaMA-3.3--70b-orange?style=for-the-badge)
![Flux](https://img.shields.io/badge/Flux-Diffusion-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

> **Automatically generate funny, relatable, and professional memes from simple text prompts using Generative AI — no design skills needed!**

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Demo](#-demo)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Getting API Keys](#-getting-api-keys)
- [Running the Project](#-running-the-project)
- [How to Use](#-how-to-use)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Team](#-team)

---

## 📖 About the Project

Memes are a dominant form of digital communication, but creating them manually requires:
- Creative & editing skills
- Time to find suitable images
- Knowledge of meme formats and trends

This project solves all of that by building an **end-to-end AI pipeline** that:
1. Understands your text prompt using a **Transformer model (LLaMA 3.3)**
2. Generates a relevant scene image using a **Diffusion model (Flux via Pollinations.ai)**
3. Writes 3 witty caption variations using **LLaMA 3.3 70B (via Groq)**
4. Assembles the final meme with speech bubbles, borders, watermark, and emoji accents using **Pillow**

---

## 🎬 Demo

| Prompt | Generated Meme Style |
|--------|---------------------|
| `Debugging code at 2am` | Tired programmer, 3D cartoon, speech bubble |
| `Exam tomorrow haven't studied` | Panicking student, photorealistic, top-bottom |
| `AI replacing programmers` | Robot in office, sci-fi render, label arrows |
| `Monday morning meetings` | Comic style office workers, speech bubbles |

---

## ✨ Features

- 🧠 **AI-Powered Captions** — 3 different caption styles: Classic, Slang, Absurd
- 🎨 **Real Image Generation** — Human characters always in scene (3D avatars, photorealistic, comic style)
- 🗨️ **3 Meme Formats** — Speech bubbles, Top/Bottom Impact text, Label & Arrows
- 🎭 **4 Tone Themes** — Funny (Gold), Sarcastic (Purple), Relatable (Blue), Absurd (Pink)
- ✨ **Professional Polish** — Glowing borders, tone badge, emoji stickers, watermark
- 📱 **Clean Web UI** — Dark theme, shimmer loading, history grid, download button
- ⚡ **Fast API Backend** — FastAPI + Uvicorn with auto-reload
- 🆓 **100% Free APIs** — Groq (LLaMA) + Pollinations.ai (Flux) — no paid credits needed

---

## 🏗 System Architecture

```
User Prompt (Text)
        │
        ▼
┌───────────────────────┐
│  STEP 1               │
│  Text Processing      │  ← LLaMA 3.3 70B via Groq API
│  (Transformer Model)  │    Understands tone, intent, format
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐       ┌──────────────────────┐
│  STEP 2               │       │  STEP 3              │
│  Image Generation     │       │  Caption Generation  │  ← LLaMA 3.3 70B
│  (Diffusion Model)    │       │  3 styles: Classic,  │    3 witty captions
│  Flux via Pollinations│       │  Slang, Absurd       │    ranked by score
└──────────┬────────────┘       └──────────┬───────────┘
           │                               │
           └──────────────┬────────────────┘
                          ▼
              ┌───────────────────────┐
              │  STEP 4              │
              │  Meme Assembly       │  ← Pillow (PIL)
              │  Speech bubbles,     │    Text overlay,
              │  borders, emoji,     │    Effects, watermark
              │  watermark           │
              └───────────┬──────────┘
                          │
                          ▼
                 🎭 Final Meme Output
                 (PNG, downloadable)
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Text Understanding | LLaMA 3.3 70B (Groq API) | Parse prompt, detect tone, write captions |
| Image Generation | Flux Diffusion (Pollinations.ai) | Generate scene with human characters |
| Image Processing | Pillow (PIL) | Speech bubbles, text, effects, assembly |
| Backend | FastAPI + Uvicorn | REST API server |
| Frontend | HTML + CSS + Vanilla JS | Web UI |
| Environment | Python 3.10+ | Runtime |

---

## 📁 Project Structure

```
meme_generator/
│
├── app.py                 ← FastAPI backend server
├── meme_pipeline.py       ← Core AI pipeline (all 4 steps)
├── requirements.txt       ← Python dependencies
├── .env.example           ← API key template
├── .gitignore             ← Git ignore rules
├── README.md              ← This file
│
├── frontend/
│   └── index.html         ← Full web UI (single file)
│
└── output/                ← Generated memes saved here (auto-created)
    └── meme_xxxxxxxx.png
```

---

## ✅ Prerequisites

Before starting, make sure you have:

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.10 or higher | https://www.python.org/downloads/ |
| VS Code | Latest | https://code.visualstudio.com/ |
| Git | Latest | https://git-scm.com/downloads |
| VS Code Extension: Live Server | Latest | Search in VS Code Extensions |

---

## 🚀 Installation & Setup

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/meme-generator.git
cd meme-generator
```

### Step 2 — Create Virtual Environment

```bash
# Windows
python -m venv env
env\Scripts\activate

# Mac / Linux
python3 -m venv env
source env/bin/activate
```

You should see `(env)` in your terminal prompt.

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
pip install python-dotenv
```

### Step 4 — Set Up API Keys

```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
GROQ_API_KEY=gsk_your_groq_key_here
HF_TOKEN=hf_your_huggingface_token_here
```

---

## 🔑 Getting API Keys

### Groq API Key (Required — Free)

1. Go to **https://console.groq.com/**
2. Sign up for a free account
3. Click **"API Keys"** → **"Create API Key"**
4. Name it anything → Copy the key (`gsk_...`)

> ✅ Free tier: 14,400 requests/day — more than enough!

### HuggingFace Token (Optional — Free)

1. Go to **https://huggingface.co/**
2. Sign up for a free account
3. Profile → **Settings** → **Access Tokens**
4. Click **"New Token"** → Role: **Read** → Copy (`hf_...`)

> 💡 Pollinations.ai (image generation) works without any key — it's completely free!

---

## ▶️ Running the Project

### Start the Backend Server

```bash
# Make sure (env) is active first!
uvicorn app:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Test the backend: open http://localhost:8000 in your browser.
You should see: `{"message": "Multimodal Meme Generator API is running!"}`

### Open the Frontend

1. In VS Code, right-click `frontend/index.html`
2. Click **"Open with Live Server"**
3. Browser opens at `http://127.0.0.1:5500/frontend/index.html`

> ⚠️ Keep the terminal with uvicorn running. Open a new terminal for any other commands.

### Quick Start (Every Time)

```bash
cd meme-generator
env\Scripts\activate          # Windows
# source env/bin/activate     # Mac/Linux
uvicorn app:app --reload --port 8000
```

Then open `frontend/index.html` with Live Server.

---

## 🎮 How to Use

1. **Enter a prompt** in the input box
   - Example: `Debugging code at 2am`
   - Example: `Exam tomorrow haven't studied`
   - Example: `AI replacing programmers`

2. **Click ⚡ Generate** or press `Enter`

3. **Watch the pipeline run** (4 animated steps, ~20-40 seconds):
   - 📝 Text Understanding
   - 🎨 Image Generation
   - 💬 Caption Writing
   - 🖼 Meme Assembly

4. **View your meme** — full size image with captions

5. **Download or regenerate** using the action buttons

---

## 📡 API Reference

### `GET /`
Health check endpoint.

**Response:**
```json
{ "message": "Multimodal Meme Generator API is running!" }
```

---

### `POST /generate`
Generate a meme from a text prompt.

**Request Body:**
```json
{ "prompt": "Debugging code at 2am" }
```

**Response:**
```json
{
  "user_prompt": "Debugging code at 2am",
  "detected_tone": "relatable",
  "image_generation_prompt": "exhausted programmer at glowing monitor at night...",
  "captions": [
    { "top_text": "ONE MORE BUG THEY SAID", "bottom_text": "IT'LL TAKE 5 MINS THEY SAID", "score": 0.95, "style": "classic" },
    { "top_text": "me at 2am: just one more error", "bottom_text": "me at 6am: why is it on fire", "score": 0.87, "style": "slang" },
    { "top_text": "THE BUG: a missing semicolon", "bottom_text": "ME: crying for 4 hours", "score": 0.80, "style": "absurd" }
  ],
  "selected_caption": { "top_text": "ONE MORE BUG THEY SAID", "bottom_text": "IT'LL TAKE 5 MINS THEY SAID" },
  "meme_style": "classic",
  "final_meme_url": "/output/meme_a3f2c1d4.png"
}
```

---

### `GET /output/{filename}`
Serve a generated meme image.

**Example:** `http://localhost:8000/output/meme_a3f2c1d4.png`

---

### Interactive API Docs
FastAPI provides automatic Swagger UI at:
```
http://localhost:8000/docs

---

## 📄 License

This project is built for educational purposes under the MIT License.

---

---

<p align="center">Made with ❤️ using Generative AI</p>
