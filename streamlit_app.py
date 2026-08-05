import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import urllib.parse
import calendar

st.set_page_config(page_title="ICM Laranjeiras - Controle", layout="wide")

# 1. LOGIN COM SENHA
def check_password():
    def password_entered():
        if st.session_state["password"] == "icm2026":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("Digite a senha", type="password", on_change=password_entered, key="password")
        st.info("Senha padrão: `icm2026`")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Digite a senha", type="password", on_change=password_entered, key="password")
        st.error("😕 Senha incorreta")
        return False
    else:
        return True

if not check_password():
    st.stop()

# 2. BANCO DE DADOS
st.title(" ICM Laranjeiras - Escala e Frequência")
if 'escala_df' not in st.session_state:
    st.session_state.escala_df = pd.DataFrame(columns=[
        'Data do Culto', 'Irmão da Palavra', 'Irmão do Louvor', 'Texto Lido', 'Irmão do Portão'
    ])
if 'frequencia_df' not in st.session_state:
    st.session_state.frequencia_df = pd.DataFrame(columns=[
        'Data do Culto', 'Membros (Adultos)', 'Visitantes (Adultos)', 'Crianças', 'Total', 'Oferta'
    ])
if 'aniversariantes_df' not in st.session_state:
    st.session_state.aniversariantes_df = pd.DataFrame(columns=['Nome', 'Data Aniversário'])

aba1, aba2, aba3, aba4, aba5 = st.tabs(["📅 Escala", "📊 Frequência", "🎂 Aniversários", "📜 Histórico", "📈 Gráficos"])

# ABA 1: ESCALA
with aba1:
    st.header("Cadastrar Escala do Culto")
    with st.form("form_escala"):
        data = st.date_input("Data do Culto", value=date.today())
        col1, col2 = st.columns(2)
        with col1:
            palavra = st.text_input("Irmão da Palavra")
            texto = st.text_input("Texto Lido", placeholder="Ex: João 3:16")
        with col2:
            louvor = st.text_input("Irmão do Louvor")
            portao = st.text_input("Irmão do Portão")
        enviado = st.form_submit_button("Salvar Escala")
        if enviado:
            nova = pd.DataFrame([{'Data do Culto': data, 'Irmão da Palavra': palavra, 'Irmão do Louvor': louvor, 'Texto Lido': texto, 'Irmão do Portão': portao}])
            st.session_state.escala_df = pd.concat([st.session_state.escala_df, nova], ignore_index=True)
            st.success("Escala salva!")

# ABA 2: FREQUENCIA + OFERTA + WHATSAPP
with aba2:
    st.header("Lançar Frequência do Culto")
    with st.form("form_frequencia"):
        data_f = st.date_input("Data do Culto", value=date.today(), key="data_f")
        col1, col2, col3, col4 = st.columns(4)
        with col1: membros = st.number_input("Membros", min_value=0, step=1)
        with col2: visitantes = st.number_input("Visitantes", min_value=0, step=1)
        with col3: criancas = st.number_input("Crianças", min_value=0, step=1)
        with col4: oferta = st.number_input("Oferta R$", min_value=0.0, step=1.0, format="%.2f")
        total = membros + visitantes + criancas
        st.metric("Total de Pessoas", total)
        enviado_f = st.form_submit_button("Salvar Frequência")
        if enviado_f:
            nova_f = pd.DataFrame([{'Data do Culto': data_f, 'Membros (Adultos)': membros, 'Visitantes (Adultos)': visitantes, 'Crianças': criancas, 'Total': total, 'Oferta': oferta}])
            st.session_state.frequencia_df = pd.concat([st.session_state.frequencia_df, nova_f], ignore_index=True)
            st.success("Frequência salva!")

    st.divider()
    st.subheader("📤 Compartilhar Relatório do Dia")
    data_selecionada = st.date_input("Selecione a data para compartilhar", value=date.today(), key="data_share")

    if st.button("Gerar Mensagem para WhatsApp"):
        esc_dia = st.session_state.escala_df[st.session_state.escala_df['Data do Culto'] == data_selecionada]
        freq_dia = st.session_state.frequencia_df[st.session_state.frequencia_df['Data do Culto'] == data_selecionada]
        mes_atual = data_selecionada.month
        aniv_mes = st.session_state.aniversariantes_df[pd.to_datetime(st.session_state.aniversariantes_df['Data Aniversário']).dt.month == mes_atual]

        if freq_dia.empty and esc_dia.empty:
            st.warning("Nenhum dado lançado para esta data.")
        else:
            mensagem = f"*📊 RELATÓRIO ICM LARANJEIRAS*\n*Data: {data_selecionada.strftime('%d/%m/%Y')}*\n\n"

            if not freq_dia.empty:
                f = freq_dia.iloc[0]
                mensagem += f"*FREQUÊNCIA:*\n"
                mensagem += f"👥 Membros: {int(f['Membros (Adultos)'])}\n"
                mensagem += f"🙌 Visitantes: {int(f['Visitantes (Adultos)'])}\n"
                mensagem += f"👶 Crianças: {int(f['Crianças'])}\n"
                mensagem += f"*TOTAL: {int(f['Total'])} pessoas*\n"
                mensagem += f"💰 Oferta: R$ {f['Oferta']:.2f}\n\n"

            if not esc_dia.empty:
                e = esc_dia.iloc[0]
                mensagem += f"*ESCALA:*\n"
                mensagem += f"📖 Palavra: {e['Irmão da Palavra']}\n"
                mensagem += f"🎵 Louvor: {e['Irmão do Louvor']}\n"
                mensagem += f"🚪 Portão: {e['Irmão do Portão']}\n"
                mensagem += f"📜 Texto: {e['Texto Lido']}\n\n"

            if not aniv_mes.empty:
                mensagem += f"*🎂 ANIVERSARIANTES DE {calendar.month_name[mes_atual].upper()}*\n"
                for _, row in aniv_mes.iterrows():
                    dia = pd.to_datetime(row['Data Aniversário']).strftime('%d/%m')
                    mensagem += f"• {row['Nome']} - {dia}\n"

            url_whatsapp = f"https://wa.me/?text={urllib.parse.quote(mensagem)}"
            st.link_button("Enviar no WhatsApp", url_whatsapp)
            st.code(mensagem, language="text")

