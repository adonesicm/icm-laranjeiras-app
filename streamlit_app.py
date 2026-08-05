import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
import calendar

st.set_page_config(page_title="ICM Laranjeiras - Controle", layout="wide")

# CSS COM CORES DA ICM - DOURADO E PRETO
st.markdown("""
<style>
.stApp {
        background: linear-gradient(135deg, #FFD700 0%, #FFF8DC 100%);
    }
    h1, h2, h3 {
        color: #000!important;
    }
.stTabs [data-baseweb="tab-list"] {
        background-color: #000;
        border-radius: 8px;
        padding: 5px;
    }
.stTabs [data-baseweb="tab"] {
        color: #FFD700;
        font-weight: bold;
    }
.stTabs [aria-selected="true"] {
        background-color: #FFD700!important;
        color: #000!important;
        border-radius: 5px;
    }
.stButton>button {
        background-color: #000;
        color: #FFD700;
        border: 2px solid #FFD700;
        font-weight: bold;
    }
.stButton>button:hover {
        background-color: #FFD700;
        color: #000;
    }
    [data-testid="stMetricValue"] {
        color: #000;
    }
</style>
""", unsafe_allow_html=True)

# FORMATA DATA PARA DD/MM/AAAA
def formata_data(dt):
    return pd.to_datetime(dt).strftime('%d/%m/%Y')

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
st.title("ICM Laranjeiras - Controle")
if 'escala_df' not in st.session_state:
    st.session_state.escala_df = pd.DataFrame(columns=[
        'Data do Culto', 'Irmão da Palavra', 'Irmão do Louvor', 'Texto Lido', 'Irmão do Portão'
    ])
if 'frequencia_df' not in st.session_state:
    st.session_state.frequencia_df = pd.DataFrame(columns=[
        'Data do Culto', 'Membros (Adultos)', 'Visitantes (Adultos)', 'Crianças', 'Total'
    ])
if 'aniversariantes_df' not in st.session_state:
    st.session_state.aniversariantes_df = pd.DataFrame(columns=['Nome', 'Data Aniversário'])
if 'avisos' not in st.session_state:
    st.session_state.avisos = ""
if 'dons' not in st.session_state:
    st.session_state.dons = ""

aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs(["📅 Escala", "📊 Frequência", "📢 Avisos", "🎁 Dons", "🎂 Aniversários", "📜 Histórico"])

# ABA 1: ESCALA
with aba1:
    st.header("Cadastrar Escala do Culto")
    with st.form("form_escala"):
        data = st.date_input("Data do Culto", value=date.today(), format="DD/MM/YYYY")
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

# ABA 2: FREQUENCIA + FOLHETO
with aba2:
    st.header("Lançar Frequência do Culto")
    with st.form("form_frequencia"):
        data_f = st.date_input("Data do Culto", value=date.today(), key="data_f", format="DD/MM/YYYY")
        col1, col2, col3 = st.columns(3)
        with col1: membros = st.number_input("Membros", min_value=0, step=1)
        with col2: visitantes = st.number_input("Visitantes", min_value=0, step=1)
        with col3: criancas = st.number_input("Crianças", min_value=0, step=1)
        total = membros + visitantes + criancas
        st.metric("Total de Pessoas", total)
        enviado_f = st.form_submit_button("Salvar Frequência")
        if enviado_f:
            nova_f = pd.DataFrame([{'Data do Culto': data_f, 'Membros (Adultos)': membros, 'Visitantes (Adultos)': visitantes, 'Crianças': criancas, 'Total': total}])
            st.session_state.frequencia_df = pd.concat([st.session_state.frequencia_df, nova_f], ignore_index=True)
            st.success("Frequência salva!")

    st.divider()
    st.subheader("📜 Gerar e Compartilhar Folheto do Culto")
    data_folheto = st.date_input("Selecione a data do culto", value=date.today(), key="data_folheto", format="DD/MM/YYYY")

    if st.button("Gerar Folheto para WhatsApp"):
        esc_dia = st.session_state.escala_df[st.session_state.escala_df['Data do Culto'] == data_folheto]
        mes_atual = data_folheto.month
        aniv_mes = st.session_state.aniversariantes_df[pd.to_datetime(st.session_state.aniversariantes_df['Data Aniversário']).dt.month == mes_atual]

        versiculo = "Aguardando definição"
        if not esc_dia.empty:
            versiculo = esc_dia.iloc[0]['Texto Lido']

        folheto = f"*FOLHETO ICM LARANJEIRAS*\n"
        folheto += f"*Culto do dia: {formata_data(data_folheto)}*\n\n"

        if not esc_dia.empty:
            e = esc_dia.iloc[0]
            folheto += f"*PROGRAMAÇÃO:*\n"
            folheto += f" Palavra: {e['Irmão da Palavra']}\n"
            folheto += f" Louvor: {e['Irmão do Louvor']}\n"
            folheto += f" Portão: {e['Irmão do Portão']}\n"
            folheto += f" Texto Base: {e['Texto Lido']}\n\n"
        else:
            folheto += f"*PROGRAMAÇÃO:*\nAguardando definição da escala\n"

        folheto += f"*VERSÍCULO DO DIA:*\n{versiculo}\n\n"

        if st.session_state.dons.strip()!= "":
            folheto += f"*DONS ESPIRITUAIS:*\n{st.session_state.dons}\n\n"

        if not aniv_mes.empty:
            folheto += f"*🎂 ANIVERSARIANTES DE {calendar.month_name[mes_atual].upper()}*\n"
            for _, row in aniv_mes.iterrows():
                dia = pd.to_datetime(row['Data Aniversário']).strftime('%d/%m')
                folheto += f"• {row['Nome']} - {dia}\n"
            folheto += "\n"

        if st.session_state.avisos.strip()!= "":
            folheto += f"*AVISOS E REUNIÕES:*\n{st.session_state.avisos}\n\n"

        folheto += f"_Que Deus te abençoe_"

        url_whatsapp = f"https://wa.me/?text={urllib.parse.quote(folheto)}"
        st.link_button("📤 Enviar Folheto no WhatsApp", url_whatsapp)
        st.code(folheto, language="text")

