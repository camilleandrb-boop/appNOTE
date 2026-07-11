import streamlit as st
import json
import os
from datetime import date

# Nomes dos nossos arquivos de banco de dados locais
ARQUIVO_NOTAS = "notas.json"
ARQUIVO_MATERIAS = "materias.json"

# --- FUNÇÕES DE PERSISTÊNCIA (NOTAS) ---
def carregar_notas():
    if os.path.exists(ARQUIVO_NOTAS):
        with open(ARQUIVO_NOTAS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_nota(nova_nota):
    notas = carregar_notas()
    notas.append(nova_nota)
    with open(ARQUIVO_NOTAS, "w", encoding="utf-8") as f:
        json.dump(notas, f, ensure_ascii=False, indent=4)

# --- FUNÇÕES DE PERSISTÊNCIA (MATÉRIAS/EIXOS) ---
def carregar_materias():
    if os.path.exists(ARQUIVO_MATERIAS):
        with open(ARQUIVO_MATERIAS, "r", encoding="utf-8") as f:
            lista = json.load(f)
            if lista: # Se não estiver vazia, retorna a lista salva
                return lista
    # Lista padrão caso o arquivo ainda não exista ou esteja vazio
    return ["Pediatria", "Genética", "Clínica Médica", "Ginecologia e Obstetrícia", "Cirurgia Geral"]

def salvar_materias(nova_lista):
    with open(ARQUIVO_MATERIAS, "w", encoding="utf-8") as f:
        json.dump(nova_lista, f, ensure_ascii=False, indent=4)

# Configuração da página
st.set_page_config(page_title="Minhas Anotações", page_icon="📝")
st.title("📝 Anotações do Internato")

# Carrega as matérias dinâmicas do arquivo
materias_disponiveis = carregar_materias()

# --- MENU LATERAL ---
st.sidebar.header("Nova Anotação")
titulo = st.sidebar.text_input("Título ou Tema")

# O selectbox agora usa a nossa lista dinâmica!
materia = st.sidebar.selectbox("Eixo/Matéria", materias_disponiveis)

conteudo = st.sidebar.text_area("Conteúdo da anotação")
data_atual = st.sidebar.date_input("Data", date.today())

# Lógica do Botão de Salvar Nota
if st.sidebar.button("Salvar Nota"):
    if titulo and conteudo:
        nova_nota = {
            "titulo": titulo,
            "materia": materia,
            "conteudo": conteudo,
            "data": str(data_atual)
        }
        salvar_nota(nova_nota)
        st.sidebar.success("Nota salva com sucesso!")
        st.rerun() # Atualiza a tela para mostrar a nota imediatamente
    else:
        st.sidebar.warning("Preencha o título e o conteúdo antes de salvar.")

st.sidebar.markdown("---") # Linha divisória no menu

# --- SEÇÃO DE GERENCIAR MATÉRIAS ---
st.sidebar.header("⚙️ Gerenciar Matérias")
nova_materia = st.sidebar.text_input("Nova Matéria/Eixo")

if st.sidebar.button("Adicionar Matéria"):
    if nova_materia:
        if nova_materia not in materias_disponiveis:
            materias_disponiveis.append(nova_materia)
            salvar_materias(materias_disponiveis)
            st.sidebar.success(f"'{nova_materia}' adicionada!")
            st.rerun() # Atualiza a tela para atualizar o selectbox acima
        else:
            st.sidebar.warning("Esta matéria já existe!")
    else:
        st.sidebar.warning("Digite o nome da matéria.")

# Opção para excluir uma matéria se necessário
st.sidebar.markdown("**Remover Matéria:**")
materia_para_remover = st.sidebar.selectbox("Selecionar para remover", [""] + materias_disponiveis)
if st.sidebar.button("Remover"):
    if materia_para_remover:
        materias_disponiveis.remove(materia_para_remover)
        salvar_materias(materias_disponiveis)
        st.sidebar.success(f"'{materia_para_remover}' removida!")
        st.rerun()

# --- ÁREA PRINCIPAL ---
st.subheader("Anotações Salvas")

# Adicionando uma barra de busca simples e filtro por matéria na área principal
col1, col2 = st.columns(2)
with col1:
    busca = st.text_input("🔍 Buscar por palavra-chave")
with col2:
    filtro_materia = st.selectbox("📁 Filtrar por Matéria", ["Todas"] + materias_disponiveis)

notas_salvas = carregar_notas()

if not notas_salvas:
    st.info("Nenhuma anotação salva ainda. Use o menu lateral para adicionar a primeira!")
else:
    # Filtra as notas com base na busca e no filtro de matéria
    notas_filtradas = []
    for nota in notas_salvas:
        # Verifica se bate com o filtro de matéria
        bate_materia = (filtro_materia == "Todas" or nota["materia"] == filtro_materia)
        # Verifica se bate com a palavra-chave no título ou conteúdo
        termo = busca.lower()
        bate_busca = (termo in nota["titulo"].lower() or termo in nota["conteudo"].lower())
        
        if bate_materia and bate_busca:
            notas_filtradas.append(nota)

    if not notas_filtradas:
        st.warning("Nenhuma nota encontrada com esses filtros.")
    else:
        # Mostra as notas filtradas da mais recente para a mais antiga
        for nota in reversed(notas_filtradas):
            with st.expander(f"{nota['data']} - {nota['materia']}: {nota['titulo']}"):
                st.write(nota['conteudo'])
