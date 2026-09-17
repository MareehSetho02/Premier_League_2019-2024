# Dashboard Premier League Football

Lien de l'application : https://premierleaguefootball.streamlit.app/ 

## 1. Message clé

Sur les saisons 2019-20 à 2023-24, le dashboard explore les associations entre production offensive et buts, les écarts de réussite selon le lieu du match et les profils de fautes et de cartons, sans établir de causalité.

- **Performance offensive :** « Comment les tirs et leur précision sont-ils associés aux buts marqués ? »
- **Avantage à domicile :** « Jouer à domicile est-il associé à un taux de victoire plus élevé ? »
- **Discipline & intensité :** « Les équipes qui commettent davantage de fautes reçoivent-elles davantage de cartons ? »

## 2. Audience cible

**Les analystes sportifs des staffs techniques de Premier League.** Le dashboard leur permet de situer une équipe par rapport aux autres, de comparer plusieurs clubs et saisons et de repérer rapidement des écarts et tendances à approfondir.


## 3. KPIs retenus et justification

| Page | KPI | Rôle | Vanity / Actionable | Justification |
|---|---|---|---|---|
| Offensive | Buts par match | Mesure la production offensive moyenne | Vanity/descriptif seul ; actionable lorsqu’il est contextualisé | La valeur brute décrit le résultat offensif. Lorsqu’une sélection est comparée à une référence, le delta permet d’identifier un écart de rendement à approfondir. |
| Offensive | Tirs cadrés par match | Mesure le volume moyen de tirs cadrés | Vanity/descriptif seul ; actionable lorsqu’il est contextualisé | La valeur brute décrit le volume offensif. Le delta permet de repérer une production de tirs cadrés supérieure ou inférieure à la référence et d’orienter l’analyse. |
| Offensive | Tirs cadrés parmi les tirs | Mesure la précision des tirs : tirs cadrés / tirs × 100 | Vanity/descriptif seul ; actionable lorsqu’il est contextualisé | La valeur brute décrit la précision. Sa comparaison à la référence permet d’identifier si la sélection cadre proportionnellement plus ou moins de tirs et d’approfondir cet écart. |
| Offensive | Rapport entre les extrêmes | Compare le maximum et le minimum des moyennes de tirs cadrés des équipes sélectionnées | Actionable / comparatif | Compare directement les équipes extrêmes et quantifie l’écart de tirs cadrés par match, ce qui permet d’identifier immédiatement un différentiel de performance à investiguer. |
| Domicile | Victoires à domicile | Mesure la part des matchs à domicile remportés | Vanity/descriptif seul ; actionable lorsqu’il est contextualisé | La valeur brute décrit la réussite à domicile. Lorsqu’elle est comparée à une référence, le delta permet d’identifier un taux de victoire supérieur ou inférieur à la référence et d’orienter l’analyse. |
| Domicile | Victoires à l’extérieur | Mesure la part des matchs à l’extérieur remportés | Vanity/descriptif seul ; actionable lorsqu’il est contextualisé | La valeur brute décrit la réussite à l’extérieur. Lorsqu’elle est comparée à une référence, le delta permet d’identifier un taux de victoire supérieur ou inférieur à la référence et d’orienter l’analyse. |
| Domicile | Écart domicile / extérieur | Mesure la différence entre le taux de victoire à domicile et le taux de victoire à l’extérieur, en points de pourcentage | Actionable / comparatif | Compare directement les deux contextes de jeu et quantifie l’écart de réussite entre domicile et extérieur, ce qui permet d’identifier immédiatement un différentiel à approfondir. |
| Discipline | Fautes moyennes par match | Mesure la fréquence moyenne des fautes par équipe | Vanity/descriptif seul ; actionable lorsqu’il est contextualisé | La valeur brute décrit le niveau de fautes. Comparée à une référence, elle permet d’identifier un profil plus ou moins fautif que le championnat et d’orienter l’analyse vers les facteurs susceptibles d’expliquer cet écart. |
| Discipline | Cartons jaunes moyens par match | Mesure la fréquence moyenne des avertissements | Vanity/descriptif seul ; actionable lorsqu’il est contextualisé | La valeur brute décrit le niveau de sanctions. Le delta par rapport à la référence permet de repérer une accumulation de cartons supérieure ou inférieure à la norme et d’identifier un risque disciplinaire à approfondir. |
| Discipline | Ratio cartons jaunes / fautes | Rapporte le total des cartons jaunes au total des fautes, en % | Comparatif / actionable | Met en relation le volume de cartons et celui des fautes afin de distinguer différents profils disciplinaires. Il ne représente pas la probabilité qu’une faute individuelle soit sanctionnée d’un carton. |

Les indicateurs sont contextualisés par une référence lorsque la sélection permet une comparaison pertinente. Les deltas sont masqués lorsqu’ils n’apportent pas d’information, notamment lorsque la sélection correspond elle-même à la référence. La page Avantage à domicile repose directement sur la comparaison entre les taux de victoire à domicile et à l’extérieur. Ces comparaisons permettent d’identifier des écarts à approfondir et d’orienter l’analyse, sans prescrire automatiquement une décision tactique.

## 4. Structure 

Les trois pages suivent une organisation commune : question analytique → filtres → KPIs → insight → visualisations détaillées. Les filtres permettent d’adapter le périmètre d’analyse, les KPIs fournissent une lecture synthétique et les onglets donnent accès au détail et aux comparaisons.

