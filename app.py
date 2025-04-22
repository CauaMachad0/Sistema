import streamlit as st
import json
import os
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CAMINHO_ARQUIVO = 'contratos.json'
EMAIL_ADMIN = "caua.machado@abnt.org.br"

st.set_page_config(page_title="Gestão de Contratos", layout="wide")

# Funções auxiliares
def carregar_contratos():
    if os.path.exists(CAMINHO_ARQUIVO):
        with open(CAMINHO_ARQUIVO, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def salvar_contratos(contratos):
    with open(CAMINHO_ARQUIVO, 'w') as f:
        json.dump(contratos, f, indent=4)

def enviar_email(lembretes):
    if not lembretes:
        return

    remetente = "seuemail@gmail.com"  # Substitua pelo seu
    senha = "sua_senha_de_app"         # Use senha de app do Gmail ou outro serviço

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = EMAIL_ADMIN
    msg['Subject'] = "📌 Lembretes de Contratos"

    corpo = ""
    for l in lembretes:
        corpo += f"Contrato: {l['nome']} | Email: {l['email']} | Dias restantes: {l['dias_restantes']}\n"

    msg.attach(MIMEText(corpo, 'plain'))

    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remetente, senha)
        servidor.send_message(msg)
        servidor.quit()
        st.success("📧 Email de lembretes enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar email: {e}")

def verificar_lembretes():
    contratos = carregar_contratos()
    hoje = datetime.today().date()
    lembretes = []

    for c in contratos:
        try:
            data_criacao = datetime.strptime(c['data_criacao'], "%Y-%m-%d").date()
        except:
            continue
        for dias in [15, 30, 90]:
            if (hoje - data_criacao).days == dias:
                lembretes.append({
                    "nome": c["razao_social"],
                    "email": c["email"],
                    "dias_restantes": dias,
                    "documento": c.get("documento", "")
                })
    return lembretes

# Layout principal
st.title("📋 Gestão de Contratos de Treinamentos")

aba = st.sidebar.selectbox("Selecione a opção", ["Criar Cadastro", "Buscar Contratos"])

lembretes = verificar_lembretes()
if lembretes:
    st.subheader("📢 Lembretes de Contratos:")
    for l in lembretes:
        st.warning(f"Contrato: {l['nome']} | Email: {l['email']} | Dias desde criação: {l['dias_restantes']}")
else:
    st.info("Nenhum lembrete para hoje.")

def validar_documento(doc):
    return doc.isdigit() and len(doc) in [11, 14]

if aba == "Criar Cadastro":
    st.header("📝 Criar Cadastro de Contrato")
    with st.form("formulario_cadastro"):
        razao_social = st.text_input("Razão Social / Nome")
        documento = st.text_input("CPF (11 dígitos) ou CNPJ (14 dígitos) - apenas números")
        st.caption("Insira somente números. CPF deve conter 11 dígitos e CNPJ deve conter 14 dígitos.")
        instrutor = st.text_input("Nome do Instrutor")
        telefone = st.text_input("Telefone", placeholder="Ex: +55 (11) 91234-5678")
        numero_contrato = st.text_input("Número do Contrato")
        descricao = st.text_area("Descrição do Treinamento")
        dias_vencimento = st.number_input("Dias até vencimento", min_value=1, value=90)
        honorario_aberto = st.text_input("Honorário - Turma Aberta")
        honorario_company = st.text_input("Honorário - In Company")
        minimo_curso = st.text_input("Mínimo para ministrar o curso (opcional)")
        email = st.text_input("Email do Cliente")
        resumo = st.text_area("Mini Currículo (resumo)")

        submit = st.form_submit_button("Salvar Cadastro")

        if submit:
            if not validar_documento(documento):
                st.error("Por favor, insira um CPF (11 dígitos) ou CNPJ (14 dígitos) válido, sem pontos ou traços.")
            else:
                novo = {
                    "razao_social": razao_social,
                    "instrutor": instrutor,
                    "telefone": telefone,
                    "numero_contrato": numero_contrato,
                    "descricao": descricao,
                    "dias_vencimento": dias_vencimento,
                    "honorario_aberto": honorario_aberto,
                    "honorario_company": honorario_company,
                    "minimo_curso": minimo_curso,
                    "email": email,
                    "documento": documento,
                    "resumo": resumo,
                    "data_criacao": datetime.today().strftime("%Y-%m-%d")
                }
                contratos = carregar_contratos()
                contratos.append(novo)
                salvar_contratos(contratos)
                st.success("Contrato cadastrado com sucesso!")

elif aba == "Buscar Contratos":
    st.header("🔍 Buscar Contratos")
    contratos = carregar_contratos()
    busca = st.text_input("Buscar por razão social ou número do contrato")

    resultados = [c for c in contratos if busca.lower() in c.get("razao_social", "").lower() or busca in c.get("numero_contrato", "")] if busca else contratos

    for c in resultados:
        st.write(f"👤 Nome: {c['razao_social']}")
        st.write(f"📧 Email: {c['email']}")
        st.write(f"🧾 CPF/CNPJ: {c['documento']}")
        st.write(f"📅 Data de Criação: {c.get('data_criacao', 'Desconhecida')}")
        st.write(f"📌 Mini Currículo: {c.get('resumo', 'Não informado')}")
        st.markdown("---")

if __name__ == '__main__':
    os.system("start cmd /c streamlit run app.py")
