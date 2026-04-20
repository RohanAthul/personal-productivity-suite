# 💬 Ollama Local Chat

A minimal Streamlit-based chat interface for running conversations with local LLMs via [Ollama](https://ollama.com/).

---

## Features

- **Model selection** — automatically detects all models you have pulled in Ollama and lets you switch between them from the sidebar
- **Streaming responses** — tokens stream in real time with a live cursor, just like ChatGPT
- **Persistent chat history** — conversation context is maintained across turns within the same session
- **Fully local** — no API keys, no data leaving your machine

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.8+ |
| [Ollama](https://ollama.com/download) | Latest |
| At least one pulled model | e.g. `ollama pull llama3` |

---

## Installation

```bash
# 1. Clone or copy the project
git clone <your-repo-url>
cd <project-folder>

# 2. Install dependencies
pip install streamlit ollama
```

---

## Usage

**Option 1 — standard Streamlit CLI**
```bash
# 1. Make sure Ollama is running
ollama serve

# 2. Launch the app
streamlit run app.py
```

**Option 2 — via `run_app.py`**

`run_app.py` is a convenience launcher that invokes Streamlit programmatically, which is useful when packaging the app as an executable (e.g. with PyInstaller) or running it from an IDE without a terminal.

```bash
python run_app.py
```

It resolves `app.py` relative to the current working directory and starts Streamlit with `developmentMode` disabled, so it behaves like a production build.

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## How It Works

1. On startup, the app calls `ollama.list()` to fetch your locally available models and populates the sidebar dropdown.
2. User messages are appended to `st.session_state.messages`, which acts as the full conversation history.
3. Each response is streamed from Ollama chunk-by-chunk and rendered progressively with a `▌` cursor until complete.
4. The finished response is saved back to the session history, keeping the full context for future turns.

---

## Project Structure

```
.
├── app.py           # Streamlit chat application
└── run_app.py       # Programmatic launcher (useful for packaging / IDEs)
```

---

## Troubleshooting

**"Could not fetch models. Is Ollama running?"**
Ollama isn't started. Run `ollama serve` in a separate terminal before launching the app.

**Empty model dropdown**
You haven't pulled any models yet. Run `ollama pull <model-name>`, e.g.:
```bash
ollama pull llama3
ollama pull mistral
```

**Error generating response**
Ensure the selected model is fully downloaded and that Ollama is still running. Check `ollama list` in your terminal to confirm.

---

## License

MIT
