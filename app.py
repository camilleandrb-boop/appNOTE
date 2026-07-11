import streamlit as st
from datetime import date

# Configuração da página (Nome na aba do navegador e ícone)
st.set_page_config(page_title="Minhas Anotações", page_icon="📝")

st.title("📝 Anotações do Internato")

# Criando um menu lateral para adicionar notas
st.sidebar.header("Nova Anotação")
titulo = st.sidebar.text_input("Título ou Tema")
materia = st.sidebar.selectbox(
    "Eixo/Matéria", 
    ["Pediatria", "Genética", "Clínica Médica", "Ginecologia e Obstetrícia", "Cirurgia Geral"]
)
conteudo = st.sidebar.text_area("Conteúdo da anotação")
data_atual = st.sidebar.date_input("Data", date.today())

# Botão para salvar
if st.sidebar.button("Salvar Nota"):
    st.sidebar.success("Nota salva com sucesso! (Por enquanto é só a interface visual)")

# Área principal para leitura
st.subheader("Anotações Recentes")
st.info("Aqui aparecerão as suas anotações salvas no futuro.")
