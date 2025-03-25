# app/services/ai_service.py
import openai
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.schemas.ai import ChatMessage

# Configura a chave da API OpenAI
openai.api_key = settings.OPENAI_API_KEY

class AIService:
    @staticmethod
    async def chat(message: str, history: Optional[List[ChatMessage]] = None) -> str:
        """
        Envia uma mensagem para a API da OpenAI e retorna a resposta.
        
        Args:
            message: Mensagem do usuário
            history: Histórico de mensagens anteriores
            
        Returns:
            Resposta da IA
        """
        try:
            # Converte o histórico para o formato esperado pela OpenAI
            messages = []
            
            # Adiciona informações de contexto sobre o sistema legal brasileiro
            system_message = {
                "role": "system",
                "content": ("Você é uma assistente jurídica especializada no sistema legal brasileiro. "
                           "Forneça informações precisas e relevantes sobre leis, jurisprudência e procedimentos legais no Brasil. "
                           "Seja clara, formal e técnica em suas respostas, utilizando terminologia jurídica adequada.")
            }
            messages.append(system_message)
            
            # Adiciona histórico de mensagens se existir
            if history:
                for msg in history:
                    messages.append({"role": msg.role, "content": msg.content})
            
            # Adiciona a mensagem atual
            messages.append({"role": "user", "content": message})
            
            # Faz a chamada para a API da OpenAI
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",  # Ou outro modelo disponível
                messages=messages,
                temperature=0.5,
                max_tokens=2048
            )
            
            # Extrai e retorna a resposta
            ai_response = response.choices[0].message.content.strip()
            return ai_response
            
        except Exception as e:
            print(f"Erro ao chamar a API da OpenAI: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde."
    
    @staticmethod
    async def analyze_document(document_text: str) -> Dict[str, Any]:
        """
        Analisa um documento jurídico usando a IA.
        
        Args:
            document_text: Texto do documento a ser analisado
            
        Returns:
            Análise do documento
        """
        try:
            # Instrução específica para análise de documentos
            prompt = (
                "Analise este documento jurídico e forneça as seguintes informações:\n"
                "1. Tipo de documento\n"
                "2. Partes envolvidas\n"
                "3. Objeto principal\n"
                "4. Principais cláusulas/argumentos\n"
                "5. Potenciais problemas ou inconsistências\n"
                "6. Sugestões de melhoria\n\n"
                f"Documento: {document_text}\n\n"
                "Formate a resposta em JSON."
            )
            
            # Faz a chamada para a API da OpenAI
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em análise de documentos jurídicos brasileiros."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048
            )
            
            # Extrai e retorna a resposta
            analysis_text = response.choices[0].message.content.strip()
            
            # Aqui seria ideal fazer um parsing do JSON, mas para simplificar,
            # retornamos um dicionário com a análise completa
            return {"analysis_text": analysis_text}
            
        except Exception as e:
            print(f"Erro ao analisar documento: {str(e)}")
            return {"error": "Ocorreu um erro ao analisar o documento"}
    
    @staticmethod
    async def generate_document(document_type: str, parameters: Dict[str, Any]) -> str:
        """
        Gera um documento jurídico usando a IA.
        
        Args:
            document_type: Tipo de documento a ser gerado
            parameters: Parâmetros específicos para o documento
            
        Returns:
            Texto do documento gerado
        """
        try:
            # Construir o prompt com base no tipo de documento e parâmetros
            prompt = f"Gere um documento jurídico do tipo {document_type} com os seguintes parâmetros:\n"
            
            for key, value in parameters.items():
                prompt += f"- {key}: {value}\n"
            
            prompt += "\nO documento deve seguir o formato padrão utilizado no sistema jurídico brasileiro."
            
            # Faz a chamada para a API da OpenAI
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em redigir documentos jurídicos brasileiros."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=4096
            )
            
            # Extrai e retorna a resposta
            document_text = response.choices[0].message.content.strip()
            return document_text
            
        except Exception as e:
            print(f"Erro ao gerar documento: {str(e)}")
            return "Ocorreu um erro ao gerar o documento. Por favor, tente novamente mais tarde."
    
    @staticmethod
    async def search_jurisprudence(query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Pesquisa jurisprudência relacionada à consulta.
        
        Args:
            query: Consulta de pesquisa
            filters: Filtros adicionais (tribunal, período, etc.)
            
        Returns:
            Lista de resultados da jurisprudência
        """
        try:
            # Construir o prompt com a consulta e filtros
            prompt = f"Pesquise jurisprudência relacionada a: {query}\n"
            
            if filters:
                prompt += "Filtros aplicados:\n"
                for key, value in filters.items():
                    prompt += f"- {key}: {value}\n"
            
            # Faz a chamada para a API da OpenAI
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em pesquisa jurisprudencial brasileira."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3072
            )
            
            # Extrai a resposta
            results_text = response.choices[0].message.content.strip()
            
            # Aqui seria ideal conectar-se a uma API real de jurisprudência,
            # mas para demonstração, retornamos resultados simulados
            results = [
                {
                    "tribunal": "STJ",
                    "numero_processo": "REsp 1234567/SP",
                    "relator": "Min. Exemplo da Silva",
                    "data_julgamento": "12/05/2023",
                    "ementa": results_text[:500],  # Usamos parte da resposta como "ementa"
                    "link": "https://exemplo.com/jurisprudencia/12345"
                },
                {
                    "tribunal": "STF",
                    "numero_processo": "RE 9876543/DF",
                    "relator": "Min. Exemplo Segundo",
                    "data_julgamento": "23/09/2022",
                    "ementa": results_text[500:1000] if len(results_text) > 500 else "Ementa exemplo",
                    "link": "https://exemplo.com/jurisprudencia/67890"
                }
            ]
            
            return results
            
        except Exception as e:
            print(f"Erro ao pesquisar jurisprudência: {str(e)}")
            return [{"error": "Ocorreu um erro ao pesquisar jurisprudência"}]