import streamlit as st
import pandas as pd
import requests

# URLs dos seus endpoints no n8n
N8N_BASE_URL = "https://n8n.massadar.me/webhook/agendador-de-servicos"
GET_CLIENTS_URL = f"{N8N_BASE_URL}/clientes"
GET_APPOINTMENTS_URL = f"{N8N_BASE_URL}/agendamentos"
DELETE_APPOINTMENT_URL = f"{N8N_BASE_URL}/agendamento/:id"

# Função genérica para interagir com endpoints
def api_request(endpoint, method="GET", data=None, params=None):
    try:
        response = requests.request(method, endpoint, json=data, params=params)
        response.raise_for_status()
        return response.json() if method == "GET" else True
    except Exception as e:
        st.error(f"Erro: {e}")
        return [] if method == "GET" else False

# Configuração inicial
st.set_page_config(page_title="Agendador de Serviços", layout="wide")

# Sidebar com botões para navegação
menu_option = st.sidebar.radio("Menu", ["Painel Administrativo", "Clientes", "Novo Agendamento"])

# Página: Painel Administrativo
if menu_option == "Painel Administrativo":
    st.title("Painel Administrativo - Agendamentos")

    appointments = api_request(GET_APPOINTMENTS_URL)
    if appointments:
        st.write("Clique nos botões para editar ou excluir um agendamento.")
        for appointment in appointments:
            cliente = appointment.get("cliente", "Não informado")
            servico = appointment.get("servico", "Não informado")
            data = appointment.get("data", "Não informado")
            hora = appointment.get("hora", "Não informado")
            appointment_id = appointment.get("id")

            cols = st.columns([3, 1, 1])  # Divisão em colunas para o layout
            cols[0].write(f"**Cliente**: {cliente}, **Serviço**: {servico}, **Data**: {data}, **Hora**: {hora}")
            if cols[1].button("Editar", key=f"edit_{appointment_id}"):
                st.info(f"Funcionalidade de edição não implementada para ID {appointment_id}")
            if cols[2].button("Excluir", key=f"delete_{appointment_id}"):
                endpoint = DELETE_APPOINTMENT_URL.replace(":id", str(appointment_id))
                if api_request(endpoint, method="DELETE"):
                    st.success(f"Agendamento ID {appointment_id} deletado com sucesso!")

# Página: Clientes
elif menu_option == "Clientes":
    st.title("Clientes Cadastrados")

    clients = api_request(GET_CLIENTS_URL)
    if clients:
        df_clients = pd.DataFrame(clients)
        st.dataframe(df_clients, use_container_width=True)
    else:
        st.warning("Nenhum cliente cadastrado no momento.")

# Página: Novo Agendamento
elif menu_option == "Novo Agendamento":
    st.title("Novo Agendamento")

    st.subheader("Cadastrar Cliente")
    st.warning("Funcionalidade de cadastro de clientes não implementada.")

    st.subheader("Agendar Serviço")
    clients = api_request(GET_CLIENTS_URL)
    if clients:
        client_options = {f"{c['first_name']} {c['last_name']}": c['id'] for c in clients}
        appointment_data = {
            "client_id": st.selectbox("Cliente", list(client_options.values())),
            "service": st.text_input("Serviço"),
            "date": st.date_input("Data").isoformat(),
            "time": st.time_input("Hora").isoformat(),
            "comment": st.text_area("Comentário"),
        }
        if st.button("Agendar Serviço"):
            st.warning("Funcionalidade de agendamento de serviços não implementada.")
    else:
        st.warning("Nenhum cliente encontrado. Cadastre um cliente antes de agendar.")
