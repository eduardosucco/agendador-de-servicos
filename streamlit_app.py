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
    "update_appointment": f"{BASE_URL}/agendamento/:id",  # Supondo que PUT seja usado para atualizar
}

# Streamlit interface
st.set_page_config(page_title="Plataforma de Agendamento", layout="wide")

# Função genérica para requisições
def api_request(url, method="GET", data=None):
    try:
        response = requests.request(method, url, json=data)
        response.raise_for_status()
        if method == "GET":
            return response.json()
        return True
    except Exception as e:
        st.error(f"Erro: {e}")
        return [] if method == "GET" else False

# Função para deletar agendamento
def delete_appointment(appointment_id):
    confirm = st.session_state.get(f"confirm_delete_{appointment_id}", False)
    
    if not confirm:
        if st.button("Confirmar Exclusão", key=f"confirm_{appointment_id}"):
            st.session_state[f"confirm_delete_{appointment_id}"] = True
            st.experimental_rerun()
    else:
        endpoint = URLS["delete_appointment"].replace(":id", str(appointment_id))
        if api_request(endpoint, method="DELETE"):
            st.success(f"Agendamento ID {appointment_id} deletado com sucesso!")
            st.session_state.pop(f"confirm_delete_{appointment_id}", None)
            st.experimental_rerun()

# Função para alterar agendamento
def alterar_agendamento(appointment_id):
    st.title("Alterar Agendamento")
    
    # Buscar detalhes do agendamento específico
    appointments = api_request(URLS["get_appointments"])
    appointment = next((item for item in appointments if item["id"] == appointment_id), None)
    
    if appointment:
        with st.form(key="alterar_form"):
            cliente = st.text_input("Cliente", value=appointment.get("cliente", ""))
            data = st.date_input("Data", value=pd.to_datetime(appointment.get("data")))
            hora = st.time_input("Hora", value=pd.to_datetime(appointment.get("hora")).time())
            servico = st.text_input("Serviço", value=appointment.get("servico", ""))
            
            submit_button = st.form_submit_button(label="Salvar Alterações")
            
            if submit_button:
                updated_data = {
                    "cliente": cliente,
                    "data": data.isoformat(),
                    "hora": hora.strftime("%H:%M:%S"),
                    "servico": servico
                }
                endpoint = URLS["update_appointment"].replace(":id", str(appointment_id))
                if api_request(endpoint, method="PUT", data=updated_data):
                    st.success("Agendamento alterado com sucesso!")
                    st.experimental_rerun()
    else:
        st.error("Agendamento não encontrado.")

# Função de Agendamentos
def agendamentos():
    st.title("Agendamentos")
    appointments = api_request(URLS["get_appointments"])
    
    if not appointments:
        st.warning("Nenhum agendamento encontrado.")
        return

    df = pd.DataFrame(appointments)

    # Processar e formatar dados
    if "appointment_time" in df.columns:
        appointment_times = pd.to_datetime(df["appointment_time"])
        df["Data"], df["Hora"] = appointment_times.dt.strftime("%d/%m/%Y"), appointment_times.dt.strftime("%H:%M")

    df = df.rename(columns={
        "name": "Nome e Sobrenome", 
        "phone": "Telefone", 
        "service": "Serviço", 
        "first_time": "Primeira Vez?"
    }).drop(columns=["id", "client_id", "created_at", "deleted_at", "appointment_time"], errors="ignore")

    if "Telefone" in df.columns:
        df["Telefone"] = df["Telefone"].astype(str)

    # Exibir tabela
    st.dataframe(df, use_container_width=True)

# Função de Clientes
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

# Função de Novo Agendamento
def novo_agendamento():
    st.title("Novo Agendamento")
    st.warning("Funcionalidade de agendamento ainda não implementada.")

# Menu de Navegação com Option Menu na Sidebar
with st.sidebar:
    selected = option_menu(
        "Menu", ["Agendamentos", "Clientes", "Novo Agendamento"],
        icons=["calendar-check", "people", "plus-circle"],
        menu_icon="cast", default_index=0
    )

# Navegar para a página selecionada
query_params = st.experimental_get_query_params()
if "page" in query_params and query_params["page"][0] == "alterar_agendamento" and "id" in query_params:
    alterar_agendamento(query_params["id"][0])
elif selected == "Agendamentos":
    agendamentos()
elif selected == "Clientes":
    clientes()
elif selected == "Novo Agendamento":
    novo_agendamento()
