import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import requests

# Configuração
BASE_URL = "https://n8n.massadar.me/webhook/agendador-de-servicos"
URLS = {
    "get_clients": f"{BASE_URL}/clientes",
    "get_appointments": f"{BASE_URL}/agendamentos",
    "delete_appointment": f"{BASE_URL}/agendamento/:id",
    "update_appointment": f"{BASE_URL}/agendamento/:id",
}

st.set_page_config(page_title="Plataforma de Agendamento", layout="wide")

# Requisição genérica
def api_request(url, method="GET", data=None):
    try:
        response = requests.request(method, url, json=data)
        response.raise_for_status()
        return response.json() if method == "GET" else True
    except Exception as e:
        st.error(f"Erro: {e}")
        return [] if method == "GET" else False

# Deletar agendamento
def delete_appointment(appointment_id):
    confirm = st.session_state.get(f"confirm_{appointment_id}", False)
    if not confirm and st.button("Confirmar Exclusão", key=f"confirm_{appointment_id}"):
        st.session_state[f"confirm_{appointment_id}"] = True
        st.experimental_rerun()
    elif confirm and api_request(URLS["delete_appointment"].replace(":id", str(appointment_id)), "DELETE"):
        st.success(f"Agendamento ID {appointment_id} deletado com sucesso!")
        st.session_state.pop(f"confirm_{appointment_id}", None)
        st.experimental_rerun()

# Alterar agendamento
def alterar_agendamento(appointment_id):
    st.title("Alterar Agendamento")
    appointment = next((item for item in api_request(URLS["get_appointments"]) if item["id"] == appointment_id), None)
    if not appointment:
        st.error("Agendamento não encontrado.")
        return
    with st.form("alterar_form"):
        cliente, data, hora, servico = (
            st.text_input("Cliente", appointment["cliente"]),
            st.date_input("Data", pd.to_datetime(appointment["data"])),
            st.time_input("Hora", pd.to_datetime(appointment["hora"]).time()),
            st.text_input("Serviço", appointment["servico"]),
        )
        if st.form_submit_button("Salvar Alterações"):
            updated_data = {"cliente": cliente, "data": data.isoformat(), "hora": hora.strftime("%H:%M:%S"), "servico": servico}
            if api_request(URLS["update_appointment"].replace(":id", str(appointment_id)), "PUT", updated_data):
                st.success("Agendamento alterado com sucesso!")
                st.experimental_rerun()

# Página Agendamentos
def agendamentos():
    st.title("Agendamentos")
    appointments = api_request(URLS["get_appointments"])
    if not appointments:
        st.warning("Nenhum agendamento encontrado.")
        return
    df = pd.DataFrame(appointments)
    if "appointment_time" in df.columns:
        df["Data"], df["Hora"] = pd.to_datetime(df["appointment_time"]).dt.strftime("%d/%m/%Y"), pd.to_datetime(df["appointment_time"]).dt.strftime("%H:%M")
    if "phone" in df.columns:
        df["phone"] = df["phone"].astype(str)
    st.dataframe(df.rename(columns={
        "name": "Nome e Sobrenome", "phone": "Telefone", "service": "Serviço", "first_time": "Primeira Vez?"
    }).drop(columns=["id", "client_id", "created_at", "deleted_at", "appointment_time"], errors="ignore"), use_container_width=True)

# Página Clientes
def clientes():
    st.title("Clientes")
    clients = api_request(URLS["get_clients"])
    if not clients:
        st.warning("Nenhum cliente cadastrado no momento.")
        return
    df = pd.DataFrame(clients).rename(columns={"name": "Nome e Sobrenome", "phone": "Telefone"}).drop(columns=["id", "created_at"], errors="ignore")
    if "Telefone" in df.columns:
        df["Telefone"] = df["Telefone"].astype(str)
    st.dataframe(df, use_container_width=True)

# Página Novo Agendamento
def novo_agendamento():
    st.title("Novo Agendamento")

    # Substitua o URL abaixo pelo link do seu formulário JotForm
    jotform_url = "https://form.jotform.com/243372617278665"

    # Código do iframe para incorporar o formulário
    iframe_code = f"""
    <iframe 
        src="{jotform_url}" 
        width="100%" 
        height="800" 
        style="border:none;">
    </iframe>
    """

    # Exibir o formulário no Streamlit
    st.components.v1.html(iframe_code, height=800)

# Menu de Navegação
with st.sidebar:
    selected = option_menu(
        "Menu", ["Agendamentos", "Clientes", "Novo Agendamento"],
        icons=["calendar-check", "people", "plus-circle"], menu_icon="cast", default_index=0
    )

# Navegação
query_params = st.experimental_get_query_params()
if query_params.get("page", [None])[0] == "alterar_agendamento" and "id" in query_params:
    alterar_agendamento(query_params["id"][0])
elif selected == "Agendamentos":
    agendamentos()
elif selected == "Clientes":
    clientes()
elif selected == "Novo Agendamento":
    novo_agendamento()
