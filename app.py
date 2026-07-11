import streamlit as st
import json
import os
from datetime import date

# Nomes dos nossos arquivos locais
ARQUIVO_NOTAS = "notas.json"
ARQUIVO_SUBEIXOS = "subeixos.json"

# As 5 grandes áreas são fixas
EIXOS_FIXOS = ["Cirurgia", "Clínica", "Ginecologia e Obstetrícia", "Pediatria", "Preventiva"]

# Cores sólidas para as etiquetas com texto branco
CORES_EIXOS = {
    "Preventiva": "#D49A00",                  # Amarelo Escuro / Ouro
    "Pediatria": "#7B1FA2",                   # Roxo
    "Ginecologia e Obstetrícia": "#C2185B",   # Rosa Escuro / Magenta
    "Clínica": "#1976D2",                      # Azul Médico
    "Cirurgia": "#E65100"                     # Laranja
}

# --- CONFIGURAÇÃO INICIAL DA PÁGINA E ESTADO ---
st.set_page_config(page_title="Medicina", page_icon="🏥", layout="wide")

# --- ESTILO CSS CUSTOMIZADO (MINIMALISTA) ---
st.markdown("""
<style>
/* Altera a cor do botão primário (Nova Nota e Salvar) de Vermelho para Grafite Escuro */
button[kind="primary"] {
    background-color: #222222 !important;
    color: #FFFFFF !important;
    border: 1px solid #222222 !important;
    border-radius: 8px !important;
}
button[kind="primary"]:hover {
    background-color: #444444 !important;
    border-color: #444444 !important;
}
/* Arredondamento padrão para os botões secundários */
button[kind="secondary"] {
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

if "pagina" not in st.session_state:
    st.session_state.pagina = "home"
if "eixo_selecionado" not in st.session_state:
    st.session_state.eixo_selecionado = ""
if "subeixo_selecionado" not in st.session_state:
    st.session_state.subeixo_selecionado = ""
if "modo_editor" not in st.session_state:
    st.session_state.modo_editor = "criar"
if "edit_titulo" not in st.session_state:
    st.session_state.edit_titulo = ""
if "edit_conteudo" not in st.session_state:
    st.session_state.edit_conteudo = ""
if "nota_index" not in st.session_state:
    st.session_state.nota_index = None

# --- FUNÇÕES DE PERSISTÊNCIA ---
def carregar_notas():
    if os.path.exists(ARQUIVO_NOTAS):
        try:
            with open(ARQUIVO_NOTAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_nota(nova_nota):
    notas = carregar_notas()
    notas.append(nova_nota)
    with open(ARQUIVO_NOTAS, "w", encoding="utf-8") as f:
        json.dump(notas, f, ensure_ascii=False, indent=4)

def carregar_subeixos():
    estrutura_base = {eixo: [] for eixo in EIXOS_FIXOS}
    if os.path.exists(ARQUIVO_SUBEIXOS):
        try:
            with open(ARQUIVO_SUBEIXOS, "r", encoding="utf-8") as f:
                dados_salvos = json.load(f)
                if isinstance(dados_salvos, dict):
                    for eixo in EIXOS_FIXOS:
                        if eixo in dados_salvos:
                            estrutura_base[eixo] = dados_salvos[eixo]
        except Exception:
            pass
    return estrutura_base

def salvar_subeixos(dados):
    with open(ARQUIVO_SUBEIXOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

subeixos_db = carregar_subeixos()

# --- POP-UP PARA VISUALIZAR A NOTA COMPLETA ---
@st.dialog("Visualizar Anotação")
def dialog_ver_nota(nota, cor_tag, eixo, subeixo):
    tag_html = f"""
    <div style="margin-bottom: 15px;">
        <span style="
            background-color: {cor_tag};
            color: #FFFFFF;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
            text-transform: uppercase;
        ">
            {eixo}{subeixo}
        </span>
    </div>
    """
    st.markdown(tag_html, unsafe_allow_html=True)
    st.subheader(nota['titulo'])
    st.markdown("---")
    st.write(nota['conteudo'])
    st.write("")

# --- POP-UP DE NOVA NOTA (SELEÇÃO DE ÁREA) ---
@st.dialog("Nova Anotação")
def popup_selecionar_materia():
    eixo_escolhido = st.selectbox("Selecione o Eixo Principal", EIXOS_FIXOS, key="popup_eixo")
    opcoes_subeixo = ["Nenhum"] + subeixos_db[eixo_escolhido]
    subeixo_escolhido = st.selectbox("Subeixo (Opcional)", opcoes_subeixo, key="popup_subeixo")
    
    if st.button("Continuar para o editor ➡️", use_container_width=True, key="btn_continuar"):
        st.session_state.eixo_selecionado = eixo_escolhido
        st.session_state.subeixo_selecionado = subeixo_escolhido if subeixo_escolhido != "Nenhum" else ""
        st.session_state.pagina = "editor"
        st.rerun()

# --- MENU LATERAL (CONFIGURAÇÕES DE SUBEIXOS) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    st.write("**Gerenciar Subeixos**")
    
    eixo_alvo = st.selectbox("Qual eixo deseja editar?", EIXOS_FIXOS, key="config_eixo_alvo")
    nova_tag = st.text_input(f"Novo Subeixo para {eixo_alvo}", key="config_nova_tag")
    if st.button("Adicionar Subeixo", key="btn_add_subeixo"):
        if nova_tag and nova_tag not in subeixos_db[eixo_alvo]:
            subeixos_db[eixo_alvo].append(nova_tag)
            salvar_subeixos(subeixos_db)
            st.success("Adicionado!")
            st.rerun()
            
    st.markdown("---")
    tag_para_remover = st.selectbox("Remover Subeixo", [""] + subeixos_db[eixo_alvo], key="config_remover_tag")
    if st.button("Remover", key="btn_rem_subeixo"):
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
    
    # Botão principal agora sem emoji e com a cor customizada pelo CSS (Grafite)
    if st.button("Nova Nota", type="primary", use_container_width=True, key="btn_nova_nota_main"):
        st.session_state.modo_editor = "criar"
        st.session_state.edit_titulo = ""
        st.session_state.edit_conteudo = ""
        popup_selecionar_materia()
        
    st.markdown("---")
    
    # Barra de busca e filtros dinâmicos
    col1, col2, col3 = st.columns(3)
    with col1:
        busca = st.text_input("🔍 Buscar", key="busca_principal")
    with col2:
        filtro_eixo = st.selectbox("📁 Eixo", ["Todos"] + EIXOS_FIXOS, key="filtro_eixo_main")
    with col3:
        if filtro_eixo != "Todos":
            opcoes_filtro_sub = ["Todos"] + subeixos_db[filtro_eixo]
            sub_disabled = False
        else:
            opcoes_filtro_sub = ["Selecione um Eixo primeiro"]
            sub_disabled = True
            
        filtro_sub_val = st.selectbox("📂 Subeixo", opcoes_filtro_sub, disabled=sub_disabled, key="filtro_sub_main")
        filtro_sub = "Todos" if filtro_eixo == "Todos" else filtro_sub_val

    notas_salvas = carregar_notas()
    
    if not notas_salvas:
        st.info("Sua base está vazia. Clique em Nova Nota para começar.")
    else:
        notas_filtradas = []
        for idx_original, nota in enumerate(notas_salvas):
            eixo_da_nota = nota.get("eixo", nota.get("materia", ""))
            subeixo_da_nota = nota.get("subeixo", "")
            
            bate_eixo = (filtro_eixo == "Todos" or eixo_da_nota == filtro_eixo)
            bate_sub = (filtro_sub == "Todos" or subeixo_da_nota == filtro_sub)
            termo = busca.lower()
            bate_busca = (termo in nota["titulo"].lower() or termo in nota["conteudo"].lower())
            
            if bate_eixo and bate_sub and bate_busca:
                notas_filtradas.append((idx_original, nota))

        if not notas_filtradas:
            st.warning("Nenhuma nota encontrada com estes filtros.")
        else:
            st.write(f"**Anotações encontradas:** {len(notas_filtradas)}")
            
            # --- SISTEMA DE GALERIA EM GRID ---
            num_colunas = 2
            cols = st.columns(num_colunas)
            
            for idx_grid, (idx_original, nota) in enumerate(reversed(notas_filtradas)):
                eixo_display = nota.get('eixo', nota.get('materia', 'Clínica'))
                sub_display = f" | {nota.get('subeixo')}" if nota.get('subeixo') else ""
                cor_tag = CORES_EIXOS.get(eixo_display, "#718096")
                
                with cols[idx_grid % num_colunas]:
                    with st.container(border=True):
                        st.markdown(f"#### {nota['titulo']}")
                        
                        tag_html = f"""
                        <div style="margin-top: 5px; margin-bottom: 15px;">
                            <span style="
                                background-color: {cor_tag};
                                color: #FFFFFF;
                                padding: 4px 10px;
                                border-radius: 6px;
                                font-size: 0.75rem;
                                font-weight: 700;
                                display: inline-block;
                                text-transform: uppercase;
                                letter-spacing: 0.3px;
                            ">
                                {eixo_display}{sub_display}
                            </span>
                        </div>
                        """
                        st.markdown(tag_html, unsafe_allow_html=True)
                        
                        # Botões lado a lado, sem emojis e com gap reduzido para otimizar espaço
                        b_col1, b_col2 = st.columns(2, gap="small")
                        with b_col1:
                            if st.button("Ver Nota", key=f"ver_{idx_original}", use_container_width=True):
                                dialog_ver_nota(nota, cor_tag, eixo_display, sub_display)
                        with b_col2:
                            if st.button("Editar", key=f"edit_{idx_original}", use_container_width=True):
                                st.session_state.pagina = "editor"
                                st.session_state.modo_editor = "editar"
                                st.session_state.nota_index = idx_original
                                st.session_state.eixo_selecionado = eixo_display
                                st.session_state.subeixo_selecionado = nota.get("subeixo", "")
                                st.session_state.edit_titulo = nota["titulo"]
                                st.session_state.edit_conteudo = nota["conteudo"]
                                st.rerun()

elif st.session_state.pagina == "editor":
    # --- TELA CHEIA DE EDIÇÃO/CRIAÇÃO ---
    sub_titulo = f" 🔸 {st.session_state.subeixo_selecionado}" if st.session_state.subeixo_selecionado else ""
    
    if st.session_state.modo_editor == "editar":
        st.title(f"✏️ Editando: {st.session_state.eixo_selecionado}{sub_titulo}")
    else:
        st.title(f"📁 Nova Nota: {st.session_state.eixo_selecionado}{sub_titulo}")
    
    titulo_nota = st.text_input("Título do Caso ou Aula", value=st.session_state.edit_titulo, key="editor_titulo")
    conteudo_nota = st.text_area("Suas anotações...", value=st.session_state.edit_conteudo, height=400, key="editor_conteudo")
    
    if st.session_state.modo_editor == "editar":
        col_salvar, col_cancelar, col_excluir = st.columns([2, 2, 1.2])
    else:
        col_salvar, col_cancelar = st.columns(2)
    
    with col_salvar:
        # Esse botão também assume a cor Grafite automaticamente por ser 'primary'
        if st.button("Salvar Anotação", type="primary", use_container_width=True, key="btn_salvar_nota"):
            if titulo_nota and conteudo_nota:
                nova_nota = {
                    "titulo": titulo_nota,
                    "eixo": st.session_state.eixo_selecionado,
                    "subeixo": st.session_state.subeixo_selecionado,
                    "conteudo": conteudo_nota,
                    "data": str(date.today())
                }
                
                if st.session_state.modo_editor == "criar":
                    salvar_nota(nova_nota)
                else:
                    notas = carregar_notas()
                    idx_alvo = st.session_state.nota_index
                    if idx_alvo is not None and idx_alvo < len(notas):
                        notas[idx_alvo] = nova_nota
                        with open(ARQUIVO_NOTAS, "w", encoding="utf-8") as f:
                            json.dump(notas, f, ensure_ascii=False, indent=4)
                
                st.session_state.pagina = "home"
                st.rerun()
            else:
                st.warning("Preencha título e conteúdo.")
                
    with col_cancelar:
        if st.button("Cancelar", use_container_width=True, key="btn_cancelar_nota"):
            st.session_state.pagina = "home"
            st.rerun()

    if st.session_state.modo_editor == "editar":
        with col_excluir:
            if st.button("Excluir", type="secondary", use_container_width=True, key="btn_excluir_nota_edit"):
                notas = carregar_notas()
                idx_alvo = st.session_state.nota_index
                if idx_alvo is not None and idx_alvo < len(notas):
                    notas.pop(idx_alvo)
                    with open(ARQUIVO_NOTAS, "w", encoding="utf-8") as f:
                        json.dump(notas, f, ensure_ascii=False, indent=4)
                st.session_state.pagina = "home"
                st.rerun()
