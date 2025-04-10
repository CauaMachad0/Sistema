import streamlit as st
import json
from datetime import datetime, timedelta

ARQUIVO = "contratos.json"

def carregar_contratos():
    try:
        with open(ARQUIVO, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return []

def salvar_contratos(contratos):
    with open(ARQUIVO, "w") as f:
        json.dump(contratos, f, indent=4)

def verificar_lembretes():
    hoje = datetime.today().date()
    contratos = carregar_contratos()
    lembretes = []
    for c in contratos:
        try:
            data_criacao = datetime.strptime(c['data_criacao'], "%Y-%m-%d").date()
        except KeyError:
            continue

        for dias in [15, 30, 90]:
            if (hoje - data_criacao).days == dias:
                lembretes.append({
                    "nome": c.get("razao_social", "Desconhecido"),
                    "instrutor": c.get("instrutor", "Desconhecido"),
                    "email": c.get("email", ""),
                    "telefone": c.get("telefone", ""),
                    "dias": dias
                })
    return lembretes

st.set_page_config(page_title="Sistema de Contratos", layout="centered")
st.title("📑 Sistema de Gestão de Contratos")

aba = st.sidebar.selectbox("Navegação", ["Criar Cadastro", "Buscar Contratos"])

if aba == "Criar Cadastro":
    st.header("📌 Cadastro de Novo Contrato")
    razao_social = st.text_input("Razão Social / Nome")
    instrutor = st.text_input("Nome do Instrutor")
    telefone = st.text_input("Telefone")
    contrato_num = st.text_input("Número do Contrato")
    descricao = st.text_area("Descrição do Treinamento")
    dias_para_vencer = st.number_input("Dias até o vencimento", min_value=1, value=30)
    honorario_aberto = st.text_input("Honorário - Turma Aberta")
    honorario_company = st.text_input("Honorário - In Company")
    minimo_turma = st.text_input("Mínimo para ministrar o curso (opcional)", value="Não definido")

    if st.button("Salvar Contrato"):
        if not (razao_social and instrutor and telefone and contrato_num):
            st.error("Por favor, preencha os campos obrigatórios.")
        else:
            contratos = carregar_contratos()
            novo_contrato = {
                "razao_social": razao_social,
                "instrutor": instrutor,
                "telefone": telefone,
                "numero_contrato": contrato_num,
                "descricao": descricao,
                "dias_para_vencer": dias_para_vencer,
                "honorario_aberto": honorario_aberto,
                "honorario_company": honorario_company,
                "minimo_turma": minimo_turma,
                "email": st.text_input("Email do responsável"),
                "data_criacao": datetime.today().strftime("%Y-%m-%d")
            }
            contratos.append(novo_contrato)
            salvar_contratos(contratos)
            st.success("Contrato cadastrado com sucesso!")

    st.markdown("## 🔔 Lembretes de Contratos")
    lembretes = verificar_lembretes()
    if lembretes:
        for l in lembretes:
            st.info(f"💬 Lembrete: O contrato de **{l['nome']}** com o instrutor **{l['instrutor']}** atingiu **{l['dias']} dias** desde o cadastro. 📧 {l['email']} | 📞 {l['telefone']}")
    else:
        st.write("✅ Nenhum lembrete no momento.")

elif aba == "Buscar Contratos":
    st.header("🔍 Buscar Contratos")
    contratos = carregar_contratos()

    busca = st.text_input("Pesquisar por nome, contrato ou instrutor")

    if busca:
        contratos = [
            c for c in contratos
            if busca.lower() in c.get("razao_social", "").lower()
            or busca.lower() in c.get("instrutor", "").lower()
            or busca.lower() in c.get("numero_contrato", "").lower()
        ]

    if contratos:
        for c in contratos:
            st.write(f"📄 Nº Contrato: {c.get('numero_contrato', 'N/A')}")
            st.write(f"🏢 Razão Social: {c.get('razao_social', 'N/A')}")
            st.write(f"👨‍🏫 Instrutor: {c.get('instrutor', 'N/A')}")
            st.write(f"📧 Email: {c.get('email', 'N/A')}")
            st.write(f"📞 Telefone: {c.get('telefone', 'N/A')}")
            st.write(f"📅 Data de Criação: {c.get('data_criacao', 'N/A')}")
            st.write(f"📝 Descrição: {c.get('descricao', '')}")
            st.write(f"💰 Honorário Turma Aberta: {c.get('honorario_aberto', '')}")
            st.write(f"🏢 Honorário In Company: {c.get('honorario_company', '')}")
            st.write(f"📊 Mínimo para ministrar: {c.get('minimo_turma', '')}")
            st.markdown("---")
    else:
        st.warning("Nenhum contrato encontrado.")
