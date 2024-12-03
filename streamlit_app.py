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

# Painel Administrativo: Tabela com opções de Alterar e Excluir
def painel_administrativo():
    st.title("Painel Administrativo - Agendamentos")

    # Buscar agendamentos
    appointments = api_request(URLS["get_appointments"])
    if appointments:
        df = pd.DataFrame(appointments)
        df["Ações"] = None  # Coluna vazia para botões
        st.dataframe(df, use_container_width=True)

        # Criar botões para cada registro
        for index, row in df.iterrows():
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Alterar", key=f"edit_{row['id']}"):
                    st.info(f"Funcionalidade de edição não implementada para ID {row['id']}")
            with col2:
                if st.button("Excluir", key=f"delete_{row['id']}"):
                    delete_appointment(row["id"])
    else:
        st.warning("Nenhum agendamento encontrado.")

# Página de Clientes
def clientes():
    st.title("Clientes")
    clients = api_request(URLS["get_clients"])
    if clients:
        df = pd.DataFrame(clients)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhum cliente cadastrado no momento.")

# Página de Novo Agendamento
def novo_agendamento():
    st.title("Novo Agendamento")
    st.warning("Funcionalidade de agendamento ainda não implementada.")

# Ação de Exclusão de Agendamento
def delete_appointment(appointment_id):
    endpoint = URLS["delete_appointment"].replace(":id", str(appointment_id))
    if api_request(endpoint, method="DELETE"):
        st.success(f"Agendamento ID {appointment_id} deletado com sucesso!")
        st.experimental_rerun()

# Navegação entre páginas
pages = {
    "Painel Administrativo": painel_administrativo,
    "Clientes": clientes,
    "Novo Agendamento": novo_agendamento,
}

st.sidebar.title("Menu")
for page_name, page_func in pages.items():
    if st.sidebar.button(page_name):
        st.session_state["current_page"] = page_name

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Painel Administrativo"

pages[st.session_state["current_page"]]()
