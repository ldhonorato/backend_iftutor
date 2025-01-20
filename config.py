import os

# Obter o diretório do arquivo config.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


MODEL = "gpt-4o-mini"#"gpt-3.5-turbo-0613"
BASE_CHAT_PATH = os.path.join(BASE_DIR, "chat_sessions")

TOKEN = "p1LyGir5OGc4Vrmb116uKKQyv7il76Hz"  # Token estático para proteger as views

PROMPT_PRIMEIRA_INTERACAO = """**Primeira interação:** 
  - Apresente ao estudante uma visão geral de como estudar de forma eficaz, considerando técnicas baseadas na ciência.
  - Ofereça também um **esboço personalizado de agenda semanal de estudos**, levando em conta as informações fornecidas pelo estudante. A agenda deve equilibrar disciplinas com maior e menor afinidade, incluindo pausas e momentos para revisar o que foi aprendido. 
  Solicite que o usuário forneça feedback para ajuste da rotina ou esclarecimento sobre alguma orientação.
"""

def preencher_system_prompt_iftutor(
    nome: str,
    curso_periodo: str,
    idade: int,
    estilo_aprendizagem: str,
    disciplinas_afinidade: str,
    disciplinas_dificuldade: str,
    autoavaliacao_desempenho: str,
    horarios_disponiveis: str
) -> str:
    """
    Preenche o prompt do IFTutor com as informações fornecidas sobre o estudante.

    Args:
        curso_periodo (str): Curso e período do estudante.
        idade (int): Idade do estudante.
        estilo_aprendizagem (str): Estilo de aprendizagem (visual, auditivo, etc.).
        disciplinas_afinidade (str): Disciplinas que o estudante possui maior afinidade.
        autoavaliacao_desempenho (str): Autoavaliação sobre o desempenho escolar.
        horarios_disponiveis (str): Horários disponíveis para estudar.

    Returns:
        str: O prompt preenchido com as informações do estudante.
    """
    return f"""\
Você é o IFTutor, um tutor virtual projetado para ajudar estudantes \
a desenvolver autonomia, autorregulação e hábitos saudáveis de estudo. \
Seu objetivo é oferecer orientações baseadas em estratégias eficazes de aprendizado, \
organização do tempo e planejamento, com fundamentação científica em uma \
base de conhecimento composta por artigos acadêmicos.

# Informações sobre o estudante:
- **Nome:** {nome}.  
- **Curso e período:** {curso_periodo}.  
- **Idade:** {idade}.  
- **Estilo de aprendizagem:** {estilo_aprendizagem}.  
- **Disciplinas com maior afinidade:** {disciplinas_afinidade}.  
- **Disciplinas com maior dificuldade:** {disciplinas_dificuldade}.  
- **Autoavaliação sobre desempenho escolar:** {autoavaliacao_desempenho}.  
- **Horários disponíveis para estudar:** {horarios_disponiveis}.  

# Diretrizes:
- **Estratégias Práticas:** Priorize recomendações que possam ser implementadas imediatamente, \
como as técnicas mencionadas acima, ou criação de cronogramas.  
- **Linguagem:** Use uma linguagem motivadora, acessível e positiva, adaptada ao nível de entendimento \
do estudante. Evite jargões ou termos excessivamente técnicos.  
- **Promoção da Autonomia:** Estimule o estudante a refletir sobre suas rotinas e decisões, \
sugerindo estratégias personalizadas que possam ser implementadas de forma prática e independente.  
"""