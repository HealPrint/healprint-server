"""
HealPrint AI Diagnostic Tools
Comprehensive health assessment tools for the AI agent
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json
import os

class SymptomCategory(BaseModel):
    category: str
    symptoms: List[str]
    severity_levels: List[str]
    associated_factors: List[str]

class DiagnosticQuestion(BaseModel):
    question_id: str
    question: str
    category: str
    response_type: str  # "multiple_choice", "scale", "text", "yes_no"
    options: Optional[List[str]] = None
    follow_up_questions: Optional[List[str]] = None

class HealthFactor(BaseModel):
    factor: str
    impact_level: str  # "high", "medium", "low"
    related_symptoms: List[str]
    recommendations: List[str]

class DiagnosticResult(BaseModel):
    primary_concerns: List[str]
    likely_causes: List[str]
    confidence_score: float
    recommendations: List[str]
    next_steps: List[str]
    urgency_level: str  # "low", "medium", "high", "urgent"
    referral_needed: bool
    tests_suggested: List[str]

# Load diagnostic data from JSON file
def load_diagnostic_data():
    """Load diagnostic data from JSON file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'diagnostic_data.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to basic data if JSON file not found
        return {
            "symptom_categories": {},
            "diagnostic_questions": [],
            "health_factors": {},
            "diagnostic_patterns": {},
            "recommended_tests": {}
        }

# Load the diagnostic data
DIAGNOSTIC_DATA = load_diagnostic_data()

