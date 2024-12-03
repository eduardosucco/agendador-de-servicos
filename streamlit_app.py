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

# Configuração do NavBar
pages = {
    "Agendamentos": agendamentos,
    "Clientes": clientes,
    "Novo Agendamento": novo_agendamento,
}

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Agendamentos"

# Estilo da NavBar
navbar_style = """
<style>
.navbar {
    display: flex;
    justify-content: space-around;
    background-color: #F0F0F0;
    padding: 10px;
    border-bottom: 2px solid #CCCCCC;
}
.navbar-item {
    font-size: 18px;
    font-weight: bold;
    padding: 8px 16px;
    color: #666666;
    text-decoration: none;
    border-radius: 5px;
}
.navbar-item:hover {
    background-color: #E0E0E0;
}
.navbar-item-selected {
    background-color: #FFD700;
    color: #000000;
}
</style>
"""

# Renderizar NavBar
st.markdown(navbar_style, unsafe_allow_html=True)
navbar = '<div class="navbar">'
for page_name in pages.keys():
    css_class = "navbar-item-selected" if st.session_state["current_page"] == page_name else "navbar-item"
    navbar += f'<a href="#" class="{css_class}" onclick="window.location.reload();">{page_name}</a>'
navbar += "</div>"
st.markdown(navbar, unsafe_allow_html=True)

# Renderizar página selecionada
pages[st.session_state["current_page"]]()
