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
def painel_administrativo():
    st.title("Painel Administrativo")
    appointments = api_request(URLS["get_appointments"])
    if appointments:
        df = pd.DataFrame(appointments)
        st.dataframe(df, use_container_width=True)
        for _, row in df.iterrows():
            cols = st.columns([4, 1])
            with cols[1]:
                if st.button("Excluir", key=row["id"]):
                    api_request(URLS["delete_appointment"].replace(":id", str(row["id"])), method="DELETE")
                    st.experimental_rerun()
    else:
        st.warning("Nenhum agendamento encontrado.")

def clientes():
    st.title("Clientes")
    clients = api_request(URLS["get_clients"])
    df = pd.DataFrame(clients) if clients else pd.DataFrame(columns=["Nenhum cliente encontrado"])
    st.dataframe(df, use_container_width=True)

def novo_agendamento():
    st.title("Novo Agendamento")
    st.warning("Funcionalidade de agendamento ainda não implementada.")

# Navegação entre páginas
pages = {"Painel Administrativo": painel_administrativo, "Clientes": clientes, "Novo Agendamento": novo_agendamento}
selected_page = st.sidebar.selectbox("Menu", pages.keys())
pages[selected_page]()
