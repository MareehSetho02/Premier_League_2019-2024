from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Premier League — Avantage à domicile", page_icon="⚽", layout="wide")

# Les mêmes couleurs identifient les lieux dans les deux graphiques.
COULEURS = {"Domicile": "#56B4E9", "Extérieur": "#E69F00"}


@st.cache_data
def load_data():
    # Copie locale des cinq saisons de football-data.co.uk utilisées dans TP6.py.
    chemin = Path(__file__).resolve().parents[1] / "data" / "premier_league.csv"
    return pd.read_csv(chemin, parse_dates=["Date"])


def calculer_taux(donnees, equipes):
    # Formules de TP6.py : victoires / matchs joués au lieu concerné.
    matchs_dom = donnees[donnees["HomeTeam"].isin(equipes)] if equipes else donnees
    matchs_ext = donnees[donnees["AwayTeam"].isin(equipes)] if equipes else donnees
    taux_dom = (matchs_dom["FTR"] == "H").mean() * 100 if len(matchs_dom) else None
    taux_ext = (matchs_ext["FTR"] == "A").mean() * 100 if len(matchs_ext) else None
    return taux_dom, taux_ext


def message_ecart(taux_dom, taux_ext):
    if taux_dom is None or taux_ext is None:
        return "Les matchs disponibles ne permettent pas de comparer les deux lieux."
    ecart = taux_dom - taux_ext
    if abs(ecart) < 1e-10:
        return "Sur la sélection, les taux de victoire à domicile et à l'extérieur sont identiques."
    if ecart > 0:
        return f"Sur la sélection, le taux de victoire à domicile dépasse de {ecart:.1f} points le taux de victoire à l'extérieur."
    return f"Sur la sélection, le taux de victoire à l'extérieur dépasse de {abs(ecart):.1f} points le taux de victoire à domicile."


def presenter_graphique(fig):
    fig.update_layout(
        legend_title_text="", plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=45, b=10),
    )
    st.plotly_chart(fig, width="stretch")


df = load_data()
st.title("🏟️ Avantage à domicile")
st.subheader("Jouer à domicile est-il associé à un taux de victoire plus élevé ?")

st.sidebar.header("Filtres d' avantage à domicile")
saisons_disponibles = sorted(df["Saison"].unique())
equipes_disponibles = sorted(set(df["HomeTeam"]) | set(df["AwayTeam"]))
saisons = st.sidebar.multiselect("Saison", saisons_disponibles, help="Aucune sélection = toutes les saisons.")
equipes = st.sidebar.multiselect("Équipe", equipes_disponibles, help="Aucune sélection = toutes les équipes.")
texte_saisons = "Toutes les saisons" if not saisons else saisons[0] if len(saisons) == 1 else f"{len(saisons)} saisons sélectionnées"
texte_equipes = "Toutes les équipes" if not equipes else equipes[0] if len(equipes) == 1 else f"{len(equipes)} équipes sélectionnées"
st.caption(f"{texte_saisons} · {texte_equipes}")

df_saisons = df[df["Saison"].isin(saisons)].copy() if saisons else df.copy()
df_filtre = df_saisons.copy()
if equipes:
    df_filtre = df_filtre[df_filtre["HomeTeam"].isin(equipes) | df_filtre["AwayTeam"].isin(equipes)]
if df_filtre.empty:
    st.info("Aucun match ne correspond aux équipes et saisons sélectionnées.")
    st.stop()

equipes_presentes = set(df_filtre["HomeTeam"]) | set(df_filtre["AwayTeam"])
absentes = sorted(set(equipes) - equipes_presentes)
if absentes:
    st.caption("Sans match sur cette période : " + ", ".join(absentes))
st.sidebar.caption(f"{len(df_filtre)} rencontres dans la sélection")
st.sidebar.download_button(
    "Télécharger les données filtrées", df_filtre.to_csv(index=False).encode("utf-8-sig"),
    file_name="premier_league_domicile.csv", mime="text/csv",
)

victoires_dom, victoires_ext = calculer_taux(df_filtre, equipes)
ecart_dom_ext = victoires_dom - victoires_ext if victoires_dom is not None and victoires_ext is not None else None

# La référence ne subit jamais le filtre équipe.
reference = df_saisons if equipes else df
ref_dom, ref_ext = calculer_taux(reference, [])
if equipes:
    clubs_reference = set(reference["HomeTeam"]) | set(reference["AwayTeam"])
    afficher_deltas = not clubs_reference.issubset(set(equipes))
    libelle_reference = "vs championnat sur les saisons sélectionnées" if saisons else "vs championnat sur toutes les saisons"
