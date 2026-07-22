"""
Kungfu Agent Interface - FastAPI Backend
Web interface untuk berinteraksi dengan kungfu-agent
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# OpenHands SDK imports
from openhands.sdk import LLM, Agent, Conversation
from openhands.sdk.subagent import register_file_agents
from openhands.tools.delegate import DelegationVisualizer
from openhands.tools.task import TaskToolSet
from openhands.sdk import Tool

app = FastAPI(
    title="Kungfu Agent Interface",
    description="Web interface untuk berinteraksi dengan kungfu-agent",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Global state
workspace_path = Path.home() / "kungfu-workspace"
workspace_path.mkdir(exist_ok=True)

# Agent state
agent_initialized = False
current_conversation: Optional[Conversation] = None
llm: Optional[LLM] = None

# Request/Response models
class TaskRequest(BaseModel):
    task: str
    workspace: Optional[str] = None

class EpisodeResponse(BaseModel):
    episode_id: str
    facts: List[str]
    timestamp: str
    status: str


def get_llm() -> LLM:
    """Get or create LLM instance"""
    global llm
    if llm is None:
        llm = LLM(
            model=os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-5-20250929"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
        )
    return llm


async def initialize_agent():
    """Initialize the kungfu-agent"""
    global agent_initialized, current_conversation
    
    if agent_initialized:
        return
    
    # Register file-based agents from user directory
    agent_dir = Path.home() / ".agents" / "agents"
    register_file_agents(str(agent_dir))
    
    # Initialize conversation
    main_agent = Agent(
        llm=get_llm(),
        tools=[Tool(name=TaskToolSet.name)],
    )
    
    current_conversation = Conversation(
        agent=main_agent,
        workspace=workspace_path,
    )
    
    agent_initialized = True


class AgentWebSocket:
    """WebSocket handler for streaming agent responses"""
    
    def __init__(self, websocket: WebSocket, workspace: Path):
        self.websocket = websocket
        self.workspace = workspace
        self.conversation = None
        self.is_running = False
    
    async def initialize(self):
        """Initialize conversation"""
        main_agent = Agent(
            llm=get_llm(),
            tools=[Tool(name=TaskToolSet.name)],
        )
        
        self.conversation = Conversation(
            agent=main_agent,
            workspace=self.workspace,
        )
    
    async def send_message(self, message: str):
        """Send message and stream response"""
        await self.websocket.send_json({
            "type": "status",
            "content": "Initializing agent...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Register agents
        agent_dir = Path.home() / ".agents" / "agents"
        register_file_agents(str(agent_dir))
        
        await self.websocket.send_json({
            "type": "status",
            "content": "Agent ready. Processing task...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Send task to agent
        task_msg = f"Please execute this task using kungfu-agent: {message}"
        
        # Stream response
        await self.websocket.send_json({
            "type": "status",
            "content": "Executing task...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Run conversation
        self.conversation.send_message(task_msg)
        
        # Collect messages
        messages = []
        for msg in self.conversation.get_messages():
            messages.append(msg)
        
        # Run the conversation
        self.conversation.run()
        
        # Get final response
        final_response = self.conversation.get_final_response()
        
        await self.websocket.send_json({
            "type": "episode",
            "content": {
                "episode_id": f"ep-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "facts": self._extract_facts(messages),
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            },
            "timestamp": datetime.now().isoformat()
        })
        
        await self.websocket.send_json({
            "type": "result",
            "content": final_response,
            "timestamp": datetime.now().isoformat()
        })
    
    def _extract_facts(self, messages: list) -> List[str]:
        """Extract facts from conversation messages"""
        facts = []
        for msg in messages:
            if hasattr(msg, 'content'):
                content = str(msg.content)
                if 'Episode' in content or 'Fact' in content:
                    facts.append(content[:200] + "..." if len(content) > 200 else content)
        return facts


# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interface"""
    with open("templates/index.html", "r") as f:
        return f.read()


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": agent_initialized,
        "workspace": str(workspace_path)
    }


@app.post("/api/task")
async def create_task(request: TaskRequest):
    """Create and execute a task"""
    try:
        await initialize_agent()
        
        # Update workspace if provided
        if request.workspace:
            task_workspace = Path(request.workspace)
            if task_workspace.exists():
                task_workspace = workspace_path
        
        return {
            "status": "queued",
            "task": request.task,
            "workspace": str(workspace_path),
            "message": "Task queued. Use WebSocket for real-time updates."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/episodes")
async def list_episodes():
    """List all recorded episodes"""
    episodes_dir = workspace_path / ".kungfu" / "episodes"
    if not episodes_dir.exists():
        return {"episodes": []}
    
    episodes = []
    for episode_file in episodes_dir.glob("*.json"):
        with open(episode_file, "r") as f:
            episodes.append(json.load(f))
    
    return {"episodes": episodes}


@app.get("/api/episodes/{episode_id}")
async def get_episode(episode_id: str):
    """Get specific episode details"""
    episode_file = workspace_path / ".kungfu" / "episodes" / f"{episode_id}.json"
    
    if not episode_file.exists():
        raise HTTPException(status_code=404, detail="Episode not found")
    
    with open(episode_file, "r") as f:
        return json.load(f)


@app.websocket("/ws/{workspace}")
async def websocket_endpoint(websocket: WebSocket, workspace: str):
    """WebSocket endpoint for real-time agent interaction"""
    await manager.connect(websocket)
    
    ws_handler = AgentWebSocket(websocket, workspace_path)
    
    try:
        await ws_handler.initialize()
        
        while True:
            data = await websocket.receive_text()
            
            # Parse message
            try:
                msg_data = json.loads(data)
                msg_type = msg_data.get("type", "task")
                
                if msg_type == "task":
                    task = msg_data.get("content", "")
                    await ws_handler.send_message(task)
                    
                elif msg_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except json.JSONDecodeError:
                # Treat as plain text task
                await ws_handler.send_message(data)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": str(e),
            "timestamp": datetime.now().isoformat()
        })
        manager.disconnect(websocket)


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload file to workspace"""
    try:
        file_path = workspace_path / file.filename
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return {
            "status": "success",
            "filename": file.filename,
            "path": str(file_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
