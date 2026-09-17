import streamlit as st

# Configurer le titre de l'onglet et utiliser la largeur de la page.
st.set_page_config(
    page_title="Premier League | Analyse de performance",
    page_icon="⚽",
    layout="wide"
)

st.title("Premier League 2019–2024")

st.header("Quels facteurs sont associés à la performance des équipes ?")

st.write(
    """
    Ce dashboard s'appuie sur notre projet d'analyse exploratoire des données
    de Premier League, des saisons 2019–2020 à 2023–2024. Il propose d'explorer
    trois dimensions : la performance offensive, l'avantage de jouer à domicile
    et la discipline.
    """
)

st.divider()

st.subheader("Les 3 axes d'analyse")

# Présenter chaque axe dans une colonne.
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ⚽ Performance offensive")
    st.write("Comprendre la relation entre les tirs cadrés et les buts.")

with col2:
    st.markdown("### 🏟️ Avantage à domicile")
    st.write("Comparer les performances à domicile et à l'extérieur.")

with col3:
    st.markdown("### 🟨 Discipline")
    st.write("Analyser la relation entre les fautes et les cartons.")

st.divider()

