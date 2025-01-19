from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from config import MODEL, preencher_system_prompt_iftutor, PROMPT_PRIMEIRA_INTERACAO, BASE_CHAT_PATH
from index_handler import QueryEngineToolsSingleton
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer
import os
import uuid
import json
# Caminho base onde os chats serão armazenados


# Função para garantir que o diretório de armazenamento exista
def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Gerar uma chave única para o chat store
def generate_chat_store_key(base_key="user"):
    """
    Gera uma chave única para o chat_store_key verificando se ela já existe.
    """
    existing_keys = [x[:-4] for x in os.listdir(BASE_CHAT_PATH) if x.endswith('.json')]
    while True:
        # Gera uma chave única combinando o base_key com um UUID
        key = f"{base_key}_{uuid.uuid4().hex[:8]}"
        if key not in existing_keys:
            return key

# Persistir o chat store em um arquivo JSON
def persist_chat_store(chat_store, chat_store_key):
    """
    Salva o chat store no caminho especificado.
    """
    ensure_directory_exists(BASE_CHAT_PATH)
    persist_path = os.path.join(BASE_CHAT_PATH, f"{chat_store_key}.json")
    chat_store.persist(persist_path=persist_path)
    print(f"Chat armazenado em: {persist_path}")


def init_chat(  nome: str,
                curso_periodo: str,
                idade: int,
                estilo_aprendizagem: str,
                disciplinas_afinidade: str,
                disciplinas_dificuldade: str,
                autoavaliacao_desempenho: str,
                horarios_disponiveis: str):
    
    print("Criando um novo chat...")
    llm = OpenAI(model=MODEL)
    system_prompt = preencher_system_prompt_iftutor(    nome,
                                                        curso_periodo, 
                                                        idade, 
                                                        estilo_aprendizagem, 
                                                        disciplinas_afinidade, 
                                                        disciplinas_dificuldade,
                                                        autoavaliacao_desempenho, 
                                                        horarios_disponiveis)
    # Gerar uma chave única para o novo chat
    chat_store_key = generate_chat_store_key(base_key='user')
    
    chat_store = SimpleChatStore()

    chat_memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000,
        chat_store=chat_store,
        chat_store_key=chat_store_key,
    )
    
    agent = OpenAIAgent.from_tools( QueryEngineToolsSingleton.get_tools(),
                                    llm=llm,
                                    verbose=True,
                                    system_prompt=system_prompt,
                                    memory=chat_memory)

    response = agent.chat(PROMPT_PRIMEIRA_INTERACAO)   

    # Persistir o chat
    persist_chat_store(chat_store, chat_store_key)

    return response, chat_store_key                       



def continue_chat(chat_store_key, new_message):
    print("Recuperando o chat...")
    
    # Carregar o chat store persistido
    llm = OpenAI(model=MODEL)
    loaded_chat_store = SimpleChatStore.from_persist_path(persist_path=os.path.join(BASE_CHAT_PATH, f"{chat_store_key}.json"))

    # Obter a memória do chat a partir do chat store carregado
    chat_memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000,
        chat_store=loaded_chat_store,
        chat_store_key=chat_store_key,
    )

    # Criar o agente OpenAIAgent com os dados carregados
    agent = OpenAIAgent.from_tools(
        QueryEngineToolsSingleton.get_tools(),
        llm=llm,
        verbose=True,
        memory=chat_memory
    )

    # Adicionar a nova mensagem do usuário ao histórico do chat
    response = agent.chat(new_message)

    # Persistir o chat atualizado
    persist_chat_store(loaded_chat_store, chat_store_key)

    return response


if __name__ == '__main__':
    nome = 'Leandro'
    curso_periodo = "Engenharia de Controle e Automação, 5º período"
    idade = 20
    estilo_aprendizagem = "Visual"
    disciplinas_afinidade = "Matemática, Física"
    disciplinas_dificuldade = "Programação"
    autoavaliacao_desempenho = "Boa, com dificuldades pontuais em organização"
    horarios_disponiveis = "Segunda a sexta, das 18h às 22h; sábado pela manhã"
    
    # response, chat_store_key = init_chat(   nome,
    #                                         curso_periodo,
    #                                         idade,
    #                                         estilo_aprendizagem,
    #                                         disciplinas_afinidade,
    #                                         disciplinas_dificuldade,
    #                                         autoavaliacao_desempenho,
    #                                         horarios_disponiveis
    #                                     )
    # print(response)
    # print(chat_store_key)
    response = continue_chat(chat_store_key='user_9915ea64', new_message='tenho dificuldade com a disciplina de programação orientada a objetos. Alguma dica de como estudar melhor esse conteúdo?')
    print(response)