# ABA 3: AVISOS
with aba3:
    st.header("Editar Avisos e Reuniões")
    st.text_area("Digite os avisos que vão no folheto", key="avisos", height=200, placeholder="Digite os avisos aqui...")
    st.info("Deixe em branco se não tiver avisos para este culto")

# ABA 4: DONS ESPIRITUAIS
with aba4:
    st.header("Dons Espirituais")
    st.text_area("Digite os dons espirituais do culto", key="dons", height=200, placeholder="Ex: Profecia, Palavra de Sabedoria, Cura...")
    st.info("Deixe em branco se não houver manifestação de dons")

# ABA 5: ANIVERSARIANTES
with aba5:
    st.header("Cadastrar Aniversariantes")
    with st.form("form_aniv"):
        nome = st.text_input("Nome")
        data_aniv = st.date_input("Data de Aniversário", format="DD/MM/YYYY")
        enviado_aniv = st.form_submit_button("Salvar Aniversariante")
        if enviado_aniv:
            novo_aniv = pd.DataFrame([{'Nome': nome, 'Data Aniversário': data_aniv}])
            st.session_state.aniversariantes_df = pd.concat([st.session_state.aniversariantes_df, novo_aniv], ignore_index=True)
            st.success("Aniversariante salvo!")
    if not st.session_state.aniversariantes_df.empty:
        df_aniv = st.session_state.aniversariantes_df.copy()
        df_aniv['Data Aniversário'] = pd.to_datetime(df_aniv['Data Aniversário']).dt.strftime('%d/%m/%Y')
        st.dataframe(df_aniv, use_container_width=True)

# ABA 6: HISTORICO
with aba6:
    st.header("Histórico")
    if not st.session_state.frequencia_df.empty:
        st.session_state.frequencia_df['Data do Culto'] = pd.to_datetime(st.session_state.frequencia_df['Data do Culto'])
        data_min = st.session_state.frequencia_df['Data do Culto'].min().date()
        data_max = st.session_state.frequencia_df['Data do Culto'].max().date()
        data_range = st.date_input("Filtrar por período", value=(data_min, data_max), min_value=data_min, max_value=data_max, format="DD/MM/YYYY")
        df_filtrado = st.session_state.frequencia_df[
            (st.session_state.frequencia_df['Data do Culto'].dt.date >= data_range[0]) &
            (st.session_state.frequencia_df['Data do Culto'].dt.date <= data_range[1])
        ]
        df_filtrado['Data do Culto'] = df_filtrado['Data do Culto'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Nenhuma frequência lançada ainda.")
    st.subheader("Escalas Cadastradas")
    if not st.session_state.escala_df.empty:
        df_escala = st.session_state.escala_df.copy()
        df_escala['Data do Culto'] = pd.to_datetime(df_escala['Data do Culto']).dt.strftime('%d/%m/%Y')
        st.dataframe(df_escala, use_container_width=True)
