from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
from ai_agent import HealPrintAIAgent

app = FastAPI(title="HealPrint Chat Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Agent
ai_agent = HealPrintAIAgent()

# Simple in-memory storage for MVP
conversations_db = {}

class ChatMessage(BaseModel):
    message: str
    user_id: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    message_id: str
    assessment_stage: str
    symptoms_collected: Dict[str, Any]
    needs_diagnosis: bool

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[dict]

@app.get("/")
async def root():
    return {"service": "HealPrint Chat Service", "status": "running"}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(chat_message: ChatMessage):
    """Process chat message and return AI response"""
    
    # Find existing conversation for this user or create new one
    conversation_id = None
    for conv_id, conv_data in conversations_db.items():
        if conv_data["user_id"] == chat_message.user_id:
            conversation_id = conv_id
            break
    
    # If no existing conversation, create a new one
    if conversation_id is None:
        conversation_id = f"conv_{chat_message.user_id}_{len(conversations_db)}"
    
    # Use AI Agent for professional health conversation
    ai_response = ai_agent.chat_with_user(
        user_message=chat_message.message,
        user_id=chat_message.user_id,
        conversation_id=conversation_id
    )
    
    # Store conversation in our database
    message_id = f"msg_{len(conversations_db) + 1}"
    if conversation_id not in conversations_db:
        conversations_db[conversation_id] = {
            "user_id": chat_message.user_id,
            "messages": []
        }
    
    conversations_db[conversation_id]["messages"].append({
        "id": message_id,
        "user_message": chat_message.message,
        "ai_response": ai_response["response"],
        "timestamp": "2024-01-01T00:00:00Z"  # In production, use real timestamp
    })
    
    return ChatResponse(
        response=ai_response["response"],
        conversation_id=conversation_id,
        message_id=message_id,
        assessment_stage=ai_response["assessment_stage"],
        symptoms_collected=ai_response["symptoms_collected"],
        needs_diagnosis=ai_response["needs_diagnosis"]
    )

@app.get("/conversation/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationHistory(
        conversation_id=conversation_id,
        messages=conversations_db[conversation_id]["messages"]
    )

@app.get("/conversations/{user_id}")
async def get_user_conversations(user_id: str):
    """Get all conversations for a user"""
    user_conversations = []
    for conv_id, conv_data in conversations_db.items():
        if conv_data["user_id"] == user_id:
            user_conversations.append({
                "conversation_id": conv_id,
                "message_count": len(conv_data["messages"]),
                "last_message": conv_data["messages"][-1] if conv_data["messages"] else None
            })
    
    return {"user_id": user_id, "conversations": user_conversations}

@app.post("/analyze/{conversation_id}")
async def analyze_conversation(conversation_id: str):
    """Generate comprehensive diagnostic analysis for a conversation"""
    try:
        analysis = ai_agent.generate_diagnostic_analysis(conversation_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/conversation/{conversation_id}/summary")
async def get_conversation_summary(conversation_id: str):
    """Get summary of a conversation"""
    try:
        summary = ai_agent.get_conversation_summary(conversation_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chat-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
