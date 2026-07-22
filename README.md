# Kungfu Agent Interface

Web interface untuk berinteraksi dengan **kungfu-agent** — general-purpose AI coding assistant dengan Kungfu-style Episode/Fact tracking.

**🎌 Live Demo (No API needed!):** https://antono4.github.io/kungfu-agent/

![Kungfu Agent Interface](https://img.shields.io/badge/Agent-kungfu--agent-99873C?style=for-the-badge)
![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Deployed-brightgreen?style=for-the-badge)
![Demo Mode](https://img.shields.io/badge/Demo-Mode%20Active-22C55E?style=for-the-badge)

## Features

- 🎌 **Demo Mode** — Coba langsung tanpa API key!
- 🌐 **Web Interface** — Interface modern untuk berinteraksi dengan agent
- 📋 **Episode Tracking** — Record semua task dalam format Kungfu-style
- ⚡ **Quick Actions** — Contoh coding task yang langsung bisa dicoba
- 🎨 **Dark Theme** — Modern UI dengan dark mode
- 📱 **Responsive** — Tampil baik di desktop dan mobile

## Demo Mode

Demo mode menyediakan contoh responses untuk topic umum:

- 📊 **Fibonacci Function** — Python recursive implementation
- 🌐 **Flask REST API** — Basic CRUD endpoints  
- ⚡ **Async/Await** — JavaScript async patterns
- 📦 **Python Class** — OOP example
- 📝 **Git Commands** — Common git operations

## Quick Start (Demo Mode)

1. Buka https://antono4.github.io/kungfu-agent/
2. Klik **Quick Actions** untuk melihat contoh
3. Atau ketik task custom dan klik **Send**

## Full Installation (with Real LLM)

Jika ingin terhubung ke real LLM:

```bash
# Clone repository
git clone https://github.com/antono4/kungfu-agent.git
cd kungfu-agent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export LLM_API_KEY="your-api-key"
export LLM_MODEL="gpt-4"  # atau model lain

# Start server
python main.py
```

## Architecture Reference

Project ini terinspirasi dari:

- [langchain-ai/agent-chat-ui](https://github.com/langchain-ai/agent-chat-ui) — LangGraph agent chat UI
- [hamedafarag/claudeck](https://github.com/hamedafarag/claudeck) — Browser-based Claude Code UI
- [lhz960904/code-artisan](https://github.com/lhz960904/code-artisan) — Web coding agent (bolt.new style)

## Project Structure

```
kungfu-agent/
├── index.html           # Demo web interface (GitHub Pages)
├── templates/
│   └── index.html       # Template for Flask
├── main.py              # FastAPI backend (optional)
├── requirements.txt     # Python dependencies
├── .github/
│   └── workflows/
│       └── deploy.yml   # GitHub Pages deployment
└── README.md
```

## License

Apache-2.0

---

**Built with ❤️ using Kungfu principles**
