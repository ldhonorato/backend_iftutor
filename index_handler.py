from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")#os.environ["OPENAI_API_KEY"]

from llama_index.core.tools import QueryEngineTool, ToolMetadata

# Obter o diretório do arquivo config.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


PATH_PAPERS = os.path.join(BASE_DIR, 'Artigos')
PATH_PAPERS_INDEX = os.path.join(BASE_DIR,'Artigos_index')
PATH_RESUMOS = os.path.join(BASE_DIR, 'Artigos resumidos')
PATH_RESUMOS_INDEX = os.path.join(BASE_DIR,'Artigos_resumidos_index')

from threading import Lock

class QueryEngineToolsSingleton:
    _instances = {}  # Armazena a única instância da classe
    _lock = Lock()  # Garante que a criação seja thread-safe

    @classmethod
    def get_tools(cls, similarity_top_k=3, path_index=PATH_PAPERS_INDEX, path_files=PATH_PAPERS):
        """
        Retorna uma instância única de query_engine_tools. Cria a instância
        apenas na primeira chamada, utilizando o padrão singleton.
        """
        if path_index not in cls._instances:
            with cls._lock:  # Bloqueia a criação da instância para evitar condições de corrida
            
                print('Inicializando query_engine_tools...')

                # Carregar ou construir o índice
                print('Tentando carregar index...')
                result, full_papers_index = cls._load_indexs(path_index)

                if not result:
                    print('Index não encontrado. Construindo index...')
                    full_papers_index = cls._build_indexs(path_files, path_index)

                if not full_papers_index:
                    raise Exception("Erro no load/build index")

                print('Criando query engine...')
                full_papers_engine = full_papers_index.as_query_engine(similarity_top_k=similarity_top_k)

                print('Montando lista de tools...')
                cls._instances[path_index] = [
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
        return cls._instances[path_index]

    @classmethod
    def _load_indexs(cls, path_index):
        """
        Método privado para carregar o índice de artigos armazenado.
        """
        try:
            storage_context = StorageContext.from_defaults(
                persist_dir=path_index
            )
            index = load_index_from_storage(storage_context)
            return True, index
        except Exception as e:
            print(f"Erro ao carregar índice: {e}")
            return False, None

    @classmethod
    def _build_indexs(cls, path_files, save_index_path):
        """
        Método privado para construir e persistir o índice de artigos.
        """
        try:
            # Carregar documentos
            docs = SimpleDirectoryReader(
                input_files=[
                    os.path.join(path_files, p)
                    for p in os.listdir(path_files)
                    if p.endswith(".pdf")
                ]
            ).load_data()

            # Construir índice
            index = VectorStoreIndex.from_documents(docs)

            # Persistir índice
            index.storage_context.persist(persist_dir=save_index_path)

            return index
        except Exception as e:
            print(f"Erro ao construir índice: {e}")
            return None


if __name__ == '__main__':
    tools = QueryEngineToolsSingleton.get_tools(similarity_top_k=3, path_files=PATH_RESUMOS, path_index=PATH_RESUMOS_INDEX)
    print(tools)