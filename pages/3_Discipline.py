from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Discipline & intensité", page_icon="🟨", layout="wide")


@st.cache_data
def load_data():
    chemin = Path(__file__).resolve().parents[1] / "data" / "premier_league.csv"
    return pd.read_csv(chemin, parse_dates=["Date"])


def team_discipline(data):
    """Une ligne par participation d'équipe, comme dans le fichier reçu."""
    home = data.rename(columns={"HomeTeam": "Team", "HF": "Fouls", "HY": "Yellow", "HR": "Red"})[
        ["Team", "Fouls", "Yellow", "Red", "Saison"]]
    away = data.rename(columns={"AwayTeam": "Team", "AF": "Fouls", "AY": "Yellow", "AR": "Red"})[
        ["Team", "Fouls", "Yellow", "Red", "Saison"]]
    return pd.concat([home, away], ignore_index=True)


def indicateurs(stats):
    total_fautes = stats["Fouls"].sum()
    ratio = stats["Yellow"].sum() / total_fautes if total_fautes > 0 else None
    return stats["Fouls"].mean(), stats["Yellow"].mean(), ratio


def nombre(valeur, decimales=2):
    return f"{valeur:.{decimales}f}".replace(".", ",")


df = load_data()
st.title("Discipline & intensité")
st.subheader("Les équipes qui commettent davantage de fautes reçoivent-elles davantage de cartons ?")
st.sidebar.header("Filtres de discipline & intensité")
saisons = st.sidebar.multiselect("Saison", sorted(df["Saison"].unique()), help="Aucune sélection = toutes les saisons.")
equipes = st.sidebar.multiselect("Équipe", sorted(set(df["HomeTeam"]) | set(df["AwayTeam"])), help="Aucune sélection = toutes les équipes.")
texte_saisons = "Toutes les saisons" if not saisons else saisons[0] if len(saisons) == 1 else f"{len(saisons)} saisons sélectionnées"
texte_equipes = "Toutes les équipes" if not equipes else equipes[0] if len(equipes) == 1 else f"{len(equipes)} équipes sélectionnées"
st.caption(f"{texte_saisons} · {texte_equipes}")

df_f = df[df["Saison"].isin(saisons)] if saisons else df
stats_saisons = team_discipline(df_f)
stats = stats_saisons[stats_saisons["Team"].isin(equipes)] if equipes else stats_saisons
if stats.empty:
    st.info("Aucune donnée pour les équipes et saisons sélectionnées.")
    st.stop()
absentes = sorted(set(equipes) - set(stats["Team"]))
if absentes:
    st.caption("Sans match sur cette période : " + ", ".join(absentes))

# Même périmètre saison pour comparer des équipes ; sinon référence toutes saisons.
reference = stats_saisons if equipes else team_discipline(df)
libelle_reference = "vs équipes des saisons sélectionnées" if equipes and saisons else "vs équipes de toutes les saisons" if equipes else "vs moyenne de toutes les saisons"
afficher_deltas = len(stats) != len(reference)
kpi_fouls, kpi_yellow, kpi_ratio = indicateurs(stats)
ref_fouls, ref_yellow, ref_ratio = indicateurs(reference)


def delta(valeur, valeur_reference, decimales=2, unite=""):
    if not afficher_deltas or valeur is None or valeur_reference is None:
        return None
    ecart = round(valeur - valeur_reference, decimales)
    if ecart == 0:
        return None
    return f"{ecart:+.{decimales}f}{unite} {libelle_reference}".replace(".", ",")


c1, c2, c3 = st.columns(3)
c1.metric("Fautes moyennes par match", nombre(kpi_fouls), delta=delta(kpi_fouls, ref_fouls), delta_color="off")
c2.metric("Cartons jaunes moyens par match", nombre(kpi_yellow), delta=delta(kpi_yellow, ref_yellow), delta_color="inverse")
c3.metric(
    "Ratio cartons jaunes / fautes", nombre(kpi_ratio * 100, 1) + " %" if kpi_ratio is not None else "Non calculable",
    delta=delta(kpi_ratio * 100 if kpi_ratio is not None else None, ref_ratio * 100 if ref_ratio is not None else None, 1, " pts"),
    delta_color="inverse",
)

