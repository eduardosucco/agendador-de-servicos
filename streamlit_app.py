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
}

# Streamlit interface
st.set_page_config(page_title="Plataforma de Agendamento", layout="wide")

# Função genérica para requisições
def api_request(url, method="GET", data=None):
    try:
        response = requests.request(method, url, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro: {e}")
        return []

# Funções das páginas
def agendamentos():
    st.title("Agendamentos")
    appointments = api_request(URLS["get_appointments"])
    if appointments:
        df = pd.DataFrame(appointments)
        st.dataframe(df, use_container_width=True)  # Ajusta ao tamanho da página
    else:
        st.warning("Nenhum agendamento encontrado.")

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

def agendamentos():
    st.title("Agendamentos")
    appointments = api_request(URLS["get_appointments"])
    if appointments:
        df = pd.DataFrame(appointments)

        # Adicionar coluna de botões para exclusão
        for index, row in df.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**Cliente**: {row['cliente']}, **Data**: {row['data']}, **Hora**: {row['hora']}")
            with col2:
                if st.button("Excluir", key=f"delete_{row['id']}"):
                    delete_appointment(row["id"])
    else:
        st.warning("Nenhum agendamento encontrado.")

def delete_appointment(appointment_id):
    endpoint = URLS["delete_appointment"].replace(":id", str(appointment_id))
    if api_request(endpoint, method="DELETE"):
        st.success(f"Agendamento ID {appointment_id} deletado com sucesso!")
        st.experimental_rerun()

# NavBar na Sidebar
with st.sidebar:
    selected = option_menu(
        "Menu", ["Agendamentos", "Clientes", "Novo Agendamento"],
        icons=["calendar-check", "people", "plus-circle"],
        menu_icon="cast", default_index=0
    )

def novo_agendamento():
    st.title("Novo Agendamento")
    
    # Formulário para cadastrar agendamento
    cliente = st.text_input("Nome do Cliente")
    data = st.date_input("Data do Agendamento")
    hora = st.time_input("Hora do Agendamento")
    servico = st.text_input("Serviço")
    
    if st.button("Cadastrar"):
        # Dados do novo agendamento
        agendamento = {
            "cliente": cliente,
            "data": str(data),
            "hora": str(hora),
            "servico": servico,
        }
        response = api_request(URLS["get_appointments"], method="POST", data=agendamento)
        if response:
            st.success("Agendamento cadastrado com sucesso!")
            st.experimental_rerun()

# Navegar para a página selecionada
if selected == "Agendamentos":
    agendamentos()
elif selected == "Clientes":
    clientes()
elif selected == "Novo Agendamento":
    novo_agendamento()
