from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

app = FastAPI(title="HealPrint Diagnostic Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SymptomAnalysis(BaseModel):
    skin_symptoms: List[str]
    hair_symptoms: List[str]
    lifestyle_factors: List[str]
    user_id: str

class DiagnosticResult(BaseModel):
    analysis_id: str
    user_id: str
    primary_concerns: List[str]
    likely_causes: List[str]
    recommendations: List[str]
    confidence_score: float
    next_steps: List[str]

# Simple diagnostic patterns for MVP
DIAGNOSTIC_PATTERNS = {
    "acne": {
        "triggers": ["stress", "hormonal", "diet", "gut_health"],
        "recommendations": ["Check hormone levels", "Improve gut health", "Manage stress", "Review diet"]
    },
    "hair_loss": {
        "triggers": ["iron_deficiency", "thyroid", "stress", "hormonal"],
        "recommendations": ["Iron level test", "Thyroid function test", "Stress management", "Nutritional support"]
    },
    "dry_skin": {
        "triggers": ["dehydration", "thyroid", "vitamin_deficiency", "environmental"],
        "recommendations": ["Increase water intake", "Check thyroid", "Vitamin D test", "Humidifier use"]
    }
}

@app.get("/")
async def root():
    return {"service": "HealPrint Diagnostic Service", "status": "running"}

@app.post("/analyze", response_model=DiagnosticResult)
async def analyze_symptoms(analysis: SymptomAnalysis):
    """Analyze symptoms and provide diagnostic insights"""
    
    analysis_id = f"analysis_{analysis.user_id}_{len(analysis.skin_symptoms)}"
    
    # Simple pattern matching for MVP
    primary_concerns = []
    likely_causes = []
    recommendations = []
    confidence_score = 0.0
    
    # Analyze skin symptoms
    for symptom in analysis.skin_symptoms:
        symptom_lower = symptom.lower()
        if "acne" in symptom_lower or "pimple" in symptom_lower:
            primary_concerns.append("Acne/breakouts")
            likely_causes.extend(DIAGNOSTIC_PATTERNS["acne"]["triggers"])
            recommendations.extend(DIAGNOSTIC_PATTERNS["acne"]["recommendations"])
            confidence_score += 0.3
        elif "dry" in symptom_lower:
            primary_concerns.append("Dry skin")
            likely_causes.extend(DIAGNOSTIC_PATTERNS["dry_skin"]["triggers"])
            recommendations.extend(DIAGNOSTIC_PATTERNS["dry_skin"]["recommendations"])
            confidence_score += 0.2
    
    # Analyze hair symptoms
    for symptom in analysis.hair_symptoms:
        symptom_lower = symptom.lower()
        if "loss" in symptom_lower or "thin" in symptom_lower:
            primary_concerns.append("Hair loss/thinning")
            likely_causes.extend(DIAGNOSTIC_PATTERNS["hair_loss"]["triggers"])
            recommendations.extend(DIAGNOSTIC_PATTERNS["hair_loss"]["recommendations"])
            confidence_score += 0.3
    
    # Analyze lifestyle factors
    for factor in analysis.lifestyle_factors:
        factor_lower = factor.lower()
        if "stress" in factor_lower:
            likely_causes.append("High stress levels")
            recommendations.append("Implement stress management techniques")
            confidence_score += 0.1
        elif "poor_diet" in factor_lower or "junk" in factor_lower:
            likely_causes.append("Nutritional deficiencies")
            recommendations.append("Improve diet quality and consider supplements")
            confidence_score += 0.1
    
    # Remove duplicates
    likely_causes = list(set(likely_causes))
    recommendations = list(set(recommendations))
    
    # Generate next steps
    next_steps = [
        "Continue tracking symptoms daily",
        "Consider consulting a healthcare provider for testing",
        "Implement recommended lifestyle changes",
        "Schedule follow-up analysis in 2 weeks"
    ]
    
    # Cap confidence score
    confidence_score = min(confidence_score, 1.0)
    
    return DiagnosticResult(
        analysis_id=analysis_id,
        user_id=analysis.user_id,
        primary_concerns=primary_concerns,
        likely_causes=likely_causes,
        recommendations=recommendations,
        confidence_score=confidence_score,
        next_steps=next_steps
    )

@app.get("/patterns")
async def get_diagnostic_patterns():
    """Get available diagnostic patterns"""
    return {"patterns": DIAGNOSTIC_PATTERNS}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "diagnostic-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