# ABA 3: ANIVERSARIANTES
with aba3:
    st.header("Cadastrar Aniversariantes")
    with st.form("form_aniv"):
        nome = st.text_input("Nome")
        data_aniv = st.date_input("Data de Aniversário")
        enviado_aniv = st.form_submit_button("Salvar Aniversariante")
        if enviado_aniv:
            novo_aniv = pd.DataFrame([{'Nome': nome, 'Data Aniversário': data_aniv}])
            st.session_state.aniversariantes_df = pd.concat([st.session_state.aniversariantes_df, novo_aniv], ignore_index=True)
            st.success("Aniversariante salvo!")
    st.dataframe(st.session_state.aniversariantes_df, use_container_width=True)

# ABA 4: HISTORICO
with aba4:
    st.header("Histórico")
    if not st.session_state.frequencia_df.empty:
        st.session_state.frequencia_df['Data do Culto'] = pd.to_datetime(st.session_state.frequencia_df['Data do Culto'])
        data_min = st.session_state.frequencia_df['Data do Culto'].min().date()
        data_max = st.session_state.frequencia_df['Data do Culto'].max().date()
        data_range = st.date_input("Filtrar por período", value=(data_min, data_max), min_value=data_min, max_value=data_max)
        df_filtrado = st.session_state.frequencia_df[
            (st.session_state.frequencia_df['Data do Culto'].dt.date >= data_range[0]) &
            (st.session_state.frequencia_df['Data do Culto'].dt.date <= data_range[1])
        ]
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Nenhuma frequência lançada ainda.")
    st.subheader("Escalas Cadastradas")
    st.dataframe(st.session_state.escala_df, use_container_width=True)

# ABA 5: GRAFICOS
with aba5:
    st.header("📈 Gráficos de Crescimento")
    if not st.session_state.frequencia_df.empty:
        df = st.session_state.frequencia_df.copy()
        df['Data do Culto'] = pd.to_datetime(df['Data do Culto'])
        df['Mês'] = df['Data do Culto'].dt.to_period('M').astype(str)
        st.subheader("Total de Pessoas por Mês")
        total_mes = df.groupby('Mês')['Total'].sum()
        fig1, ax1 = plt.subplots()
        total_mes.plot(kind='bar', ax=ax1, color='#FFD700')
        ax1.set_ylabel("Total de Pessoas")
        st.pyplot(fig1)
        st.subheader("Total de Ofertas por Mês")
        oferta_mes = df.groupby('Mês')['Oferta'].sum()
        fig3, ax3 = plt.subplots()
        oferta_mes.plot(kind='bar', ax=ax3, color='#2E8B57')
        ax3.set_ylabel("R$")
        st.pyplot(fig3)
    else:
        st.warning("Lance algumas frequências primeiro para ver os gráficos.")
