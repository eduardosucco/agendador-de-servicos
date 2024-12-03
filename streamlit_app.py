import streamlit as st
import pandas as pd
import requests

# Configuração
BASE_URL = "https://n8n.massadar.me/webhook/agendador-de-servicos"
URLS = {
    "get_clients": f"{BASE_URL}/clientes",
    "get_appointments": f"{BASE_URL}/agendamentos",
    "delete_appointment": f"{BASE_URL}/agendamento/:id",
}

# Função genérica para requisições
def api_request(url, method="GET", data=None):
    try:
        response = requests.request(method, url, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro: {e}")
        return []

# Páginas
def agendamentos():
    st.title("Agendamentos")
    st.write("Conteúdo da página de Agendamentos.")

def clientes():
    st.title("Clientes")
    clients = api_request(URLS["get_clients"])
    if clients:
        df = pd.DataFrame(clients)
        df = df.rename(columns={"name": "Nome e Sobrenome", "phone": "Telefone"})
        df = df.drop(columns=["id", "created_at"], errors="ignore")
        if "Telefone" in df.columns:
            df["Telefone"] = df["Telefone"].astype(str)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhum cliente cadastrado no momento.")

def novo_agendamento():
    st.title("Novo Agendamento")
    st.warning("Funcionalidade de agendamento ainda não implementada.")

# Configuração do menu com destaque
pages = {
    "Agendamentos": agendamentos,
    "Clientes": clientes,
    "Novo Agendamento": novo_agendamento,
}

# Inicializar estado da sessão
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Agendamentos"

# Estilo para o menu
menu_style = """
<style>
.sidebar .sidebar-content div[role="radiogroup"] > label {{
    font-size: 18px;
    font-weight: bold;
    background-color: {bg_color};
    color: {color};
    padding: 8px 16px;
    margin: 4px 0;
    border-radius: 5px;
}}
.sidebar .sidebar-content div[role="radiogroup"] > label:hover {{
    background-color: #F0F0F0;
    cursor: pointer;
}}
</style>
"""

# Renderizar menu lateral com destaque
st.sidebar.title("Menu")
for page_name in pages.keys():
    if st.sidebar.button(page_name, key=page_name):
        st.session_state["current_page"] = page_name

# Destacar a página selecionada
for page_name in pages.keys():
    bg_color = "#FFD700" if st.session_state["current_page"] == page_name else "#FFFFFF"
    color = "#000000" if st.session_state["current_page"] == page_name else "#666666"
    st.sidebar.markdown(menu_style.format(bg_color=bg_color, color=color), unsafe_allow_html=True)

# Renderizar página selecionada
pages[st.session_state["current_page"]]()
