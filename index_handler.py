from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
import os
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]

from llama_index.core.tools import QueryEngineTool, ToolMetadata

# Obter o diretório do arquivo config.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


PATH_PAPERS = os.path.join(BASE_DIR, 'Artigos')
PATH_PAPERS_INDEX = os.path.join(BASE_DIR,'Artigos Index')
PATH_RESUMOS = ''

from threading import Lock

class QueryEngineToolsSingleton:
    _instance = None  # Armazena a única instância da classe
    _lock = Lock()  # Garante que a criação seja thread-safe

    @classmethod
    def get_tools(cls, similarity_top_k=3):
        """
        Retorna uma instância única de query_engine_tools. Cria a instância
        apenas na primeira chamada, utilizando o padrão singleton.
        """
        if cls._instance is None:
            with cls._lock:  # Bloqueia a criação da instância para evitar condições de corrida
                if cls._instance is None:
                    print('Inicializando query_engine_tools...')

                    # Carregar ou construir o índice
                    print('Tentando carregar index...')
                    result, full_papers_index = cls._load_indexs_full_paper()

                    if not result:
                        print('Index não encontrado. Construindo index...')
                        full_papers_index = cls._build_indexs_full_paper()
                    
                    if not full_papers_index:
                        raise Exception("Erro no load/build index")

                    print('Criando query engine...')
                    full_papers_engine = full_papers_index.as_query_engine(similarity_top_k=similarity_top_k)

                    print('Montando lista de tools...')
                    cls._instance = [
                        QueryEngineTool(
                            query_engine=full_papers_engine,
                            metadata=ToolMetadata(
                                name="artigos_base_conhecimento",
                                description=(
                                    "Fornece informações baseadas em uma base de dados composta por 17 artigos científicos selecionados "
                                    "sobre estratégias de estudo, organização do tempo e autorregulação da aprendizagem. "
                                    "Utilize uma pergunta detalhada em texto simples como entrada para a ferramenta. "
                                    "O modelo retornará respostas fundamentadas em literatura acadêmica."
                                ),
                            ),
                        ),
                    ]
        return cls._instance

    @classmethod
    def _load_indexs_full_paper(cls):
        """
        Método privado para carregar o índice de artigos armazenado.
        """
        try:
            storage_context = StorageContext.from_defaults(
                persist_dir=PATH_PAPERS_INDEX
            )
            full_papers_index = load_index_from_storage(storage_context)
            return True, full_papers_index
        except Exception as e:
            print(f"Erro ao carregar índice: {e}")
            return False, None

    @classmethod
    def _build_indexs_full_paper(cls):
        """
        Método privado para construir e persistir o índice de artigos.
        """
        try:
            # Carregar documentos
            full_papers_docs = SimpleDirectoryReader(
                input_files=[
                    os.path.join(PATH_PAPERS, p)
                    for p in os.listdir(PATH_PAPERS)
                    if p.endswith(".pdf")
                ]
            ).load_data()

            # Construir índice
            full_papers_index = VectorStoreIndex.from_documents(full_papers_docs)

            # Persistir índice
            full_papers_index.storage_context.persist(persist_dir=PATH_PAPERS_INDEX)
            
            return full_papers_index
        except Exception as e:
            print(f"Erro ao construir índice: {e}")
            return None


if __name__ == '__main__':
    tools = QueryEngineToolsSingleton.get_tools(similarity_top_k=3)
    print(tools)