# 🤖 PDF RAG Bot — Gemini-Powered Search tool

A lightweight Retrieval-Augmented Generation (RAG) chatbot built with **Streamlit** and **Google Gemini**. Upload a PDF and ask questions about its content — the app extracts the text and passes it as context to the model, giving you document-aware responses with streaming output.

---

## Problem Statement
Programming documentation and cheatsheets are dense, finding a specific concept or syntax snippet often means endless scrolling or relying on basic keyword search that doesn't understand context or intent.  

I wanted a smarter way to interact with PDF-based technical documents: the ability to ask natural language questions and get precise, relevant answers without having to manually scan through pages.  

This project was built to solve that problem. By leveraging the Gemini API — Google's free and powerful AI API — I built a system that can ingest PDF documents and respond to natural language queries about their contents. It turned a frustrating workflow into a conversational one, and along the way taught me how to work with external APIs, handle document parsing, and build AI-powered tooling from scratch.

---

## ✨ Features

- 📄 **PDF Upload** — Upload any PDF via the sidebar and use it as context for your queries
- 🌊 **Streaming Responses** — Responses stream in token-by-token for a smooth chat experience
- 🎛️ **Adjustable Model Behavior** — Choose between *Precise*, *Balanced*, or *Creative* output using a temperature slider
- 💬 **Persistent Chat History** — Conversation history is preserved within the session
- ⚡ **Powered by Gemini** — Uses Google's `gemini-3-flash-preview` model via the `google-genai` SDK

Gemini 3 Flash chosen specifically because of its 1-million+ token context window. This means for many documents, we don't require a complex vector database; we can just feed the entire document into the prompt.

---

## 🚀 Getting Started

### Prerequisites

- Python 3
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/pdf-rag-bot.git
   cd pdf-rag-bot
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit google-genai pypdf python-dotenv
   ```

3. **Set up your environment variables**

   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

---

## 🗂️ Project Structure

```
pdf-rag-bot/
├── app.py          # Main application
├── run_app.py      # Programmatic launcher for IDEs / packaging
├── .env            # API key (not committed to version control)
├── .gitignore
└── README.md
```

---

## 🧠 How It Works

1. The user uploads a PDF in the sidebar
2. When a question is submitted, `pypdf` extracts the raw text from the PDF
3. The first 5,000 characters of that text are prepended to the user's question as context
4. The combined prompt is sent to Gemini, which streams back a context-aware response

> **Note:** This implementation uses simple text truncation rather than a true vector database.

---

## ⚙️ Configuration

| Setting | Options | Default | Description |
|---|---|---|---|
| Model Behavior | Precise / Balanced / Creative | Balanced | Maps to Gemini temperature values 0.0 / 0.5 / 1.0 |
| Context window | — | 5,000 chars | Max PDF text passed to the model per query |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | UI framework |
| `google-genai` | Gemini API client |
| `pypdf` | PDF text extraction |
| `python-dotenv` | Environment variable management |

---

## 🔒 Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key |

Make sure `.env` is listed in your `.gitignore` to avoid accidentally committing your API key.

---

## 🛣️ Potential Improvements

- **Vector store integration** — Use FAISS or ChromaDB to embed and retrieve relevant PDF chunks instead of truncating raw text
- **Multi-PDF support** — Allow uploading and querying across multiple documents
- **Source highlighting** — Display which part of the PDF the answer was derived from
- **Chat export** — Let users download the conversation history

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
