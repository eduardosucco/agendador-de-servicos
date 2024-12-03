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

# Função para exibir DataFrame com ações
def show_table_with_actions(df, delete_action=None, edit_action=None):
    for idx, row in df.iterrows():
        cliente = row.get("cliente", "Não informado")
        servico = row.get("servico", "Não informado")
        data = row.get("data", "Não informado")
        hora = row.get("hora", "Não informado")
        cols = st.columns([4, 1, 1])  # Ajuste do layout
        with cols[0]:
            st.write(f"**Cliente**: {cliente} | **Serviço**: {servico} | **Data**: {data} | **Hora**: {hora}")
        with cols[1]:
            if st.button("Editar", key=f"edit_{row['id']}"):
                if edit_action:
                    edit_action(row)
        with cols[2]:
            if st.button("Excluir", key=f"delete_{row['id']}"):
                if delete_action:
                    delete_action(row)

# Páginas
def painel_administrativo():
    st.title("Painel Administrativo")
    appointments = api_request(URLS["get_appointments"])
    if appointments:
        df = pd.DataFrame(appointments)
        st.write("Clique em **Editar** para modificar ou **Excluir** para remover um agendamento.")
        show_table_with_actions(
            df,
            delete_action=lambda row: delete_appointment(row["id"]),
            edit_action=lambda row: st.info(f"Funcionalidade de edição não implementada para ID {row['id']}")
        )
    else:
        st.warning("Nenhum agendamento encontrado.")

def clientes():
    st.title("Clientes")
    clients = api_request(URLS["get_clients"])
    if clients:
        df = pd.DataFrame(clients)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhum cliente cadastrado no momento.")

def novo_agendamento():
    st.title("Novo Agendamento")
    st.warning("Funcionalidade de agendamento ainda não implementada.")

# Ações
def delete_appointment(appointment_id):
    endpoint = URLS["delete_appointment"].replace(":id", str(appointment_id))
    if api_request(endpoint, method="DELETE"):
        st.success(f"Agendamento ID {appointment_id} deletado com sucesso!")
        st.experimental_rerun()

# Navegação
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
