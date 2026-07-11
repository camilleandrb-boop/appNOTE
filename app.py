import streamlit as st
import json
import os
import re
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

# --- MOTOR DE FORMATAÇÃO CUSTOMIZADA (SOLUÇÃO DEFINITIVA) ---
def formatar_texto_customizado(texto):
    if not texto:
        return ""
    
    linhas = texto.split("\n")
    linhas_formatadas = []
    
    for linha in linhas:
        linha_clean = linha.strip()
        
        # 1. Subtítulos (Linha começando com #)
        if linha_clean.startswith("#"):
            conteudo = re.sub(r'^#\s*', '', linha)
            linhas_formatadas.append(f"<h4 style='margin-top: 14px; margin-bottom: 6px; color: #1A202C; font-weight: 700;'>{conteudo}</h4>")
        
        # 2. Citações (Linha começando com “)
        elif linha_clean.startswith("“") or linha_clean.startswith('"'):
            conteudo = re.sub(r'^[“"]\s*', '', linha)
            linhas_formatadas.append(f"<blockquote style='border-left: 4px solid #CBD5E0; padding-left: 12px; color: #4A5568; font-style: italic; margin: 8px 0; background-color: #F7FAFC; padding-top: 4px; padding-bottom: 4px;'>{conteudo}</blockquote>")
        
        else:
            # 3. Processamento de Cores (Suporta Inglês e Português perfeitamente)
            padrao_cor = r':(red|vermelho|blue|azul|green|verde|orange|laranja|violet|roxo)\[(.*?)\]'
            def substituir_cor(match):
                cor_nome = match.group(1).lower()
                conteudo_cor = match.group(2)
                mapa_cores = {
                    "red": "#E53E3E", "vermelho": "#E53E3E",
                    "blue": "#1976D2", "azul": "#1976D2",
                    "green": "#38A169", "verde": "#38A169",
                    "orange": "#E65100", "laranja": "#E65100",
                    "violet": "#7B1FA2", "roxo": "#7B1FA2"
                }
                return f"<span style='color: {mapa_cores.get(cor_nome, '#2D3748')}; font-weight: 600;'>{conteudo_cor}</span>"
            
            linha = re.sub(padrao_cor, substituir_cor, linha, flags=re.IGNORECASE)
            
            # 4. Negrito (*)
            linha = re.sub(r'\*(.*?)\*', r'<strong>\1</strong>', linha)
            
            # 5. Itálico (_)
            linha = re.sub(r'_(.*?)_', r'<em>\1</em>', linha)
            
            # 6. Sublinhado (=)
            linha = re.sub(r'=(.*?)=', r'<u>\1</u>', linha)
            
            # Gerenciamento de linhas em branco para espaçamento correto
            if not linha_clean:
                linhas_formatadas.append("<div style='height: 10px;'></div>")
            else:
                linhas_formatadas.append(f"<p style='margin: 4px 0; line-height: 1.5; color: #2D3748;'>{linha}</p>")
                
    return "".join(linhas_formatadas)

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
    
    # Executa o motor de formatação customizado com suporte a HTML
    conteudo_renderizado = formatar_texto_customizado(nota['conteudo'])
    st.markdown(conteudo_renderizado, unsafe_allow_html=True)
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

