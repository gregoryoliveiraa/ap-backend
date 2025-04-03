from typing import List, Dict, Tuple, Any
import openai
import anthropic
from enum import Enum
from app.core.config import settings

class AIProvider(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"

class AIProviderManager:
    def __init__(self):
        # Configurar clientes
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.claude_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
    def get_chat_completion(
        self,
        messages: List[Dict[str, str]],
        provider: AIProvider = AIProvider.OPENAI,
        model: str = None
    ) -> Tuple[str, int]:
        """
        Obter uma resposta do modelo de IA baseado no provedor selecionado.
        
        Args:
            messages: Lista de mensagens no formato esperado pela API
            provider: Provedor de IA a ser usado
            model: Modelo específico a ser usado (opcional)
            
        Returns:
            Uma tupla contendo (resposta, tokens_utilizados)
        """
        try:
            # Adicionar um sistema prompt para contexto legal brasileiro
            system_message = {
                "role": "system",
                "content": """Você é uma assistente jurídica especializada no sistema legal brasileiro.
                Forneça informações precisas e úteis sobre questões legais no Brasil, citando leis e códigos relevantes.
                Quando não tiver certeza, seja transparente sobre as limitações do seu conhecimento.
                Não forneça conselhos jurídicos definitivos, apenas orientações gerais."""
            }
            
            # Verificar se já existe um sistema prompt
            has_system = any(msg.get("role") == "system" for msg in messages)
            
            if not has_system:
                messages = [system_message] + messages
            
            if provider == AIProvider.OPENAI:
                return self._get_openai_completion(messages, model)
            elif provider == AIProvider.CLAUDE:
                return self._get_claude_completion(messages)
            elif provider == AIProvider.DEEPSEEK:
                return self._get_deepseek_completion(messages)
            else:
                raise ValueError(f"Provedor não suportado: {provider}")
                
        except Exception as e:
            print(f"Erro ao chamar {provider.value}: {str(e)}")
            # Tentar o próximo provedor disponível
            if provider == AIProvider.OPENAI:
                return self._get_claude_completion(messages)
            elif provider == AIProvider.CLAUDE:
                return self._get_deepseek_completion(messages)
            else:
                return f"Desculpe, não foi possível processar sua solicitação no momento. Erro: {str(e)}", 0
    
    def _get_openai_completion(self, messages: List[Dict[str, str]], model: str = None) -> Tuple[str, int]:
        """Obter resposta do OpenAI"""
        try:
            model = model or "gpt-3.5-turbo"
            print(f"Calling OpenAI API with model: {model}")
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            return response.choices[0].message.content, response.usage.total_tokens
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            # Try with fallback model if specified model failed
            if model != "gpt-3.5-turbo":
                print(f"Retrying with fallback model: gpt-3.5-turbo")
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1000,
                        top_p=0.95,
                        frequency_penalty=0,
                        presence_penalty=0
                    )
                    return response.choices[0].message.content, response.usage.total_tokens
                except Exception as e2:
                    print(f"Fallback model error: {str(e2)}")
            raise
    
    def _get_claude_completion(self, messages: List[Dict[str, str]]) -> Tuple[str, int]:
        """Obter resposta do Claude"""
        # Converter mensagens para o formato do Claude
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"Human: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n\n"
        
        response = self.claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text, 0  # Claude não retorna contagem de tokens
    
    def _get_deepseek_completion(self, messages: List[Dict[str, str]]) -> Tuple[str, int]:
        """Obter resposta do DeepSeek"""
        # Configurar cliente DeepSeek
        deepseek_client = openai.OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )
        
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content, 0  # DeepSeek não retorna contagem de tokens 

    def get_response(self, user_message: str, session_id: str, provider: AIProvider = AIProvider.OPENAI):
        """
        Obter uma resposta do modelo de IA baseado na mensagem do usuário
        
        Args:
            user_message: Mensagem enviada pelo usuário
            session_id: ID da sessão de chat
            provider: Provedor de IA a ser usado
            
        Returns:
            Um objeto contendo a resposta do assistente
        """
        try:
            messages = [
                {"role": "user", "content": user_message}
            ]
            
            print(f"Processing message with provider: {provider.value}")
            
            # Obter completions do provedor
            ai_message, tokens_used = self.get_chat_completion(
                messages=messages,
                provider=provider
            )
            
            # Criar objeto de resposta
            class AIResponse:
                def __init__(self, message, tokens_used):
                    self.message = message
                    self.tokens_used = tokens_used
            
            return AIResponse(message=ai_message, tokens_used=tokens_used)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error in get_response: {str(e)}")
            print(f"Error details: {error_trace}")
            print(f"Provider: {provider.value}, Message: {user_message[:50]}...")
            
            # Fornecer uma resposta de fallback para não quebrar a UI
            error_msg = f"Desculpe, não foi possível processar sua solicitação no momento. Erro: {str(e)[:100]}"
            
            class AIResponse:
                def __init__(self, message, tokens_used):
                    self.message = message
                    self.tokens_used = tokens_used
                    
            return AIResponse(message=error_msg, tokens_used=0) 