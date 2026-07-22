# Kungfu Agent Interface

Web interface untuk berinteraksi dengan **kungfu-agent** — general-purpose AI agent dengan Kungfu-style continuity dan Episode/Fact tracking.

![Kungfu Agent Interface](https://img.shields.io/badge/Agent-kungfu--agent-99873C?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi)

## Features

- 🌐 **Web Interface** — Interface modern untuk berinteraksi dengan agent
- 🔄 **Real-time Updates** — WebSocket untuk streaming response
- 📋 **Episode Tracking** — Record semua task dalam format Kungfu-style
- 🔍 **Context Continuity** — Lanjutkan pekerjaan dari session sebelumnya
- 🛡️ **Safety First** — Konfirmasi untuk aksi berbahaya

## Prerequisites

- Python 3.11+
- OpenHands SDK (`openhands>=1.0.0`)
- API key untuk LLM provider ( Anthropic, OpenAI, dll)

## Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/kungfu-agent-interface.git
cd kungfu-agent-interface

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export LLM_API_KEY="your-api-key"
export LLM_MODEL="anthropic/claude-sonnet-4-5-20250929"
```

## Usage

### Start the Server

```bash
python main.py
```

Atau dengan uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Access the Interface

Buka browser dan navigasi ke:
- http://localhost:8000 — Web Interface
- http://localhost:8000/docs — API Documentation

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_API_KEY` | Yes | - | API key untuk LLM provider |
| `LLM_MODEL` | No | `anthropic/claude-sonnet-4-5-20250929` | Model yang digunakan |
| `LLM_BASE_URL` | No | - | Base URL untuk custom LLM endpoint |

## API Endpoints

### REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | GET | Web Interface |
| `GET /api/health` | GET | Health check |
| `POST /api/task` | POST | Create task (returns queue status) |
| `GET /api/episodes` | GET | List all episodes |
| `GET /api/episodes/{episode_id}` | GET | Get episode details |
| `POST /api/upload` | POST | Upload file to workspace |

### WebSocket

Connect ke `/ws/{workspace}` untuk real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/default');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};

ws.send(JSON.stringify({
    type: 'task',
    content: 'Add user authentication'
}));
```

## Kungfu Agent

Agent ini disimpan di `~/.agents/agents/kungfu-agent.md` dan memiliki fitur:

### Kemampuan
- **Kungfu Continuity** — Cek context dari session sebelumnya
- **Episode/Fact Tracking** — Record progress dalam format Kungfu-style
- **Understand First** — Pahami struktur project sebelum coding
- **Incremental Work** — Working step-by-step dengan tracking
- **Safety First** — Konfirmasi untuk aksi berbahaya

### Constraints
- ❌ No major architectural decisions tanpa persetujuan
- ❌ No push ke remote repository
- ❌ No destructive commands
- ❌ Confirm untuk dangerous actions

## Episode Format

Setiap task menghasilkan Episode record:

```json
{
    "episode_id": "ep-20240722-104530",
    "facts": [
        "Created auth middleware at middleware/auth.js",
        "Updated login route to use auth middleware"
    ],
    "timestamp": "2024-07-22T10:45:30Z",
    "status": "completed"
}
```

## Project Structure

```
kungfu-agent-interface/
├── main.py              # FastAPI application
├── templates/
│   └── index.html       # Web interface
├── static/              # Static assets
├── requirements.txt     # Python dependencies
└── README.md
```

## License

Apache-2.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Built with ❤️ using OpenHands SDK**
