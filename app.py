import streamlit as st
import json
import os
from datetime import date

# Nomes dos nossos arquivos locais
ARQUIVO_NOTAS = "notas.json"
ARQUIVO_SUBEIXOS = "subeixos.json"

# As 5 grandes áreas são fixas
EIXOS_FIXOS = ["Cirurgia", "Clínica", "Ginecologia e Obstetrícia", "Pediatria", "Preventiva"]

# Cores sólidas e marcantes para garantir excelente leitura com texto branco
CORES_EIXOS = {
    "Preventiva": "#D49A00",                  # Amarelo Escuro / Ouro
    "Pediatria": "#7B1FA2",                   # Roxo
    "Ginecologia e Obstetrícia": "#C2185B",   # Rosa Escuro / Magenta
    "Clínica": "#1976D2",                      # Azul Médico
    "Cirurgia": "#E65100"                     # Laranja
}

# --- CONFIGURAÇÃO INICIAL DA PÁGINA E ESTADO ---
st.set_page_config(page_title="Medicina", page_icon="🏥", layout="wide")

if "pagina" not in st.session_state:
    st.session_state.pagina = "home"
if "eixo_selecionado" not in st.session_state:
    st.session_state.eixo_selecionado = ""
if "subeixo_selecionado" not in st.session_state:
    st.session_state.subeixo_selecionado = ""

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

def carregar_subeixos():
    estrutura_base = {eixo: [] for eixo in EIXOS_FIXOS}
    if os.path.exists(ARQUIVO_SUBEIXOS):
        with open(ARQUIVO_SUBEIXOS, "r", encoding="utf-8") as f:
            dados_salvos = json.load(f)
            for eixo in EIXOS_FIXOS:
                if eixo in dados_salvos:
                    estrutura_base[eixo] = dados_salvos[eixo]
    return estrutura_base

