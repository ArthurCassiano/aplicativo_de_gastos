import streamlit as st 
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

import database as db

#---------SETTINGS --------------#
incomes = ["Salário","Bicos","Outras Rendas"]
expenses = ["Aluguel","Contas","Supermercado","Carro", "Outros Gastos", "Economias"]
currency = "R$"
page_title = "Gestão de Ganhos e Gastos"
page_icon = ":money_with_wings:"
layout = "centered"

#---------------------------------------#

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " +page_icon)

years= [2023, 2024]
months= ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


# --- DATABASE INTERFACE ---
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods

# --- HIDE STREAMLIT STYLE // ESTILIZAÇAO ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

#--------------MENU DE NAVEGACAO-------------------------#
selected = option_menu(
    menu_title=None,
    options=["Entrada de Dados", "Visualização de Dados"],
    icons=["pencil-fill", "bar-chart-fill"],  # https://icons.getbootstrap.com/
    orientation="horizontal",
)



#----------INPUT AND SAVE PERIODS----------#
if selected == "Entrada de Dados":
    st.header(f'Entrada de dados em {currency}')
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Selecione o mês:", months, key="month" )
        col2.selectbox("Selecione o ano:", years, key="year" )

        "---"
        with st.expander("Salário"):
            for income in incomes:
                st.number_input(f'{income}:', min_value=0, format='%i', step=1, key=income)
        with st.expander("Gastos"):
            for expense in expenses:
                st.number_input(f'{expense}:', min_value=0, format='%i', step=1, key=expense)
        with st.expander("Comentários"):
            comment = st.text_area("", placeholder="Escreva seus comentários aqui ...")


        "---"

        submitted = st.form_submit_button("Salvar Dados")
        if submitted:
            period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            incomes = {income: st.session_state[income] for income in incomes}
            expenses = {expense: st.session_state[expense] for expense in expenses}
            db.insert_period(period, incomes, expenses, comment)
            st.success('Dados Salvos!') 

    #PLOT PERIODS
if selected == "Visualização de Dados":    
    st.header("Visualização de Dados")
    with st.form("saved_periods"):
            
        period = st.selectbox("Selecione um período:", get_all_periods())
        submitted = st.form_submit_button("Selecionar Período")
        if submitted:
             period_data = db.get_period(period)
             comment = period_data.get("comment")
             expenses = period_data.get("expenses")
             incomes = period_data.get("incomes")


        #----CRIAÇAO DE METRICAS
      
        total_income = sum(incomes.values())
        total_expense = sum(expenses.values())
        remaining_budget = total_income - total_expense
        col1, col2, col3 = st.columns(3)
        col1.metric("Ganhos Totais", f"{total_income} {currency}")
        col2.metric("Gastos Totais", f"{total_expense} {currency}")
        col3.metric("Valor Restante", f"{remaining_budget} {currency}")
        st.text(f"Comment: {comment}")



        # Criando sankey chart
        label = list(incomes.keys()) + ["Ganhos Totais"] + list(expenses.keys())
        source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
        target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
        value = list(incomes.values()) + list(expenses.values())

        # dados para o dict, dict para o sankey
        link = dict(source=source, target=target, value=value)
        node = dict(label=label, pad=20, thickness=30, color="#E694FF")
        data = go.Sankey(link=link, node=node)

        # Plot it!
        fig = go.Figure(data)
        fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
        st.plotly_chart(fig, use_container_width=True)