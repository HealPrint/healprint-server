# HealPrint AI - Microservices Architecture

## Overview
HealPrint AI is a chat-based digital health platform that connects internal health symptoms with external skin and hair problems using AI.

## MVP Microservices

### 1. User Service (Port 8001)
- User registration and authentication
- User profile management
- Simple token-based auth for MVP

### 2. Chat Service (Port 8002)
- **Professional AI Health Agent** using GPT-4o through OpenRouter
- Advanced symptom pattern recognition
- Comprehensive diagnostic tools and health assessment
- Conversation management with assessment stages
- Holistic health analysis connecting internal and external symptoms

### 3. Diagnostic Service (Port 8003)
- Symptom analysis and pattern matching
- Health recommendations
- Confidence scoring

### 4. API Gateway (Port 8000)
- Routes requests to appropriate services
- Health monitoring
- CORS handling

## Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# Start all services
docker-compose up --build

# Access API Gateway
http://localhost:8000
```

### Option 2: Individual Services
```bash
# Terminal 1 - User Service
cd user-service
pip install -r requirements.txt
python main.py

# Terminal 2 - Chat Service
cd chat-service
pip install -r requirements.txt
python main.py

# Terminal 3 - Diagnostic Service
cd diagnostic-service
pip install -r requirements.txt
python main.py

# Terminal 4 - API Gateway
cd api-gateway
pip install -r requirements.txt
python main.py
```

## API Endpoints

### User Service
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /profile/{user_id}` - Get user profile

### Chat Service
- `POST /chat` - Send message to AI
- `GET /conversation/{conversation_id}` - Get conversation history

### Diagnostic Service
- `POST /analyze` - Analyze symptoms
- `GET /patterns` - Get diagnostic patterns

### API Gateway
- `GET /health` - Check all services health
- All other endpoints are proxied to appropriate services

## Testing the MVP

1. **Register a user:**
```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@healprint.com", "password": "password123", "name": "Test User"}'
```

2. **Start a chat with the AI Health Agent:**
```bash
curl -X POST "http://localhost:8000/chat/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have been experiencing acne on my face and hair loss. I feel stressed and tired all the time.",
    "user_id": "user_1"
  }'
```

3. **Get diagnostic analysis:**
```bash
curl -X POST "http://localhost:8000/chat/analyze/conv_user_1_0" \
  -H "Content-Type: application/json"
```

4. **Analyze symptoms (legacy endpoint):**
```bash
curl -X POST "http://localhost:8000/diagnostic/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "skin_symptoms": ["acne", "dry patches"],
    "hair_symptoms": ["hair loss"],
    "lifestyle_factors": ["stress", "poor diet"],
    "user_id": "user_1"
  }'
```

## AI Health Agent Features

### **Professional Health Assessment**
- **GPT-4o Integration**: Uses OpenAI's most advanced model through OpenRouter
- **Holistic Analysis**: Connects internal health (hormones, nutrition, stress) with external symptoms (skin, hair)
- **Pattern Recognition**: Identifies complex symptom patterns and root causes
- **Conversation Management**: Tracks assessment stages and symptom collection

### **Comprehensive Diagnostic Tools**
- **200+ Symptoms**: Covers skin, hair, and internal health indicators
- **Health Factors**: Nutritional, hormonal, stress, gut health, environmental
- **Diagnostic Patterns**: Acne patterns, hair loss patterns, aging patterns
- **Medical Tests**: Recommended tests for different health concerns
- **Urgency Levels**: Proper triage and referral recommendations

### **Professional Medical Awareness**
- **Safety First**: Never provides medical diagnoses, always recommends professional consultation
- **Evidence-Based**: Uses medical knowledge and research-backed recommendations
- **Personalized**: Tailored advice based on individual health profiles
- **Actionable**: Provides specific, practical steps for improvement

## Next Steps for Development

1. **Add Database**: Replace in-memory storage with PostgreSQL
2. **Add Authentication**: Implement JWT tokens
3. **Enhance AI**: Add more specialized health models
4. **Add More Services**: Payment, notifications, expert marketplace
5. **Add Monitoring**: Logging, metrics, health checks
6. **Add Multilingual Support**: Support for multiple languages

## Architecture Benefits

- **Independent Development**: Each service can be developed separately
- **Independent Deployment**: Deploy services independently
- **Scalability**: Scale services based on demand
- **Technology Flexibility**: Use different tech stacks per service
- **Fault Isolation**: One service failure doesn't affect others