# Fallback diagnostic data structure (if JSON loading fails)
FALLBACK_DIAGNOSTIC_DATA = {
    "symptom_categories": {
        "skin_conditions": {
            "category": "Skin Conditions",
            "symptoms": [
                "acne", "blackheads", "whiteheads", "cysts", "nodules",
                "dry_skin", "oily_skin", "sensitive_skin", "redness", "inflammation",
                "rashes", "eczema", "psoriasis", "dermatitis", "rosacea",
                "hyperpigmentation", "dark_spots", "melasma", "age_spots",
                "wrinkles", "fine_lines", "sagging", "dull_skin", "uneven_texture"
            ],
            "severity_levels": ["mild", "moderate", "severe"],
            "associated_factors": ["hormonal", "dietary", "stress", "environmental", "genetic"]
        },
        "hair_conditions": {
            "category": "Hair Conditions",
            "symptoms": [
                "hair_loss", "thinning", "bald_patches", "receding_hairline",
                "dry_hair", "oily_hair", "brittle_hair", "split_ends",
                "dandruff", "scalp_irritation", "scalp_psoriasis", "scalp_eczema",
                "slow_growth", "excessive_shedding", "breakage", "frizz"
            ],
            "severity_levels": ["mild", "moderate", "severe"],
            "associated_factors": ["nutritional", "hormonal", "stress", "genetic", "environmental"]
        },
        "internal_health": {
            "category": "Internal Health Indicators",
            "symptoms": [
                "digestive_issues", "bloating", "constipation", "diarrhea", "acid_reflux",
                "fatigue", "low_energy", "sleep_issues", "insomnia", "poor_sleep_quality",
                "mood_swings", "anxiety", "depression", "irritability", "brain_fog",
                "weight_changes", "unexplained_weight_gain", "unexplained_weight_loss",
                "hormonal_imbalances", "irregular_cycles", "pms_symptoms", "menopause_symptoms"
            ],
            "severity_levels": ["mild", "moderate", "severe"],
            "associated_factors": ["lifestyle", "dietary", "stress", "genetic", "environmental"]
        }
    },
    
    "diagnostic_questions": [
        {
            "question_id": "skin_primary_concern",
            "question": "What is your primary skin concern right now?",
            "category": "skin_conditions",
            "response_type": "multiple_choice",
            "options": ["acne", "dryness", "oily skin", "sensitivity", "aging", "pigmentation", "other"],
            "follow_up_questions": ["skin_severity", "skin_duration"]
        },
        {
            "question_id": "hair_primary_concern",
            "question": "What is your main hair concern?",
            "category": "hair_conditions",
            "response_type": "multiple_choice",
            "options": ["hair loss", "thinning", "dryness", "dandruff", "slow growth", "breakage", "other"],
            "follow_up_questions": ["hair_severity", "hair_duration"]
        },
        {
            "question_id": "stress_level",
            "question": "How would you rate your current stress level?",
            "category": "internal_health",
            "response_type": "scale",
            "options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            "follow_up_questions": ["stress_sources", "stress_management"]
        },
        {
            "question_id": "sleep_quality",
            "question": "How would you describe your sleep quality?",
            "category": "internal_health",
            "response_type": "multiple_choice",
            "options": ["excellent", "good", "fair", "poor", "very poor"],
            "follow_up_questions": ["sleep_duration", "sleep_issues"]
        },
        {
            "question_id": "diet_quality",
            "question": "How would you rate your current diet?",
            "category": "internal_health",
            "response_type": "multiple_choice",
            "options": ["excellent", "good", "fair", "poor", "very poor"],
            "follow_up_questions": ["diet_details", "supplements"]
        },
        {
            "question_id": "digestive_health",
            "question": "Do you experience any digestive issues?",
            "category": "internal_health",
            "response_type": "yes_no",
            "follow_up_questions": ["digestive_symptoms", "digestive_frequency"]
        },
        {
            "question_id": "hormonal_changes",
            "question": "Have you noticed any hormonal changes recently?",
            "category": "internal_health",
            "response_type": "yes_no",
            "follow_up_questions": ["hormonal_symptoms", "cycle_changes"]
        }
    ],
    
    "health_factors": {
        "nutritional": {
            "factor": "Nutritional Deficiencies",
            "impact_level": "high",
            "related_symptoms": ["hair_loss", "dry_skin", "fatigue", "brittle_hair", "slow_healing"],
            "recommendations": [
                "Get comprehensive blood work (iron, B12, vitamin D, zinc)",
                "Increase protein intake",
                "Add omega-3 fatty acids",
                "Consider multivitamin supplement",
                "Eat more leafy greens and colorful vegetables"
            ]
        },
        "hormonal": {
            "factor": "Hormonal Imbalances",
            "impact_level": "high",
            "related_symptoms": ["acne", "hair_loss", "mood_swings", "weight_changes", "irregular_cycles"],
            "recommendations": [
                "Get hormone panel testing (thyroid, sex hormones)",
                "Track menstrual cycles",
                "Manage stress levels",
                "Consider adaptogenic herbs",
                "Consult endocrinologist if severe"
            ]
        },
        "stress": {
            "factor": "Chronic Stress",
            "impact_level": "high",
            "related_symptoms": ["acne", "hair_loss", "fatigue", "sleep_issues", "inflammation"],
            "recommendations": [
                "Implement stress management techniques",
                "Practice meditation or yoga",
                "Get adequate sleep",
                "Consider therapy or counseling",
                "Engage in regular physical activity"
            ]
        },
        "digestive": {
            "factor": "Gut Health Issues",
            "impact_level": "medium",
            "related_symptoms": ["acne", "skin_inflammation", "bloating", "fatigue", "mood_issues"],
            "recommendations": [
                "Get gut health testing",
                "Eliminate inflammatory foods",
                "Add probiotics and prebiotics",
                "Manage stress",
                "Consider elimination diet"
            ]
        },
        "environmental": {
            "factor": "Environmental Factors",
            "impact_level": "medium",
            "related_symptoms": ["dry_skin", "sensitivity", "premature_aging", "inflammation"],
            "recommendations": [
                "Use gentle, fragrance-free products",
                "Protect skin from UV damage",
                "Improve indoor air quality",
                "Use humidifier",
                "Avoid harsh chemicals"
            ]
        }
    },
    
    "diagnostic_patterns": {
        "acne_patterns": {
            "hormonal_acne": {
                "symptoms": ["acne_along_jawline", "cystic_acne", "irregular_cycles", "mood_swings"],
                "likely_causes": ["hormonal_imbalance", "pcos", "thyroid_issues"],
                "confidence_threshold": 0.8
            },
            "stress_acne": {
                "symptoms": ["acne_during_stress", "inflammation", "poor_sleep", "anxiety"],
                "likely_causes": ["cortisol_imbalance", "inflammation", "poor_immune_function"],
                "confidence_threshold": 0.7
            },
            "dietary_acne": {
                "symptoms": ["acne_after_meals", "digestive_issues", "bloating", "inflammation"],
                "likely_causes": ["food_sensitivities", "gut_dysbiosis", "inflammation"],
                "confidence_threshold": 0.6
            }
        },
        "hair_loss_patterns": {
            "nutritional_hair_loss": {
                "symptoms": ["overall_thinning", "brittle_hair", "fatigue", "pale_skin"],
                "likely_causes": ["iron_deficiency", "b12_deficiency", "protein_deficiency"],
                "confidence_threshold": 0.8
            },
            "hormonal_hair_loss": {
                "symptoms": ["thinning_at_crown", "irregular_cycles", "weight_changes", "mood_swings"],
                "likely_causes": ["thyroid_issues", "pcos", "menopause", "hormonal_imbalance"],
                "confidence_threshold": 0.8
            },
            "stress_hair_loss": {
                "symptoms": ["sudden_shedding", "stress_events", "poor_sleep", "anxiety"],
                "likely_causes": ["telogen_effluvium", "cortisol_imbalance", "inflammation"],
                "confidence_threshold": 0.7
            }
        }
    },
    
    "recommended_tests": {
        "basic_panel": [
            "Complete Blood Count (CBC)",
            "Comprehensive Metabolic Panel (CMP)",
            "Iron studies (ferritin, TIBC, iron saturation)",
            "Vitamin D (25-hydroxyvitamin D)",
            "B12 and folate levels"
        ],
        "hormonal_panel": [
            "Thyroid function (TSH, T3, T4, reverse T3)",
            "Sex hormones (estradiol, progesterone, testosterone)",
            "Cortisol (AM and PM levels)",
            "Insulin and glucose levels"
        ],
        "advanced_panel": [
            "Food sensitivity testing",
            "Gut microbiome analysis",
            "Inflammatory markers (CRP, ESR)",
            "Heavy metal testing",
            "Nutrient absorption testing"
        ]
    }
}

def get_diagnostic_questions_by_category(category: str) -> List[DiagnosticQuestion]:
    """Get diagnostic questions for a specific category"""
    questions = []
    for q in DIAGNOSTIC_DATA["diagnostic_questions"]:
        if q["category"] == category:
            questions.append(DiagnosticQuestion(**q))
    return questions

def analyze_symptom_patterns(symptoms: Dict[str, Any]) -> DiagnosticResult:
    """Analyze symptoms and return diagnostic result"""
    # This would be implemented with the AI model
    # For now, return a basic analysis
    return DiagnosticResult(
        primary_concerns=["Analysis in progress"],
        likely_causes=["AI analysis required"],
        confidence_score=0.0,
        recommendations=["Continue conversation"],
        next_steps=["Answer more questions"],
        urgency_level="low",
        referral_needed=False,
        tests_suggested=[]
    )

def get_health_factors_by_symptoms(symptoms: List[str]) -> List[HealthFactor]:
    """Get relevant health factors based on symptoms"""
    factors = []
    for factor_name, factor_data in DIAGNOSTIC_DATA["health_factors"].items():
        if any(symptom in factor_data["related_symptoms"] for symptom in symptoms):
            factors.append(HealthFactor(**factor_data))
    return factors