else:
    afficher_deltas = bool(saisons) and set(saisons) != set(saisons_disponibles)
    libelle_reference = "vs moyenne de toutes les saisons"


def delta_victoires(taux, taux_reference):
    if not afficher_deltas or taux is None or taux_reference is None:
        return None
    ecart = round(taux - taux_reference, 1)
    if ecart == 0:
        return None
    return f"{ecart:+.1f} pts {libelle_reference}"


col1, col2, col3 = st.columns(3)
col1.metric("Victoires à domicile", f"{victoires_dom:.1f} %" if victoires_dom is not None else "—", delta=delta_victoires(victoires_dom, ref_dom))
col2.metric("Victoires à l'extérieur", f"{victoires_ext:.1f} %" if victoires_ext is not None else "—", delta=delta_victoires(victoires_ext, ref_ext))
col3.metric("Écart domicile / extérieur", f"{ecart_dom_ext:+.1f} pts" if ecart_dom_ext is not None else "—")
st.caption("Les taux portent sur les matchs joués par les équipes sélectionnées à chaque lieu. Les matchs nuls restent dans le dénominateur. Une association ne démontre pas une causalité.")

tab2, tab3 = st.tabs(["📈 Évolution par saison", "🏠 Domicile vs extérieur"])

with tab2:
    st.header("Jouer à domicile c'est déjà gagner à moitié")
    lignes = []
    for saison in sorted(saisons or saisons_disponibles):
        matchs_saison = df_filtre[df_filtre["Saison"] == saison]
        taux_dom, taux_ext = calculer_taux(matchs_saison, equipes)
        lignes.append({"Saison": saison, "Domicile": taux_dom, "Extérieur": taux_ext})
    evolution = pd.DataFrame(lignes)
    df_graph = evolution.melt(id_vars="Saison", var_name="Lieu", value_name="Taux de victoire")
    fig = px.line(
        df_graph, x="Saison", y="Taux de victoire", color="Lieu", markers=True,
        color_discrete_map=COULEURS, labels={"Taux de victoire": "Taux de victoire (%)"},
        category_orders={"Saison": evolution["Saison"].tolist()},
    )
    fig.update_traces(connectgaps=False)
    # Une bande de largeur non nulle sur l'axe catégoriel, uniquement si la saison est visible.
    if "2020-21" in evolution["Saison"].values:
        position = evolution["Saison"].tolist().index("2020-21")
        fig.add_vrect(x0=position - 0.4, x1=position + 0.4, fillcolor="gray", opacity=0.12, layer="below", line_width=0)
        fig.add_annotation(x="2020-21", y=1, yref="paper", text="2020-21 · huis clos (COVID-19)", showarrow=False, yanchor="bottom", font=dict(size=11, color="gray"))
    fig.update_yaxes(range=[0, 100])
    fig.update_layout(hovermode="x unified")
    presenter_graphique(fig)

with tab3:
    # Même calcul par équipe que dans TP6.py, restreint aux équipes affichées.
    clubs = sorted(equipes_presentes & set(equipes)) if equipes else sorted(equipes_presentes)
    lignes_equipes = []
    for equipe in clubs:
        taux_dom, taux_ext = calculer_taux(df_saisons, [equipe])
        lignes_equipes.append({"Équipe": equipe, "Domicile": taux_dom, "Extérieur": taux_ext})
    df_equipes_taux = pd.DataFrame(lignes_equipes).sort_values("Domicile", ascending=False)
    if len(df_equipes_taux) == 1:
        st.header(f"{clubs[0]} : domicile vs extérieur")
        st.info(message_ecart(victoires_dom, victoires_ext))
    else:
        meilleur_taux = df_equipes_taux["Domicile"].max()
        leaders = df_equipes_taux.loc[df_equipes_taux["Domicile"] == meilleur_taux, "Équipe"].tolist()
        if pd.notna(meilleur_taux):
            st.header(f"{', '.join(leaders)} : meilleur taux de victoire à domicile sur la sélection ({meilleur_taux:.1f} %)")
        else:
            st.header("Domicile vs extérieur sur la sélection")
    df_equipes_graph = df_equipes_taux.melt(id_vars="Équipe", var_name="Lieu", value_name="Taux de victoire")
    fig = px.bar(
        df_equipes_graph, y="Équipe", x="Taux de victoire", color="Lieu", barmode="group",
        orientation="h", color_discrete_map=COULEURS, text_auto=".1f",
        category_orders={"Équipe": df_equipes_taux["Équipe"].tolist()},
        labels={"Taux de victoire": "Taux de victoire (%)", "Équipe": ""},
    )
    fig.update_xaxes(range=[0, 100])
    fig.update_layout(height=max(320, len(clubs) * 45))
    presenter_graphique(fig)
