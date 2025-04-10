import streamlit as st
import json
from datetime import datetime, timedelta, date
import smtplib
from email.message import EmailMessage
import os

ARQUIVO_CONTRATOS = "contratos.json"
EMAIL_DESTINO = "caua.machado@abnt.org.br"

def carregar_contratos():
    if not os.path.exists(ARQUIVO_CONTRATOS):
        return []
    with open(ARQUIVO_CONTRATOS, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def salvar_contratos(contratos):
    with open(ARQUIVO_CONTRATOS, "w", encoding="utf-8") as f:
        json.dump(contratos, f, indent=4, ensure_ascii=False)

def enviar_email_assincrono(contrato):
    try:
        msg = EmailMessage()
        msg.set_content(f"Lembrete: Contrato com {contrato['nome']} ({contrato['documento']}) foi cadastrado há {contrato['dias']} dias.")
        msg["Subject"] = "🔔 Lembrete de Contrato"
        msg["From"] = "nao-responda@seudominio.com"
        msg["To"] = EMAIL_DESTINO

        with smtplib.SMTP("localhost") as server:
            server.send_message(msg)
    except Exception as e:
        print("Erro ao enviar e-mail:", e)

def verificar_lembretes():
    contratos = carregar_contratos()
    hoje = date.today()
    lembretes = []

    for c in contratos:
        if "data_criacao" not in c:
            continue

        try:
            data_criacao = datetime.strptime(c["data_criacao"], "%Y-%m-%d").date()
        except ValueError:
            continue

        dias_passados = (hoje - data_criacao).days

        if dias_passados in [15, 30, 90]:
            lembrete = {
                "nome": c["nome"],
                "email": c["email"],
                "documento": c["documento"],
                "dias": dias_passados,
                "resumo": c.get("resumo", "Não informado")
            }
            lembretes.append(lembrete)
            enviar_email_assincrono(lembrete)

    return lembretes


st.set_page_config(page_title="Sistema de Contratos", layout="centered")
st.title("📋 Sistema de Gerenciamento de Contratos")

aba = st.sidebar.radio("Navegação", ["Cadastro", "Contratos"])
lembretes = verificar_lembretes()

if lembretes:
    st.subheader("🔔 Lembretes de Contratos")
    for l in lembretes:
        st.warning(f"Contrato de {l['nome']} ({l['documento']}) cadastrado há {l['dias']} dias.")
else:
    st.info("Nenhum lembrete de contrato no momento.")

if aba == "Cadastro":
    st.subheader("📌 Cadastro de Novo Contrato")

    nome = st.text_input("Nome completo")
    email = st.text_input("Email")
    documento = st.text_input("CPF ou CNPJ")
    resumo = st.text_area("Mini currículo / Resumo do contrato")
    data_teste = st.date_input("📅 Data de Criação (opcional - para testes)", value=None)

    if st.button("Salvar Contrato"):
        if nome and email and documento:
            data_criacao = data_teste if data_teste else date.today()

            novo_contrato = {
                "nome": nome,
                "email": email,
                "documento": documento,
                "resumo": resumo,
                "data_criacao": str(data_criacao)
            }

            contratos = carregar_contratos()
            contratos.append(novo_contrato)
            salvar_contratos(contratos)

            st.success("✅ Contrato salvo com sucesso!")
        else:
            st.error("Preencha todos os campos obrigatórios.")

elif aba == "Contratos":
    st.subheader("📑 Contratos Registrados")
    contratos = carregar_contratos()

    if contratos:
        for c in contratos:
            st.write(f"👤 Nome: {c['nome']}")
            st.write(f"📧 Email: {c['email']}")
            st.write(f"🧾 CPF/CNPJ: {c['documento']}")
            st.write(f"📅 Data de Criação: {c.get('data_criacao', 'Desconhecida')}")
            st.write(f"📌 Mini Currículo: {c.get('resumo', 'Não informado')}")
            st.markdown("---")
    else:
        st.info("Nenhum contrato cadastrado ainda.")
