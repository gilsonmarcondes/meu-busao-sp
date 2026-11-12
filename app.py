from datetime import datetime
import http.cookiejar
import json
import urllib.request
import streamlit as st

st.set_page_config(page_title="Meu Busão", page_icon="🚌", layout="centered")

# Puxa a chave com segurança do cofre da nuvem
TOKEN_API = st.secrets["SPTRANS_TOKEN"]

# --- DICIONÁRIO DE LINHAS E PARAGENS ---
LINHAS_CONFIG = {
    "4113-10 - Gentil de Moura": {
        "codigo_linha": 33536,
        "codigo_parada": 330016305,
        "descricao_ponto": "📍 Av. Nazaré, 28 (Hosp. Ipiranga)",
    },
    "5028-10 - Heliópolis": {
        "codigo_linha": 78786,
        "codigo_parada": 330016305,
        "descricao_ponto": "📍 Ponto monitorado (Linha 5028-10)",
    },
}

st.title("🚌 Meu Busão")

# --- SELETOR LOGO ABAIXO DO TÍTULO (Ótimo para o telemóvel) ---
linha_selecionada = st.selectbox(
    "Escolha a linha para monitorizar:", list(LINHAS_CONFIG.keys())
)

# Puxa os dados da linha escolhida
config_atual = LINHAS_CONFIG[linha_selecionada]
CODIGO_LINHA = config_atual["codigo_linha"]
CODIGO_PARADA = config_atual["codigo_parada"]

st.subheader(config_atual["descricao_ponto"])

URL_LOGIN = (
    f"https://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={TOKEN_API}"
)
URL_PREVISAO = f"https://api.olhovivo.sptrans.com.br/v2.1/Previsao?codigoParada={CODIGO_PARADA}&codigoLinha={CODIGO_LINHA}"


def buscar_horarios():
  cj = http.cookiejar.CookieJar()
  opener = urllib.request.build_opener(
      urllib.request.HTTPCookieProcessor(cj)
  )
  opener.addheaders = [("User-Agent", "Mozilla/5.0")]

  try:
    if (
        opener.open(urllib.request.Request(URL_LOGIN, method="POST"))
        .read()
        .decode("utf-8")
        == "true"
    ):
      dados = json.loads(
          opener.open(urllib.request.Request(URL_PREVISAO))
          .read()
          .decode("utf-8")
      )
      if (
          "p" in dados
          and dados["p"]
          and "l" in dados["p"]
          and len(dados["p"]["l"]) > 0
      ):
        return dados["p"]["l"][0]["vs"]
    return []
  except Exception as e:
    return None


if st.button("🔄 Atualizar Horários", use_container_width=True):
  veiculos = buscar_horarios()
  agora = datetime.now().strftime("%H:%M:%S")

  if veiculos is None:
    st.error("❌ Falha ao conectar com a SPTrans.")
  elif len(veiculos) == 0:
    st.warning("😕 Nenhum ônibus a caminho neste momento.")
  else:
    st.caption(f"Última atualização: {agora}")
    for v in veiculos[:4]:
      st.success(f"⏰ **{v['t']}**  (Carro: {v['p']})")
