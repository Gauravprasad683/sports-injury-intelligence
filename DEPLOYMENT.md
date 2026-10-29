# 🚀 Guide: Deploying to Streamlit Community Cloud (Free)

This application is fully prepared for one-click deployment on **Streamlit Community Cloud** (`share.streamlit.io`).

---

## 🛠️ Step 1: Push Project to GitHub

1. Go to [GitHub.com](https://github.com) and log in (or create a free account).
2. Click **New Repository** (give it a name like `sports-injury-intelligence`).
3. Set it to **Public** (required for free Streamlit Community Cloud) and click **Create repository**.
4. Upload all files from this folder (`c:\Users\ASUS\Downloads\player`) to the repository:
   - You can click **"uploading an existing file"** on GitHub and drag & drop the files/folders, OR use GitHub Desktop.
   - **Key files to ensure are uploaded:**
     - `app.py`
     - `requirements.txt`
     - `.streamlit/config.toml`
     - `player_health_data.json`
     - `credentials.json`
     - `medical-protocol.md`
     - `briefing-template.md`
     - `synthetic_data.py`
     - `groq_rag.py`
     - `guardrails/` (both `guardrails_policy.md` and `validator.py`)
     - `models/` (both `injury_risk_model.joblib` and `model_metadata.json`)
     - `data/`

---

## ☁️ Step 2: Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with your GitHub account.
2. Click the **"New app"** (or **"Create app"**) button.
3. Select your repository:
   - **Repository:** `your-username/sports-injury-intelligence`
   - **Branch:** `main` (or `master`)
   - **Main file path:** `app.py`

---

## 🔑 Step 3: Add Your Groq API Key (Secrets)

Before clicking Deploy:
1. Click **"Advanced settings..."** at the bottom of the deploy screen.
2. Under **Secrets**, paste your Groq API key in TOML format:
   ```toml
   groq_api_key = "gsk_your_actual_groq_api_key_here"
   ```
3. Click **Save**.

---

## 🎉 Step 4: Click Deploy!

Click **"Deploy!"**. Streamlit Cloud will automatically:
- Install the dependencies from `requirements.txt`.
- Launch your application.
- Give you a permanent public URL (e.g., `https://sports-injury-intelligence.streamlit.app`) that you can share with anyone!

