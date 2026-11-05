import streamlit as st
import urllib.request
import json
import http.cookiejar
from datetime import datetime

st.set_page_config(page_title="Meu Busão", page_icon="🚌", layout="centered")

# Puxa a chave com segurança do cofre da nuvem
TOKEN_API = st.secrets["SPTRANS_TOKEN"]
CODIGO_LINHA = 33536      
CODIGO_PARADA = 330016305 

URL_LOGIN = f"https://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={TOKEN_API}"
URL_PREVISAO = f"https://api.olhovivo.sptrans.com.br/v2.1/Previsao?codigoParada={CODIGO_PARADA}&codigoLinha={CODIGO_LINHA}"

def buscar_horarios():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    
    try:
        if opener.open(urllib.request.Request(URL_LOGIN, method='POST')).read().decode('utf-8') == "true":
            dados = json.loads(opener.open(urllib.request.Request(URL_PREVISAO)).read().decode('utf-8'))
            if 'p' in dados and dados['p'] and 'l' in dados['p'] and len(dados['p']['l']) > 0:
                return dados['p']['l'][0]['vs']
        return []
    except Exception as e:
        return None

st.title("🚌 Radar 4113-10")
st.subheader("📍 Av. Nazaré, 28 (Hosp. Ipiranga)")

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