def salvar_subeixos(dados):
    with open(ARQUIVO_SUBEIXOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

subeixos_db = carregar_subeixos()

# --- POP-UP DE NOVA NOTA ---
@st.dialog("Nova Anotação")
def popup_selecionar_materia():
    eixo_escolhido = st.selectbox("Selecione o Eixo Principal", EIXOS_FIXOS)
    opcoes_subeixo = ["Nenhum"] + subeixos_db[eixo_escolhido]
    subeixo_escolhido = st.selectbox("Subeixo (Opcional)", opcoes_subeixo)
    
    if st.button("Continuar para o editor ➡️", use_container_width=True):
        st.session_state.eixo_selecionado = eixo_escolhido
        st.session_state.subeixo_selecionado = subeixo_escolhido if subeixo_escolhido != "Nenhum" else ""
        st.session_state.pagina = "editor"
        st.rerun()

# --- MENU LATERAL (CONFIGURAÇÕES DE SUBEIXOS) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    st.write("**Gerenciar Subeixos**")
    
    eixo_alvo = st.selectbox("Qual eixo deseja editar?", EIXOS_FIXOS)
    nova_tag = st.text_input(f"Novo Subeixo para {eixo_alvo}")
    if st.button("Adicionar Subeixo"):
        if nova_tag and nova_tag not in subeixos_db[eixo_alvo]:
            subeixos_db[eixo_alvo].append(nova_tag)
            salvar_subeixos(subeixos_db)
            st.success("Adicionado!")
            st.rerun()
            
    st.markdown("---")
    tag_para_remover = st.selectbox("Remover Subeixo", [""] + subeixos_db[eixo_alvo])
    if st.button("Remover"):
        if tag_para_remover:
            subeixos_db[eixo_alvo].remove(tag_para_remover)
            salvar_subeixos(subeixos_db)
            st.success("Removido!")
            st.rerun()

# ==========================================
# ROTEAMENTO DE TELAS
# ==========================================

if st.session_state.pagina == "home":
    # --- TELA INICIAL ---
    st.title("🏥 Medicina")
    
    if st.button("➕ Nova Nota", type="primary", use_container_width=True):
        popup_selecionar_materia()
        
    st.markdown("---")
    
    # Barra de busca e filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        busca = st.text_input("🔍 Buscar")
    with col2:
        filtro_eixo = st.selectbox("📁 Eixo", ["Todos"] + EIXOS_FIXOS)
    with col3:
        if filtro_eixo != "Todos":
            opcoes_filtro_sub = ["Todos"] + subeixos_db[filtro_eixo]
            filtro_sub = st.selectbox("📂 Subeixo", opcoes_filtro_sub)
        else:
            filtro_sub = st.selectbox("📂 Subeixo", ["Selecione um Eixo primeiro"], disabled=True)
            filtro_sub = "Todos"

    notas_salvas = carregar_notas()
    
    if not notas_salvas:
        st.info("Sua base está vazia. Clique em Nova Nota para começar.")
    else:
        notas_filtradas = []
        for nota in notas_salvas:
            eixo_da_nota = nota.get("eixo", nota.get("materia", ""))
            subeixo_da_nota = nota.get("subeixo", "")
            
            bate_eixo = (filtro_eixo == "Todos" or eixo_da_nota == filtro_eixo)
            bate_sub = (filtro_sub == "Todos" or subeixo_da_nota == filtro_sub)
            termo = busca.lower()
            bate_busca = (termo in nota["titulo"].lower() or termo in nota["conteudo"].lower())
            
            if bate_eixo and bate_sub and bate_busca:
                notas_filtradas.append(nota)

        if not notas_filtradas:
            st.warning("Nenhuma nota encontrada com estes filtros.")
        else:
            st.write(f"**Anotações encontradas:** {len(notas_filtradas)}")
            
            # --- SISTEMA DE GALERIA (GRID) ---
            num_colunas = 2
            cols = st.columns(num_colunas)
            
            for idx, nota in enumerate(reversed(notas_filtradas)):
                eixo_display = nota.get('eixo', nota.get('materia', 'Clínica'))
                sub_display = f" | {nota.get('subeixo')}" if nota.get('subeixo') else ""
                
                # Pega a cor correspondente da etiqueta
                cor_tag = CORES_EIXOS.get(eixo_display, "#718096")
                
                # Monta o quadrado em HTML branco com a tag colorida embaixo
                card_html = f"""
                <div style="
                    background-color: #FFFFFF;
                    padding: 20px;
                    border-radius: 14px;
                    margin-bottom: 16px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.04);
                    border: 1px solid #E2E8F0;
                ">
                    <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 10px; color: #1A202C;">
                        {nota['titulo']}
                    </div>
                    
                    <div style="font-size: 0.95rem; line-height: 1.5; white-space: pre-wrap; color: #4A5568; margin-bottom: 18px;">
                        {nota['conteudo']}
                    </div>
                    
                    # Etiqueta do Eixo (Letra branca e fundo colorido na parte de baixo)
                    <div style="margin-top: auto;">
                        <span style="
                            background-color: {cor_tag};
                            color: #FFFFFF;
                            padding: 5px 12px;
                            border-radius: 8px;
                            font-size: 0.75rem;
                            font-weight: 700;
                            display: inline-block;
                            letter-spacing: 0.5px;
                            text-transform: uppercase;
                        ">
                            {eixo_display}{sub_display}
                        </span>
                    </div>
                </div>
                """
                
                with cols[idx % num_colunas]:
                    st.markdown(card_html, unsafe_allow_html=True)

elif st.session_state.pagina == "editor":
    # --- TELA CHEIA DE EDIÇÃO ---
    sub_titulo = f" 🔸 {st.session_state.subeixo_selecionado}" if st.session_state.subeixo_selecionado else ""
    st.title(f"📁 {st.session_state.eixo_selecionado}{sub_titulo}")
    
    titulo_nota = st.text_input("Título do Caso ou Aula")
    conteudo_nota = st.text_area("Suas anotações...", height=400)
    
    col_salvar, col_cancelar = st.columns(2)
    
    with col_salvar:
        if st.button("💾 Salvar Anotação", type="primary", use_container_width=True):
            if titulo_nota and conteudo_nota:
                nova_nota = {
                    "titulo": titulo_nota,
                    "eixo": st.session_state.eixo_selecionado,
                    "subeixo": st.session_state.subeixo_selecionado,
                    "conteudo": conteudo_nota,
                    "data": str(date.today())
                }
                salvar_nota(nova_nota)
                st.session_state.pagina = "home"
                st.session_state.eixo_selecionado = ""
                st.session_state.subeixo_selecionado = ""
                st.rerun()
            else:
                st.warning("Preencha título e conteúdo.")
                
    with col_cancelar:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state.pagina = "home"
            st.session_state.eixo_selecionado = ""
            st.session_state.subeixo_selecionado = ""
            st.rerun()