if afficher_deltas:
    sens_fautes = "davantage de" if kpi_fouls > ref_fouls else "moins de" if kpi_fouls < ref_fouls else "autant de"
    sens_cartons = "davantage de" if kpi_yellow > ref_yellow else "moins de" if kpi_yellow < ref_yellow else "autant de"
    st.info(f"Sur la sélection : {sens_fautes} fautes et {sens_cartons} cartons jaunes par match que la référence ({libelle_reference.removeprefix('vs ')}).")
else:
    st.info(f"Sur la sélection, une équipe commet en moyenne {nombre(kpi_fouls)} fautes et reçoit {nombre(kpi_yellow)} cartons jaunes par match.")
st.caption(f"{len(stats)} observations équipe-match, domicile et extérieur réunis. Le ratio est descriptif, pas une probabilité de sanction : certains cartons ne correspondent pas à une faute comptabilisée.")

# Moyennes et ratio par équipe du fichier reçu ; aucune limitation aux 12 premières.
agg = stats.groupby("Team").agg(
    Fouls=("Fouls", "mean"), Yellow=("Yellow", "mean"),
    Red=("Red", "mean"), Matches=("Fouls", "count"),
).reset_index()
agg["Ratio"] = agg["Yellow"] / agg["Fouls"].replace(0, float("nan")) * 100

onglet1, onglet2 = st.tabs(["🟨 Fautes & cartons", "🏆 Comparaison des équipes"])

with onglet1:
    if len(agg) == 1:
        ligne = agg.iloc[0]
        st.subheader(f"{ligne['Team']} : {nombre(ligne['Fouls'])} fautes et {nombre(ligne['Yellow'])} cartons jaunes par match")
    elif agg["Fouls"].nunique() > 1 and agg["Yellow"].nunique() > 1:
        correlation = agg["Fouls"].corr(agg["Yellow"])
        sens = "positive" if correlation > 0 else "négative" if correlation < 0 else "nulle"
        st.subheader(f"Association {sens} entre fautes et cartons sur la sélection (r = {nombre(correlation)})")
    else:
        st.subheader("La sélection ne permet pas de calculer une corrélation entre équipes")
    fig = px.scatter(
        agg, x="Fouls", y="Yellow", size="Matches", color="Ratio", hover_name="Team",
        hover_data={"Fouls": ":.2f", "Yellow": ":.2f", "Ratio": ":.1f", "Matches": True},
        labels={"Fouls": "Fautes moyennes / match", "Yellow": "Cartons jaunes moyens / match", "Ratio": "Cartons / fautes (%)", "Matches": "Matchs"},
        color_continuous_scale=["#FFF3B0", "#C08A18"],
    )
    fig.update_traces(marker=dict(line=dict(width=0.5, color="white")))
    fig.update_layout(height=480, margin=dict(l=20, r=20, t=20, b=20))
    fig.update_xaxes(rangemode="tozero")
    fig.update_yaxes(rangemode="tozero")
    st.plotly_chart(fig, width="stretch")

with onglet2:
    classement = agg.sort_values("Fouls", ascending=False)
    if len(classement) == 1:
        st.subheader(f"{classement.iloc[0]['Team']} : fautes et cartons sur la sélection")
    else:
        leaders = classement.loc[classement["Fouls"] == classement["Fouls"].max(), "Team"]
        st.subheader(f"{', '.join(leaders)} : le plus de fautes par match parmi les équipes affichées")
    barres = classement.rename(columns={"Fouls": "Fautes / match", "Yellow": "Cartons jaunes / match"}).melt(
        id_vars="Team", value_vars=["Fautes / match", "Cartons jaunes / match"], var_name="Indicateur", value_name="Moyenne par match")
    fig2 = px.bar(
        barres, y="Team", x="Moyenne par match", color="Indicateur", orientation="h", barmode="group",
        color_discrete_map={"Fautes / match": "#56B4E9", "Cartons jaunes / match": "#E69F00"},
        category_orders={"Team": classement["Team"].tolist()}, labels={"Team": ""},
    )
    fig2.update_layout(height=max(320, len(classement) * 45), legend_title_text="", margin=dict(l=20, r=20, t=20, b=20))
    fig2.update_xaxes(rangemode="tozero")
    st.plotly_chart(fig2, width="stretch")
