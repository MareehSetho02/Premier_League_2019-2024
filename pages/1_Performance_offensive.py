from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Charger la copie locale des cinq CSV utilisés dans le notebook AED.
@st.cache_data
def charger_donnees():
    chemin = Path(__file__).resolve().parents[1] / "data" / "premier_league.csv"
    return pd.read_csv(chemin, parse_dates=["Date"])


st.title("⚽ Performance offensive")
st.subheader("Comment les tirs et leur précision sont-ils associés aux buts marqués ?")

df = charger_donnees()

# Les noms ci-dessous sont ceux du notebook et des fichiers sources.
colonnes = ["Date", "Saison", "HomeTeam", "AwayTeam", "FTHG", "FTAG",
            "HS", "AS", "HST", "AST"]
if not set(colonnes).issubset(df.columns):
    st.error("Le fichier de données ne contient pas toutes les colonnes attendues.")
    st.stop()

st.sidebar.header("Filtres de performance offensive")
saisons = st.sidebar.multiselect("Saison", sorted(df["Saison"].unique()), help="Aucune sélection = toutes les saisons.")
equipes = sorted(set(df["HomeTeam"]) | set(df["AwayTeam"]))
equipes_selectionnees = st.sidebar.multiselect("Équipe", equipes, help="Aucune sélection = toutes les équipes.")

texte_saisons = "Toutes les saisons" if not saisons else saisons[0] if len(saisons) == 1 else f"{len(saisons)} saisons sélectionnées"
texte_equipes = "Toutes les équipes" if not equipes_selectionnees else equipes_selectionnees[0] if len(equipes_selectionnees) == 1 else f"{len(equipes_selectionnees)} équipes sélectionnées"
st.caption(f"{texte_saisons} · {texte_equipes}")

matchs = df.copy()
if saisons:
    matchs = matchs[matchs["Saison"].isin(saisons)].copy()

# Garder une ligne par rencontre pour la comparaison des clubs, sans doublons.
matchs_saisons = matchs.copy()

# Créer des colonnes de calcul explicites : elles ne sont pas dans le CSV.
# Sans équipe choisie, on additionne les statistiques des deux adversaires.
if not equipes_selectionnees:
    matchs["Buts"] = matchs["FTHG"] + matchs["FTAG"]
    matchs["Tirs"] = matchs["HS"] + matchs["AS"]
    matchs["Tirs cadrés"] = matchs["HST"] + matchs["AST"]
    st.caption("Un point représente un match, avec les buts et les tirs des deux équipes additionnés.")
else:
    # Une ligne par équipe sélectionnée et par match : chaque équipe garde ses statistiques.
    domicile = matchs[matchs["HomeTeam"].isin(equipes_selectionnees)].copy()
    domicile["Équipe"] = domicile["HomeTeam"]
    domicile["Buts"] = domicile["FTHG"]
    domicile["Tirs"] = domicile["HS"]
    domicile["Tirs cadrés"] = domicile["HST"]
    exterieur = matchs[matchs["AwayTeam"].isin(equipes_selectionnees)].copy()
    exterieur["Équipe"] = exterieur["AwayTeam"]
    exterieur["Buts"] = exterieur["FTAG"]
    exterieur["Tirs"] = exterieur["AS"]
    exterieur["Tirs cadrés"] = exterieur["AST"]
    matchs = pd.concat([domicile, exterieur], ignore_index=True)
    st.caption("Un point représente une équipe dans un match, avec uniquement ses buts et ses tirs. Une rencontre entre deux équipes sélectionnées produit deux points. Les moyennes sont pondérées par les matchs disputés.")

if matchs.empty:
    st.info("Aucun match pour les équipes et saisons sélectionnées.")
    st.stop()

# Calculer les trois KPIs à partir de la sélection.
moyenne_buts = matchs["Buts"].mean()
moyenne_tirs_cadres = matchs["Tirs cadrés"].mean()
total_tirs = matchs["Tirs"].sum()
precision = 100 * matchs["Tirs cadrés"].sum() / total_tirs if total_tirs > 0 else None

