"""
HealPrint AI Health Agent
Professional health AI agent using OpenAI through OpenRouter
"""

from openai import OpenAI
from typing import Dict, List, Any, Optional
import json
import os
from config import OPENROUTER_API_KEY, SITE_URL, SITE_NAME
from diagnostic_tools import DIAGNOSTIC_DATA, get_health_factors_by_symptoms

class HealPrintAIAgent:
    def __init__(self):
        self.client = None
        if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_openrouter_api_key_here":
            try:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=OPENROUTER_API_KEY,
                )
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            print("Warning: No valid OpenRouter API key provided")
        
        self.conversation_history = {}
        
    def get_system_prompt(self) -> str:
        """Get the system prompt for the HealPrint AI agent"""
        return f"""You are HealPrint AI, a professional health and wellness AI agent specializing in connecting internal health symptoms with external skin and hair problems. You are an expert in:

1. Holistic Health Assessment: You understand the deep connections between internal health (hormones, nutrition, stress, gut health) and external appearance (skin, hair).

2. Symptom Pattern Recognition: You can identify patterns that link seemingly unrelated symptoms to root causes.

3. Personalized Recommendations: You provide tailored advice based on individual health profiles.

4. Professional Medical Awareness: You know when to recommend professional medical consultation and appropriate tests.

Your Approach:
- Ask thoughtful, targeted questions to understand the full health picture
- Connect internal and external symptoms to identify root causes
- Provide evidence-based recommendations
- Always prioritize safety and recommend professional consultation when needed
- Be empathetic, supportive, and non-judgmental
- Focus on holistic, sustainable solutions
- Build on previous responses and maintain conversation context
- When users respond to your questions, acknowledge their answer and ask follow-up questions
- Reference previous parts of the conversation to show you're listening
- Guide the conversation naturally from one topic to the next

Available Diagnostic Tools:
- Comprehensive symptom assessment across skin, hair, and internal health
- Pattern recognition for common health-skin/hair connections
- Access to detailed health factor analysis
- Knowledge of recommended medical tests and professional referrals

Important Guidelines:
- Never provide specific medical diagnoses
- Always recommend professional consultation for serious concerns
- Focus on lifestyle, nutrition, and wellness approaches
- Be encouraging and supportive
- Ask follow-up questions to get complete picture
- Provide actionable, practical advice
- Use clean, simple formatting without markdown bold syntax
- Avoid using ** for emphasis - use plain text instead
- Always acknowledge the user's previous response before asking new questions
- Build naturally on what the user has shared
- Show that you're listening by referencing their specific answers
- Guide the conversation flow logically from one topic to the next
- When you provide numbered options and user selects one, acknowledge their choice and ask follow-up questions about that specific option
- If user responds with numbers (1, 2, 3) or mentions "option", treat it as a selection from your previous options
- Always build on the user's selection to gather more detailed information

Your Goal: Help users understand the connection between their internal health and external appearance, guiding them toward better health and wellness through personalized insights and recommendations.

Remember: You're not replacing medical professionals, but you're providing valuable insights that can guide users toward better health decisions and appropriate professional care."""

    def get_diagnostic_tools_prompt(self) -> str:
        """Get the diagnostic tools available to the AI agent"""
        return f"""
Available Diagnostic Tools and Data:

Symptom Categories:
{json.dumps(DIAGNOSTIC_DATA['symptom_categories'], indent=2)}

Key Health Factors to Consider:
{json.dumps(DIAGNOSTIC_DATA['health_factors'], indent=2)}

Common Diagnostic Patterns:
{json.dumps(DIAGNOSTIC_DATA['diagnostic_patterns'], indent=2)}

Recommended Tests:
{json.dumps(DIAGNOSTIC_DATA['recommended_tests'], indent=2)}

Use this information to guide your questions and provide comprehensive health insights.
"""

    def chat_with_user(self, user_message: str, user_id: str, conversation_id: str) -> Dict[str, Any]:
        """Main chat function with the AI agent"""
        
        # Initialize conversation if new
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = {
                "user_id": user_id,
                "messages": [],
                "symptoms_collected": {},
                "assessment_stage": "initial"
            }
        
        # Add user message to history
        self.conversation_history[conversation_id]["messages"].append({
            "role": "user",
            "content": user_message
        })
        
        # Get conversation context
        conversation = self.conversation_history[conversation_id]
        messages = conversation["messages"]
        
        # Prepare messages for OpenAI using proper chat template
        system_prompt = self.get_system_prompt()
        diagnostic_tools = self.get_diagnostic_tools_prompt()
        
        # Add conversation context analysis
        conversation_context = self._analyze_conversation_context(conversation)
        
        # Format messages using the proper chat template
        formatted_messages = self._format_messages_for_openai(
            system_prompt, 
            diagnostic_tools, 
            messages,
            conversation_context
        )
        
        try:
            # Check if client is available
            if self.client is None:
                return self._get_fallback_response(conversation_id, conversation)
            
            # Call OpenAI API
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": SITE_URL,
                    "X-Title": SITE_NAME,
                },
                model="openai/gpt-4o-mini",  # Using cheaper model
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=500  # Reduced to save credits
            )
            
            ai_response = completion.choices[0].message.content
            
            # Add AI response to conversation history
            conversation["messages"].append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Analyze if we should move to diagnostic stage
            assessment_stage = self._analyze_conversation_stage(conversation)
            conversation["assessment_stage"] = assessment_stage
            
            # Extract symptoms if mentioned
            symptoms = self._extract_symptoms(user_message)
            if symptoms:
                conversation["symptoms_collected"].update(symptoms)
            
            return {
                "response": ai_response,
                "conversation_id": conversation_id,
                "assessment_stage": assessment_stage,
                "symptoms_collected": conversation["symptoms_collected"],
                "needs_diagnosis": assessment_stage == "diagnostic_ready"
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle specific API credit errors
            if "402" in error_msg or "credits" in error_msg.lower():
                return {
                    "response": "I'm currently unable to process your request due to API credit limitations. Please contact support or try again later. For immediate assistance, please reach out to our support team at support@healprint.xyz.",
                    "conversation_id": conversation_id,
                    "assessment_stage": conversation["assessment_stage"],
                    "symptoms_collected": conversation["symptoms_collected"],
                    "needs_diagnosis": False,
                    "error": "API credits exhausted"
                }
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                return {
                    "response": "I'm currently unable to process your request due to API authentication issues. Please contact support at support@healprint.xyz.",
                    "conversation_id": conversation_id,
                    "assessment_stage": conversation["assessment_stage"],
                    "symptoms_collected": conversation["symptoms_collected"],
                    "needs_diagnosis": False,
                    "error": "API authentication failed"
                }
            else:
                return {
                    "response": f"I apologize, I'm experiencing technical difficulties. Please try again later or contact support at support@healprint.xyz. Error: {error_msg}",
                    "conversation_id": conversation_id,
                    "assessment_stage": conversation["assessment_stage"],
                    "symptoms_collected": conversation["symptoms_collected"],
                    "needs_diagnosis": False,
                    "error": f"API error: {error_msg}"
                }
    
    def _get_fallback_response(self, conversation_id: str, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback response when API is not available"""
        user_message = conversation["messages"][-1]["content"].lower()
        
        # Simple keyword-based responses
        if any(word in user_message for word in ["hello", "hi", "hey", "start"]):
            response = "Hello! I'm HealPrint AI, your health and wellness assistant. I'm currently experiencing some technical difficulties with my AI processing, but I'm here to help guide you through your health journey. Please describe any skin, hair, or health concerns you'd like to discuss."
        elif any(word in user_message for word in ["skin", "acne", "rash", "dry", "oily"]):
            response = "I understand you're concerned about skin issues. While I'm experiencing technical difficulties with my AI analysis, I can still provide general guidance. Common skin concerns often relate to diet, stress, hormones, or skincare routines. Would you like to share more details about your specific skin concerns?"
        elif any(word in user_message for word in ["hair", "hair loss", "thinning", "dry hair"]):
            response = "Hair health is often connected to internal factors like nutrition, stress, and hormonal balance. While I'm having technical difficulties with my AI processing, I can still offer general advice. What specific hair concerns are you experiencing?"
        elif any(word in user_message for word in ["help", "support", "contact"]):
            response = "I'm here to help! While I'm experiencing some technical difficulties with my AI processing, our support team is available to assist you. You can reach us at support@healprint.xyz or try again later when the service is fully restored."
        else:
            response = "Thank you for your message. I'm currently experiencing some technical difficulties with my AI processing capabilities, but I'm still here to help guide you through your health journey. Please feel free to describe any health concerns you have, and I'll do my best to provide helpful guidance."
        
        # Add response to conversation
        conversation["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        return {
            "response": response,
            "conversation_id": conversation_id,
            "assessment_stage": conversation["assessment_stage"],
            "symptoms_collected": conversation["symptoms_collected"],
            "needs_diagnosis": False,
            "fallback_mode": True
        }
    
    def _analyze_conversation_stage(self, conversation: Dict[str, Any]) -> str:
        """Analyze conversation to determine assessment stage"""
        messages = conversation["messages"]
        symptoms = conversation["symptoms_collected"]
        
        # Count meaningful exchanges (user + assistant pairs)
        meaningful_exchanges = len([m for m in messages if m["role"] == "assistant"])
        
        # If we have collected enough symptoms AND had meaningful conversation
        if len(symptoms) >= 3 and meaningful_exchanges >= 2:
            return "diagnostic_ready"
        
        # If we have some symptoms but need more info
        if len(symptoms) >= 1 or meaningful_exchanges >= 1:
            return "gathering_info"
        
        # Initial stage
        return "initial"
    
    def _extract_symptoms(self, message: str) -> Dict[str, Any]:
        """Extract symptoms mentioned in the message"""
        symptoms = {}
        message_lower = message.lower()
        
        # Check for skin symptoms
        for category, data in DIAGNOSTIC_DATA["symptom_categories"].items():
            for symptom in data["symptoms"]:
                if symptom.replace("_", " ") in message_lower:
                    symptoms[symptom] = {
                        "category": category,
                        "mentioned": True
                    }
        
        return symptoms
    
    def _analyze_conversation_context(self, conversation: Dict[str, Any]) -> str:
        """Analyze conversation context to help AI understand what user is responding to"""
        messages = conversation["messages"]
        symptoms = conversation["symptoms_collected"]
        assessment_stage = conversation["assessment_stage"]
        
        context_parts = []
        
        # Add current assessment stage
        context_parts.append(f"Current Assessment Stage: {assessment_stage}")
        
        # Add collected symptoms
        if symptoms:
            symptom_list = list(symptoms.keys())
            context_parts.append(f"Identified Symptoms: {', '.join(symptom_list)}")
        
        # Analyze recent conversation flow with more detail
        if len(messages) >= 2:
            last_assistant_message = None
            last_user_message = None
            
            # Get the last assistant and user messages
            for msg in reversed(messages):
                if msg["role"] == "assistant" and last_assistant_message is None:
                    last_assistant_message = msg["content"]
                elif msg["role"] == "user" and last_user_message is None:
                    last_user_message = msg["content"]
            
            if last_assistant_message and last_user_message:
                # Check if last assistant message contained numbered options or choices
                if any(char.isdigit() for char in last_assistant_message) and ("." in last_assistant_message or ":" in last_assistant_message):
                    context_parts.append("Previous Context: User is responding to specific options/choices you provided")
                    # Extract the options to help AI understand what user chose
                    lines = last_assistant_message.split('\n')
                    options = [line.strip() for line in lines if line.strip() and (line.strip()[0].isdigit() or ':' in line)]
                    if options:
                        context_parts.append(f"Options provided: {' | '.join(options[:3])}")  # Show first 3 options
                elif "?" in last_assistant_message:
                    context_parts.append("Previous Context: User is responding to questions you asked")
                else:
                    context_parts.append("Previous Context: User is providing additional information")
                
                # Check if user's response seems to be selecting an option
                user_lower = last_user_message.lower()
                if any(word in user_lower for word in ["option", "choice", "select", "choose", "1", "2", "3", "4", "5"]):
                    context_parts.append("User Response Type: Appears to be selecting from provided options")
        
        # Add conversation length context
        message_count = len(messages)
        if message_count <= 2:
            context_parts.append("Conversation Status: Early stage - focus on gathering basic information")
        elif message_count <= 6:
            context_parts.append("Conversation Status: Mid-stage - dive deeper into specific symptoms")
        else:
            context_parts.append("Conversation Status: Advanced stage - ready for analysis or recommendations")
        
        return " | ".join(context_parts)
    
    def _format_messages_for_openai(self, system_prompt: str, diagnostic_tools: str, messages: List[Dict[str, str]], conversation_context: str = "") -> List[Dict[str, str]]:
        """Format messages using the proper chat template format"""
        from datetime import datetime
        
        # Get current date
        current_date = datetime.now().strftime("%d %b %Y")
        
        # Create the formatted message using the chat template
        formatted_content = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        formatted_content += f"Cutting Knowledge Date: December 2023\n"
        formatted_content += f"Today Date: {current_date}\n\n"
        formatted_content += f"{system_prompt}\n\n"
        formatted_content += f"{diagnostic_tools}\n\n"
        
        # Add conversation context if available
        if conversation_context:
            formatted_content += f"CONVERSATION CONTEXT: {conversation_context}\n\n"
        
        # Add specific instruction for option handling
        if "responding to specific options" in conversation_context:
            formatted_content += f"IMPORTANT: The user just responded to options you provided. Acknowledge their choice and ask follow-up questions about their selection.\n\n"
        
        formatted_content += f"<|eot_id|>"
        
        # Add conversation history
        for message in messages[-10:]:  # Last 10 messages to stay within context
            if message["role"] == "user":
                formatted_content += f"<|start_header_id|>user<|end_header_id|>\n\n{message['content']}<|eot_id|>"
            elif message["role"] == "assistant":
                formatted_content += f"<|start_header_id|>assistant<|end_header_id|>\n\n{message['content']}<|eot_id|>"
        
        # Add the current user message
        if messages:
            current_message = messages[-1]
            if current_message["role"] == "user":
                formatted_content += f"<|start_header_id|>user<|end_header_id|>\n\n{current_message['content']}<|eot_id|>"
        
        # Add assistant header for response
        formatted_content += f"<|start_header_id|>assistant<|end_header_id|>"
        
        return [{"role": "user", "content": formatted_content}]
    
    def generate_diagnostic_analysis(self, conversation_id: str) -> Dict[str, Any]:
        """Generate comprehensive diagnostic analysis"""
        if conversation_id not in self.conversation_history:
            return {"error": "Conversation not found"}
        
        conversation = self.conversation_history[conversation_id]
        symptoms = conversation["symptoms_collected"]
        
        if not symptoms:
            return {"error": "No symptoms collected for analysis"}
        
        # Get relevant health factors
        symptom_list = list(symptoms.keys())
        health_factors = get_health_factors_by_symptoms(symptom_list)
        
        # Create analysis prompt
        analysis_prompt = f"""
Based on the collected symptoms and conversation, provide a comprehensive health analysis:

**Collected Symptoms:**
{json.dumps(symptoms, indent=2)}

**Relevant Health Factors:**
{json.dumps([factor.dict() for factor in health_factors], indent=2)}

Please provide:
1. Primary health concerns identified
2. Likely root causes
3. Confidence level (0-1)
4. Specific recommendations
5. Next steps
6. Whether professional consultation is needed
7. Suggested tests or evaluations

Format your response as a structured analysis.
"""
        
        try:
            # Format analysis prompt using chat template
            formatted_analysis_messages = self._format_messages_for_openai(
                self.get_system_prompt(),
                self.get_diagnostic_tools_prompt(),
                [{"role": "user", "content": analysis_prompt}],
                f"Analysis Mode: {conversation['assessment_stage']} | Symptoms: {list(symptoms.keys())}"
            )
            
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": SITE_URL,
                    "X-Title": SITE_NAME,
                },
                model="openai/gpt-4o",
                messages=formatted_analysis_messages,
                temperature=0.3,
                max_tokens=1500
            )
            
            analysis = completion.choices[0].message.content
            
            return {
                "analysis": analysis,
                "symptoms_analyzed": symptoms,
                "health_factors": [factor.dict() for factor in health_factors],
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "symptoms_analyzed": symptoms
            }
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get summary of conversation"""
        if conversation_id not in self.conversation_history:
            return {"error": "Conversation not found"}
        
        conversation = self.conversation_history[conversation_id]
        return {
            "conversation_id": conversation_id,
            "user_id": conversation["user_id"],
            "message_count": len(conversation["messages"]),
            "symptoms_collected": conversation["symptoms_collected"],
            "assessment_stage": conversation["assessment_stage"],
            "last_message": conversation["messages"][-1] if conversation["messages"] else None
        }
