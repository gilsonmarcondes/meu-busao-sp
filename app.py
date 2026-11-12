from datetime import datetime
import http.cookiejar
import json
import urllib.request
import streamlit as st

st.set_page_config(page_title="Meu Busão", page_icon="🚌", layout="centered")

# Puxa a chave com segurança do cofre da nuvem
TOKEN_API = st.secrets["SPTRANS_TOKEN"]

# --- DICIONÁRIO DE LINHAS (SEM MENU LATERAL) ---
LINHAS_CONFIG = {
    "4113-10 - Gentil de Moura": {
        "codigo_linha": 33536,
        "codigo_parada": 330016305,
    },
    "5028-10 - Metrô Alto do Ipiranga": {
        "codigo_linha": 78786,
        "codigo_parada": 330016305,
    },
    "5030-10 - Maria Estela": {
        "codigo_linha": 82986,
        "codigo_parada": 330016305,
    },
}

st.title("🚌 Painel de Próximos Ônibus")
st.subheader("📍 Av. Nazaré, 28 (Hosp. Ipiranga)")


def buscar_todas_as_previsoes():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj)
    )
    opener.addheaders = [("User-Agent", "Mozilla/5.0")]

    url_login = f"https://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={TOKEN_API}"
    todas_as_previsoes = []

    try:
        # Faz o login único
        if (
            opener.open(urllib.request.Request(url_login, method="POST"))
            .read()
            .decode("utf-8")
            == "true"
        ):
            # Varre cada linha configurada acima para o mesmo ponto
            for nome_linha, config in LINHAS_CONFIG.items():
                url_prev = f"https://api.olhovivo.sptrans.com.br/v2.1/Previsao?codigoParada={config['codigo_parada']}&codigoLinha={config['codigo_linha']}"
                try:
                    resposta = (
                        opener.open(urllib.request.Request(url_prev))
                        .read()
                        .decode("utf-8")
                    )
                    dados = json.loads(resposta)

                    if (
                        "p" in dados
                        and dados["p"]
                        and "l" in dados["p"]
                        and len(dados["p"]["l"]) > 0
                    ):
                        veiculos = dados["p"]["l"][0].get("vs", [])
                        for v in veiculos:
                            todas_as_previsoes.append({
                                "linha": nome_linha,
                                "horario": v.get("t"),
                                "carro": v.get("p"),
                            })
                except Exception:
                    continue

            # Ordena todas as previsões juntas pelo horário crescente (ex: 10:25, 10:27, 10:32)
            todas_as_previsoes.sort(key=lambda x: x["horario"])
            return todas_as_previsoes

        return None
    except Exception as e:
        return None


if st.button("🔄 Atualizar Todos os Horários", use_container_width=True):
    with st.spinner("Consultando radares da SPTrans..."):
        previsoes = buscar_todas_as_previsoes()
        agora = datetime.now().strftime("%H:%M:%S")

    if previsoes is None:
        st.error("❌ Falha ao conectar com a SPTrans.")
    elif len(previsoes) == 0:
        st.warning("😕 Nenhum ônibus a caminho de nenhuma das linhas neste momento.")
    else:
        st.caption(f"Última atualização: {agora}")
        for p in previsoes:
            # Exibe o resultado misturado e em ordem cronológica!
            st.success(
                f"⏰ **{p['horario']}** — **{p['linha']}**  *(Carro: {p['carro']})*"
            )