# Partir du dataset complet pour ne jamais filtrer la référence par équipe.
reference = df
if equipes_selectionnees:
    if saisons:
        reference = df[df["Saison"].isin(saisons)]
    # Chaque rencontre représente deux équipes : moyenne par équipe et par match.
    nombre_observations = 2 * len(reference)
    libelle_reference = "vs moyenne des équipes"
    contexte_reference = "Référence : moyenne par équipe et par match, toutes les équipes de PL, "
    contexte_reference += "saisons : " + ", ".join(saisons) + "." if saisons else "toutes les saisons disponibles."
else:
    # Comme les KPIs additionnent les deux adversaires, garder cette même unité.
    nombre_observations = len(reference)
    libelle_reference = "vs moyenne de toutes les saisons"
    contexte_reference = (
        "Référence : toutes les saisons disponibles, statistiques des deux équipes "
        "additionnées par match."
    )

reference_buts = (reference["FTHG"].sum() + reference["FTAG"].sum()) / nombre_observations
reference_cadres = (reference["HST"].sum() + reference["AST"].sum()) / nombre_observations
reference_tirs = reference["HS"].sum() + reference["AS"].sum()
reference_precision = (
    100 * (reference["HST"].sum() + reference["AST"].sum()) / reference_tirs
    if reference_tirs > 0 else None
)

# Aucun delta lorsque la sélection est identique à la référence globale.
if equipes_selectionnees:
    equipes_reference = set(reference["HomeTeam"]) | set(reference["AwayTeam"])
    afficher_deltas = not equipes_reference.issubset(set(equipes_selectionnees))
else:
    afficher_deltas = bool(saisons) and set(saisons) != set(df["Saison"])


def formater_delta(valeur, moyenne_reference, decimales, unite=""):
    if not afficher_deltas or valeur is None or moyenne_reference is None:
        return None
    ecart = round(valeur - moyenne_reference, decimales)
    # Masquer aussi les écarts trop petits pour être visibles à cette précision.
    if ecart == 0:
        return None
    return f"{ecart:+.{decimales}f}{unite} {libelle_reference}"


delta_buts = formater_delta(moyenne_buts, reference_buts, 2)
delta_cadres = formater_delta(moyenne_tirs_cadres, reference_cadres, 2)
delta_precision = formater_delta(precision, reference_precision, 1, " pts")

