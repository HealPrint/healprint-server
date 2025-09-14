from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

app = FastAPI(title="HealPrint API Gateway", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs (in production, use environment variables or service discovery)
USER_SERVICE_URL = "http://localhost:8001"
CHAT_SERVICE_URL = "http://localhost:8002"
DIAGNOSTIC_SERVICE_URL = "http://localhost:8003"

@app.get("/")
async def root():
    return {
        "service": "HealPrint API Gateway",
        "status": "running",
        "services": {
            "user-service": USER_SERVICE_URL,
            "chat-service": CHAT_SERVICE_URL,
            "diagnostic-service": DIAGNOSTIC_SERVICE_URL
        }
    }

@app.get("/health")
async def health_check():
    """Check health of all services"""
    services_status = {}
    
    async with httpx.AsyncClient() as client:
        # Check user service
        try:
            response = await client.get(f"{USER_SERVICE_URL}/health", timeout=5.0)
            services_status["user-service"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services_status["user-service"] = "unreachable"
        
        # Check chat service
        try:
            response = await client.get(f"{CHAT_SERVICE_URL}/health", timeout=5.0)
            services_status["chat-service"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services_status["chat-service"] = "unreachable"
        
        # Check diagnostic service
        try:
            response = await client.get(f"{DIAGNOSTIC_SERVICE_URL}/health", timeout=5.0)
            services_status["diagnostic-service"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services_status["diagnostic-service"] = "unreachable"
    
    return {
        "gateway": "healthy",
        "services": services_status
    }

# User Service Routes
@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_service_proxy(path: str, request):
    """Proxy requests to user service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=f"{USER_SERVICE_URL}/users/{path}",
                headers=dict(request.headers),
                content=await request.body()
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User service error: {str(e)}")

# Chat Service Routes
@app.api_route("/chat/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def chat_service_proxy(path: str, request):
    """Proxy requests to chat service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=f"{CHAT_SERVICE_URL}/{path}",
                headers=dict(request.headers),
                content=await request.body()
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

# Diagnostic Service Routes
@app.api_route("/diagnostic/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def diagnostic_service_proxy(path: str, request):
    """Proxy requests to diagnostic service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=f"{DIAGNOSTIC_SERVICE_URL}/{path}",
                headers=dict(request.headers),
                content=await request.body()
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Diagnostic service error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
