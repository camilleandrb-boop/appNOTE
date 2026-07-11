import streamlit as st
import json
import os
from datetime import date

# Nome do nosso arquivo de banco de dados local
ARQUIVO_NOTAS = "notas.json"

# Função para ler o arquivo e carregar as notas
def carregar_notas():
    if os.path.exists(ARQUIVO_NOTAS):
        with open(ARQUIVO_NOTAS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Função para adicionar uma nota nova ao arquivo
def salvar_nota(nova_nota):
    notas = carregar_notas()
    notas.append(nova_nota)
    with open(ARQUIVO_NOTAS, "w", encoding="utf-8") as f:
        json.dump(notas, f, ensure_ascii=False, indent=4)

# Configuração da página
st.set_page_config(page_title="Minhas Anotações", page_icon="📝")
st.title("📝 Anotações do Internato")

# --- MENU LATERAL ---
st.sidebar.header("Nova Anotação")
titulo = st.sidebar.text_input("Título ou Tema")
# Já deixei algumas áreas do internato e seus interesses pré-configurados!
materia = st.sidebar.selectbox(
    "Eixo/Matéria", 
    ["Pediatria", "Genética", "Clínica Médica", "Ginecologia e Obstetrícia", "Cirurgia Geral"]
)
conteudo = st.sidebar.text_area("Conteúdo da anotação")
data_atual = st.sidebar.date_input("Data", date.today())

# Lógica do Botão de Salvar
if st.sidebar.button("Salvar Nota"):
    if titulo and conteudo: # Só salva se não estiver em branco
        nova_nota = {
            "titulo": titulo,
            "materia": materia,
            "conteudo": conteudo,
            "data": str(data_atual)
        }
        salvar_nota(nova_nota)
        st.sidebar.success("Nota salva com sucesso!")
    else:
        st.sidebar.warning("Preencha o título e o conteúdo antes de salvar.")

# --- ÁREA PRINCIPAL ---
st.subheader("Anotações Salvas")
notas_salvas = carregar_notas()

if not notas_salvas:
    st.info("Nenhuma anotação salva ainda. Use o menu lateral para adicionar a primeira!")
else:
    # Mostra as notas da mais recente para a mais antiga (usando reversed)
    for nota in reversed(notas_salvas):
        # Cria uma caixinha sanfona para cada nota, deixando a tela limpa
        with st.expander(f"{nota['data']} - {nota['materia']}: {nota['titulo']}"):
            st.write(nota['conteudo'])