# Limiter le style aux trois indicateurs, sans toucher au KPI des extrêmes.
st.markdown(
    """
    <style>
    .st-key-kpis_offensifs [data-testid="stMetricLabel"],
    .st-key-kpis_offensifs [data-testid="stMetricLabel"] p {
        color: #DCE5EF;
    }
    .st-key-kpis_offensifs [data-testid="stMetricValue"] {
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
with st.container(key="kpis_offensifs"):
    col1, col2, col3 = st.columns(3, gap="small")
    col1.metric("Buts par match", f"{moyenne_buts:.2f}", delta=delta_buts)
    col2.metric("Tirs cadrés par match", f"{moyenne_tirs_cadres:.2f}", delta=delta_cadres)
    col3.metric("Tirs cadrés parmi les tirs", f"{precision:.1f} %" if precision is not None else "Non calculable", delta=delta_precision)
unite_observation = "observations équipe-match" if equipes_selectionnees else "matchs"
st.caption(f"{len(matchs)} {unite_observation} sélectionnés.")

onglet1, onglet2 = st.tabs(["🎯 Tirs cadrés & buts", "🏆 Comparaison des équipes"])

with onglet1:
    # Un point par match, ou par équipe-match lorsqu'on sélectionne des équipes.
    st.subheader("Plus de tirs cadrés sont associés à davantage de buts marqués")
    scatter = px.scatter(
        matchs, x="Tirs cadrés", y="Buts", opacity=0.4,
        hover_data=["Date", "Saison", "HomeTeam", "AwayTeam"] + (["Équipe"] if equipes_selectionnees else []),
        labels={"Buts": "Buts marqués", "HomeTeam": "Domicile", "AwayTeam": "Extérieur"},
    )
    scatter.update_xaxes(rangemode="tozero")
    scatter.update_yaxes(rangemode="tozero")
    st.plotly_chart(scatter, width="stretch")

with onglet2:
    # Pour comparer les clubs, réunir leurs statistiques à domicile et à l'extérieur.
    domicile = matchs_saisons[["HomeTeam", "HST"]].rename(
        columns={"HomeTeam": "Équipe", "HST": "Tirs cadrés"})
    exterieur = matchs_saisons[["AwayTeam", "AST"]].rename(
        columns={"AwayTeam": "Équipe", "AST": "Tirs cadrés"})
    par_equipe = pd.concat([domicile, exterieur], ignore_index=True)
    if equipes_selectionnees:
        par_equipe = par_equipe[par_equipe["Équipe"].isin(equipes_selectionnees)]

    comparaison = par_equipe.groupby("Équipe", as_index=False)["Tirs cadrés"].mean()
    comparaison = comparaison.sort_values("Tirs cadrés")

    # Le tableau est trié par ordre croissant : la dernière ligne est la barre du haut.
    meilleure_equipe = comparaison.iloc[-1]
    nom_equipe = meilleure_equipe["Équipe"]
    if not equipes_selectionnees:
        titre_comparaison = f"{nom_equipe} affiche le plus de tirs cadrés par match"
    elif len(equipes_selectionnees) == 1:
        valeur_affichee = f"{meilleure_equipe['Tirs cadrés']:.1f}".replace(".", ",")
        titre_comparaison = f"{nom_equipe} : {valeur_affichee} tirs cadrés par match sur la sélection"
    else:
        titre_comparaison = f"{nom_equipe} affiche le plus de tirs cadrés parmi les équipes sélectionnées"
    st.subheader(titre_comparaison)
    # Utiliser les mêmes moyennes filtrées et le même ordre que les barres.
    if len(comparaison) < 2:
        st.caption("Sélectionnez au moins 2 équipes pour afficher le rapport entre les extrêmes.")
    else:
        minimum = comparaison.iloc[0]
        maximum = comparaison.iloc[-1]
        equipe_min = minimum["Équipe"]
        equipe_max = maximum["Équipe"]
        valeur_min = minimum["Tirs cadrés"]
        valeur_max = maximum["Tirs cadrés"]
        if valeur_min > 0:
            ratio_extremes = valeur_max / valeur_min
            st.metric("Rapport entre les extrêmes", f"×{ratio_extremes:.2f}".replace(".", ","))
            st.caption(f"{equipe_max} vs {equipe_min}")
        else:
            st.info("Rapport non calculable : la moyenne minimale de tirs cadrés est nulle.")

    barres = px.bar(
        comparaison, x="Tirs cadrés", y="Équipe", orientation="h", text_auto=".2f",
        labels={"Tirs cadrés": "Tirs cadrés par match"},
        color="Tirs cadrés", color_continuous_scale=["#C6DBEF", "#08519C"],
    )
    barres.update_layout(height=max(300, len(comparaison) * 25), yaxis={"categoryorder": "total ascending"})
    barres.update_layout(coloraxis_showscale=False)
    # Moyenne des valeurs des barres : chaque équipe affichée a le même poids.
    if len(comparaison) >= 2:
        moyenne_equipes = comparaison["Tirs cadrés"].mean()
        barres.add_vline(
            x=moyenne_equipes, line_dash="dot", line_color="#777777", line_width=1,
            annotation_text=f"Moyenne des équipes : {moyenne_equipes:.2f}",
            annotation_position="top", annotation_font_color="#777777",
            annotation_font_size=11,
        )
    barres.update_xaxes(rangemode="tozero")
    st.plotly_chart(barres, width="stretch")
