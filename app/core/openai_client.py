import os
import openai
from typing import List, Dict, Tuple, Any
from app.core.config import settings

# Configurar a API key do OpenAI
openai.api_key = settings.OPENAI_API_KEY

def get_chat_completion(messages: List[Dict[str, str]]) -> Tuple[str, int]:
    """
    Obter uma resposta do modelo GPT baseado no histórico de mensagens.
    
    Args:
        messages: Lista de mensagens no formato esperado pela API da OpenAI.
        
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
            
        # Fazer a chamada à API da OpenAI
        if openai.api_key:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Modelo mais amplamente disponível
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            message_content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return message_content, tokens_used
        else:
            # Resposta simulada para desenvolvimento quando não há API key
            return "Esta é uma resposta simulada do assistente jurídico porque nenhuma chave da API OpenAI foi configurada.", 50
            
    except Exception as e:
        # Log do erro
        print(f"Erro ao chamar OpenAI: {str(e)}")
        # Retornar uma resposta de fallback
        return f"Desculpe, não foi possível processar sua solicitação no momento. Erro: {str(e)}", 0 