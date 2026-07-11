import streamlit as st
import json
import os
from datetime import date

# Nomes dos nossos arquivos locais
ARQUIVO_NOTAS = "notas.json"
ARQUIVO_MATERIAS = "materias.json"

# --- CONFIGURAÇÃO INICIAL DA PÁGINA E ESTADO ---
st.set_page_config(page_title="Medicina", page_icon="🏥")

# Criamos variáveis de "estado" para o app lembrar onde estamos
if "pagina" not in st.session_state:
    st.session_state.pagina = "home"
if "materia_selecionada" not in st.session_state:
    st.session_state.materia_selecionada = ""

# --- FUNÇÕES DE PERSISTÊNCIA ---
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

def carregar_materias():
    if os.path.exists(ARQUIVO_MATERIAS):
        with open(ARQUIVO_MATERIAS, "r", encoding="utf-8") as f:
            lista = json.load(f)
            if lista: return lista
    return ["Pediatria", "Genética", "Clínica Médica", "Ginecologia e Obstetrícia", "Cirurgia Geral"]

def salvar_materias(nova_lista):
    with open(ARQUIVO_MATERIAS, "w", encoding="utf-8") as f:
        json.dump(nova_lista, f, ensure_ascii=False, indent=4)

materias_disponiveis = carregar_materias()

# --- POP-UP DE NOVA NOTA ---
@st.dialog("Nova Anotação")
def popup_selecionar_materia():
    st.write("Em qual eixo você vai anotar agora?")
    materia_escolhida = st.selectbox("Eixo/Matéria", materias_disponiveis, label_visibility="collapsed")
    
    if st.button("Continuar para o editor ➡️", use_container_width=True):
        # Salva a escolha e muda a página
        st.session_state.materia_selecionada = materia_escolhida
        st.session_state.pagina = "editor"
        st.rerun()

# --- MENU LATERAL (APENAS CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    st.write("Gerenciar Eixos/Matérias")
    nova_materia = st.text_input("Nova Matéria")
    if st.button("Adicionar"):
        if nova_materia and nova_materia not in materias_disponiveis:
            materias_disponiveis.append(nova_materia)
            salvar_materias(materias_disponiveis)
            st.success("Adicionada!")
            st.rerun()
            
    materia_para_remover = st.selectbox("Remover Matéria", [""] + materias_disponiveis)
    if st.button("Remover"):
        if materia_para_remover:
            materias_disponiveis.remove(materia_para_remover)
            salvar_materias(materias_disponiveis)
            st.success("Removida!")
            st.rerun()

# ==========================================
# ROTEAMENTO DE TELAS
# ==========================================

if st.session_state.pagina == "home":
    # --- TELA INICIAL ---
    st.title("🏥 Medicina")
    
    # Botão de destaque na tela principal
    if st.button("➕ Nova Nota", type="primary", use_container_width=True):
        popup_selecionar_materia()
        
    st.markdown("---")
    
    # Barra de busca e listagem
    col1, col2 = st.columns(2)
    with col1:
        busca = st.text_input("🔍 Buscar anotação")
    with col2:
        filtro_materia = st.selectbox("📁 Filtrar eixo", ["Todos"] + materias_disponiveis)

    notas_salvas = carregar_notas()
    
    if not notas_salvas:
        st.info("Sua base está vazia. Clique em Nova Nota para começar.")
    else:
        notas_filtradas = []
        for nota in notas_salvas:
            bate_materia = (filtro_materia == "Todos" or nota["materia"] == filtro_materia)
            termo = busca.lower()
            bate_busca = (termo in nota["titulo"].lower() or termo in nota["conteudo"].lower())
            if bate_materia and bate_busca:
                notas_filtradas.append(nota)

        for nota in reversed(notas_filtradas):
            with st.expander(f"{nota['data']} | {nota['materia']} - {nota['titulo']}"):
                st.write(nota['conteudo'])

elif st.session_state.pagina == "editor":
    # --- TELA CHEIA DE EDIÇÃO ---
    st.title(f"📁 {st.session_state.materia_selecionada}")
    
    titulo_nota = st.text_input("Título do Caso ou Aula")
    conteudo_nota = st.text_area("Suas anotações...", height=400) # Deixa a caixa de texto bem grande
    
    col_salvar, col_cancelar = st.columns(2)
    
    with col_salvar:
        if st.button("💾 Salvar Anotação", type="primary", use_container_width=True):
            if titulo_nota and conteudo_nota:
                nova_nota = {
                    "titulo": titulo_nota,
                    "materia": st.session_state.materia_selecionada,
                    "conteudo": conteudo_nota,
                    "data": str(date.today())
                }
                salvar_nota(nova_nota)
                # Limpa o estado e volta pra home
                st.session_state.pagina = "home"
                st.session_state.materia_selecionada = ""
                st.rerun()
            else:
                st.warning("Preencha título e conteúdo.")
                
    with col_cancelar:
        if st.button("❌ Cancelar", use_container_width=True):
            # Abandona a edição e volta pra home
            st.session_state.pagina = "home"
            st.session_state.materia_selecionada = ""
            st.rerun()
