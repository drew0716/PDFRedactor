# 🛡️ RedactIQ

**Your AI-powered privacy assistant for clean, compliant documents.**

RedactIQ helps you scan and redact sensitive content from PDFs with the help of Claude AI and built-in regex detection. It's designed for professionals and teams that need fast, intelligent redaction of PII, PHI, and other confidential information.

---

### 🚀 Features

- 🔍 **Automatic PII/PHI detection** using regular expressions
- 🤖 **AI-enhanced redaction suggestions** via Claude 3 Haiku
- ✅ **Interactive review** table with filters, sort, and risk level indicators
- 📄 **On-the-fly PDF redactions** with one-click export
- 🎨 Beautiful UI with modern theming and no data stored after processing

---

### 🧪 How It Works

1. Upload a PDF containing potentially sensitive information.
2. Optionally enable **Claude AI** to suggest deeper redactions.
3. Review detected items in an interactive table:
   - Checkboxes to confirm what gets redacted
   - Page number, reason, and risk level (🔴/🟡/🟢)
4. Apply redactions and download your cleaned PDF.

---

## 🚀 Try the App

🔺 **[Launch RedactIQ](https://redactiq.streamlit.app)**

> **Note:** Access to the hosted version is currently limited.
> Contact [Drew](mailto:drew0716@gmail.com) to request access.

---

### 📦 Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/drew0716/pdfredactor.git
cd pdfredactor
pip install -r requirements.txt
```

---

### 🧠 Claude API Setup

1. [Get a Claude API key](https://console.anthropic.com)
2. Add your key to `.streamlit/secrets.toml` (this file is already `.gitignore`d):

```toml
claude_api_key = "sk-ant-XXXXXXXXXXXXXXXX"
```

---

### 🏁 Run the App

```bash
streamlit run app.py
```

Then visit [http://localhost:8501](http://localhost:8501)

---

### ☁️ Deploy to Streamlit Cloud

1. Push your project to a public GitHub repo.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) → New App.
3. Set `app.py` as the main file.
4. Add your Claude API key under **Settings → Secrets**.
5. Done!

---

### 🛑 Security & Privacy

- ✅ No documents or images are stored — all processing is done in-memory and temporary files are deleted after use.
- ✅ `secrets.toml` is excluded via `.gitignore` to prevent accidental exposure.
- ✅ Claude API suggestions run securely and only on your provided input.

---

### 📄 Project Structure

```
📁 pdfredactor/
├── app.py                # Main Streamlit app
├── claude_helper.py      # Claude API integration
├── requirements.txt
├── .gitignore
└── .streamlit/
    └── secrets.toml      # Your Claude API key (ignored by git)
```

---

### 💡 Future Ideas

- OCR support for scanned PDFs
- Risk-based redaction auto-selection
- PDF metadata cleanup
- Export to DOCX with redaction markers

---

### 👨‍💻 Created By

Built with ❤️ by Drew Galbraith  
[GitHub](https://github.com/drew0716) • [LinkedIn](https://www.linkedin.com/in/scubadrew0716/)