# --- BARRA LATERAL (CENTRAL DE CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    
    st.write("**Gerenciar Subeixos**")
    eixo_alvo = st.selectbox("Selecione o eixo principal", EIXOS_FIXOS, key="config_eixo_alvo")
    nova_tag = st.text_input(f"Novo subeixo para {eixo_alvo}", key="config_nova_tag")
    if st.button("Adicionar Subeixo", key="btn_add_subeixo", use_container_width=True):
        if nova_tag and nova_tag not in subeixos_db[eixo_alvo]:
            subeixos_db[eixo_alvo].append(nova_tag)
            salvar_subeixos(subeixos_db)
            st.success("Adicionado!")
            st.rerun()
            
    tag_para_remover = st.selectbox("Remover subeixo existente", [""] + subeixos_db[eixo_alvo], key="config_remover_tag")
    if st.button("Remover Subeixo", key="btn_rem_subeixo", use_container_width=True):
        if tag_para_remover:
            subeixos_db[eixo_alvo].remove(tag_para_remover)
            salvar_subeixos(subeixos_db)
            st.success("Removido!")
            st.rerun()
            
    st.markdown("---")
    
    st.write("**Gerenciar Notas**")
    notes_painel = carregar_notas()
    if notes_painel:
        busca_gerenciar = st.text_input("🔍 Filtrar nota para exclusão", key="busca_gerenciar_nota")
        
        opcoes_remover_notas = []
        mapeamento_indices = {}
        
        for idx_real, n in enumerate(notes_painel):
            eixo_n = n.get('eixo', 'Clínica')
            sub_n = f" | {n.get('subeixo')}" if n.get('subeixo') else ""
            label_nota = f"{eixo_n}{sub_n} - {n['titulo']}"
            
            termo_busca = busca_gerenciar.lower()
            if not busca_gerenciar or (termo_busca in label_nota.lower() or termo_busca in n['conteudo'].lower()):
                opcoes_remover_notas.append(label_nota)
                mapeamento_indices[label_nota] = idx_real
        
        nota_alvo_remover = st.selectbox("Selecionar nota para excluir", [""] + opcoes_remover_notas, key="config_remover_nota")
        
        if st.button("Excluir Nota", key="btn_rem_nota_sidebar", use_container_width=True):
            if nota_alvo_remover and nota_alvo_remover in mapeamento_indices:
                idx_remover = mapeamento_indices[nota_alvo_remover]
                notes_painel.pop(idx_remover)
                with open(ARQUIVO_NOTAS, "w", encoding="utf-8") as f:
                    json.dump(notes_painel, f, ensure_ascii=False, indent=4)
                st.success("Nota excluída!")
                st.rerun()
    else:
        st.caption("Nenhuma nota salva no banco de dados.")

# ==========================================
# ROTEAMENTO DE TELAS
# ==========================================

if st.session_state.pagina == "home":
    st.title("🏥 Medicina")
    
    if st.button("Nova Nota", type="primary", use_container_width=True, key="btn_nova_nota_main"):
        st.session_state.modo_editor = "criar"
        st.session_state.edit_titulo = ""
        st.session_state.edit_conteudo = ""
        popup_selecionar_materia()
        
    st.markdown("---")
    
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
    sub_titulo = f" 🔸 {st.session_state.subeixo_selecionado}" if st.session_state.subeixo_selecionado else ""
    
    if st.session_state.modo_editor == "editar":
        st.title(f"✏️ Editando: {st.session_state.eixo_selecionado}{sub_titulo}")
    else:
        st.title(f"📁 Nova Nota: {st.session_state.eixo_selecionado}{sub_titulo}")
    
    titulo_nota = st.text_input("Título do Caso ou Aula", value=st.session_state.edit_titulo, key="editor_titulo")
    conteudo_nota = st.text_area("Suas anotações...", value=st.session_state.edit_conteudo, height=380, key="editor_conteudo")
    
    # --- ATUALIZADO: GUIA DE FORMATAÇÃO DO TEXTO CUSTOMIZADO ---
    with st.expander("💡 Guia de Formatação Rápida (Toque para ver os novos comandos)"):
        st.markdown("""
        Você pode estilizar suas anotações digitando estes comandos simples direto no texto:
        * *Negrito:* Use apenas um asterisco simples em cada ponta. Ex: `*hipertensão*` vira **hipertensão**.
        * _Itálico:_ Use um sublinhado/underline. Ex: `_Staphylococcus_` vira *Staphylococcus*.
        * # Subtítulos: Digite a hashtag seguida de um espaço no início da linha. Ex: `# Conduta`
        * =Sublinhar=: Use o sinal de igual em cada ponta. Ex: `=checar exames=` vira <u>checar exames</u>.
        * “ Citação: Digite as aspas normais no início de uma linha para criar um bloco cinza. Ex: `“ Paciente relata dor crônica...`
        * **Texto Colorido Correto (Suporta Português!):** Use o padrão `:cor[seu texto]`. 
          * Exemplos: `:vermelho[Alerta Máximo]`, `:azul[Ajuste de Dose]`, `:verde[Paciente Estável]`, `:roxo[Genética]`, `:laranja[Cirúrgico]`.
        """)
    
    col_salvar, col_cancelar = st.columns(2)
    
    with col_salvar:
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
