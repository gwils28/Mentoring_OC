"""Interface Streamlit : aucune logique de machine learning, elle interroge l'API et affiche les réponses.

API_URL=http://localhost:8000 uv run streamlit run app/app.py
"""

import os

import altair as alt
import pandas as pd
import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT_S = 10

CROPS_FR = {
    "Cassava": "Manioc",
    "Maize": "Maïs",
    "Plantains and others": "Banane plantain",
    "Potatoes": "Pomme de terre",
    "Rice, paddy": "Riz (paddy)",
    "Sorghum": "Sorgho",
    "Soybeans": "Soja",
    "Sweet potatoes": "Patate douce",
    "Wheat": "Blé",
    "Yams": "Igname",
}
FIELDS_FR = {"avg_temp": "température", "rainfall_mm": "pluie", "pesticides_t": "pesticides"}


def call(method: str, path: str, payload: dict | None = None):
    """Appelle l'API ; en cas d'échec, affiche un message compréhensible et arrête la page."""
    try:
        r = requests.request(method, f"{API_URL}{path}", json=payload, timeout=TIMEOUT_S)
    except requests.RequestException:
        st.error(f"L'API ne répond pas ({API_URL}). Est-elle lancée ?")
        st.stop()
    if r.status_code != 200:
        st.error(f"L'API a refusé la demande ({r.status_code}) : {r.json().get('detail', r.text)}")
        st.stop()
    return r.json()


def warn_domain(out_of_range: list[str]) -> None:
    if out_of_range:
        names = ", ".join(FIELDS_FR.get(f, f) for f in out_of_range)
        st.warning(
            f"Conditions hors de ce que le modèle a vu ({names}) : résultat à prendre avec précaution."
        )


st.set_page_config(page_title="Agritech Answers — cultures", page_icon="🌾", layout="centered")
st.title("🌾 Rendement et choix de culture")
st.caption(
    "Les conditions décrivent un **pays-type** (moyennes nationales annuelles), pas une parcelle. "
    "Le modèle reflète les rendements observés de 1990 à 2013."
)

mode = st.radio("Que voulez-vous faire ?", ["Prédiction", "Recommandation"], horizontal=True)

with st.form("conditions"):
    crop = None
    if mode == "Prédiction":
        crops = call("GET", "/crops")
        crop = st.selectbox("Culture", crops, format_func=lambda c: CROPS_FR.get(c, c))
    avg_temp = st.slider("Température moyenne annuelle (°C)", -5.0, 32.0, 20.0, 0.5)
    rainfall_mm = st.slider("Pluie annuelle (mm)", 0, 3500, 1000, 50)
    pesticides_t = st.number_input(
        "Pesticides utilisés dans le pays (tonnes par an)", min_value=0.0, max_value=2_000_000.0, value=5000.0
    )
    submitted = st.form_submit_button("Interroger le modèle")

if submitted:
    context = {"avg_temp": avg_temp, "rainfall_mm": rainfall_mm, "pesticides_t": pesticides_t}
    if mode == "Prédiction":
        res = call("POST", "/predict", {**context, "crop": crop})
        warn_domain(res["out_of_range"])
        st.metric(f"Rendement estimé — {CROPS_FR.get(crop, crop)}", f"{res['yield_t_ha']:.1f} t/ha")
        st.write(f"Soit **{res['relative_yield']:.2f} fois** le rendement habituel de cette culture.")
        if not res["crop_supported"]:
            st.info("Aucun pays aux conditions proches ne cultive cette culture dans les données.")
    else:
        res = call("POST", "/recommend", context)
        warn_domain(res["out_of_range"])
        table = pd.DataFrame(res["ranking"])
        table["Culture"] = table["crop"].map(lambda c: CROPS_FR.get(c, c))
        table["Appuyée par des données proches"] = table["crop_supported"].map({True: "oui", False: "non"})
        st.subheader("Classement par rendement relatif")
        # Barres dans l'ordre du classement (st.bar_chart trie par ordre alphabétique) ; gris = non appuyée
        chart = (
            alt.Chart(table)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X("relative_yield:Q", title="rendement relatif (1 = rendement habituel de la culture)"),
                y=alt.Y("Culture:N", sort=alt.SortField("rank"), title=None),
                color=alt.condition("datum.crop_supported", alt.value("#2a78d6"), alt.value("#c3c2b7")),
                tooltip=[
                    "Culture",
                    alt.Tooltip("relative_yield:Q", format=".2f"),
                    alt.Tooltip("yield_t_ha:Q", format=".1f"),
                ],
            )
        )
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(
            table[
                ["rank", "Culture", "relative_yield", "yield_t_ha", "Appuyée par des données proches"]
            ].rename(
                columns={
                    "rank": "Rang",
                    "relative_yield": "Rendement relatif",
                    "yield_t_ha": "Rendement (t/ha)",
                }
            ),
            hide_index=True,
            column_config={
                "Rendement relatif": st.column_config.NumberColumn(format="%.2f"),
                "Rendement (t/ha)": st.column_config.NumberColumn(format="%.1f"),
            },
        )
        st.caption(res["note"] + " Les tonnes par hectare ne se comparent pas d'une culture à l'autre.")
