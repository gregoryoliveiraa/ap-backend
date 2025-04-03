import openai
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.models.usage_tracking import ApiUsage
from sqlalchemy.orm import Session

# Configure the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY


class AIService:
    """
    Service for interacting with OpenAI API
    """
    
    @staticmethod
    async def generate_chat_completion(
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        user_id: Optional[int] = None,
        db: Optional[Session] = None,
        operation_type: str = "chat",
        resource_accessed: str = "chat_completion",
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using OpenAI's API
        
        Args:
            messages: List of message objects with role and content
            model: Model to use (defaults to settings.DEFAULT_MODEL_NAME)
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            user_id: User ID for tracking usage
            db: Database session for logging usage
            operation_type: Type of operation for usage tracking
            resource_accessed: Resource being accessed
            
        Returns:
            Response from OpenAI API
        """
        model = model or settings.DEFAULT_MODEL_NAME
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Log usage if user_id and db provided
            if user_id and db:
                usage = response.get("usage", {})
                api_usage = ApiUsage(
                    usuario_id=user_id,
                    tipo_operacao=operation_type,
                    tokens_entrada=usage.get("prompt_tokens", 0),
                    tokens_saida=usage.get("completion_tokens", 0),
                    modelo=model,
                    recurso_acessado=resource_accessed,
                )
                db.add(api_usage)
                db.commit()
            
            return response
        
        except Exception as e:
            # If there's an error and we specified the default model, try the fallback
            if model == settings.DEFAULT_MODEL_NAME:
                try:
                    response = await openai.ChatCompletion.acreate(
                        model=settings.FALLBACK_MODEL_NAME,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    
                    # Log usage if user_id and db provided
                    if user_id and db:
                        usage = response.get("usage", {})
                        api_usage = ApiUsage(
                            usuario_id=user_id,
                            tipo_operacao=operation_type,
                            tokens_entrada=usage.get("prompt_tokens", 0),
                            tokens_saida=usage.get("completion_tokens", 0),
                            modelo=settings.FALLBACK_MODEL_NAME,
                            recurso_acessado=resource_accessed,
                        )
                        db.add(api_usage)
                        db.commit()
                    
                    return response
                except Exception as fallback_error:
                    raise fallback_error
            else:
                raise e
    
    @staticmethod
    async def generate_legal_theses(
        facts: str,
        document_type: str,
        user_id: Optional[int] = None,
        db: Optional[Session] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate legal theses for a given case
        
        Args:
            facts: Facts of the case
            document_type: Type of document (petition, appeal, etc.)
            user_id: User ID for tracking usage
            db: Database session for logging usage
            
        Returns:
            List of legal theses
        """
        legal_context = """
        You are Advogada Parceira, a legal assistant specialized in the Brazilian legal system.
        You should always:
        1. Base your responses on updated Brazilian legislation, jurisprudence, and doctrine
        2. Cite relevant laws, codes, precedents, and legal summaries
        3. Adopt formal and technical language, appropriate for the legal context
        4. Structure arguments in a logical and well-founded manner
        5. Indicate when a question has multiple interpretations or positions
        """

        prompt = f"""
        {legal_context}

        Generate legal theses for a {document_type} related to the following facts:

        {facts}

        For each thesis, provide:
        1. A concise title
        2. Detailed legal foundation
        3. Citations of relevant jurisprudence
        4. Clear connection with the presented facts

        Format the response as a JSON array where each thesis is an object with the following structure:
        {{
            "title": "Thesis title",
            "legal_foundation": "Detailed legal foundation",
            "jurisprudence": "Relevant jurisprudence citations",
            "connection_to_facts": "Connection with the presented facts"
        }}
        """
        
        messages = [
            {"role": "system", "content": legal_context},
            {"role": "user", "content": prompt}
        ]
        
        response = await AIService.generate_chat_completion(
            messages=messages,
            temperature=0.3,  # Lower temperature for more deterministic responses
            max_tokens=2500,
            user_id=user_id,
            db=db,
            operation_type="document_generation",
            resource_accessed="legal_thesis_generation",
        )
        
        # Parse the response as JSON
        try:
            content = response["choices"][0]["message"]["content"]
            # Extract JSON from content if needed
            import json
            import re
            
            # Try to extract JSON if the response is not pure JSON
            json_match = re.search(r'(\[.*\])', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            theses = json.loads(content)
            return theses
        except Exception as e:
            # Fallback to returning the raw content if JSON parsing fails
            return [{"title": "Error parsing theses", "content": response["choices"][0]["message"]["content"]}]
    
    # Additional methods for document generation, jurisprudence analysis, etc. can be added here
