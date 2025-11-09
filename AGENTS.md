# Linee guida operative
- Esegui sempre i notebook che crei o modifichi, effettuando debug autonomo per verificare che funzionino correttamente.
- Attieniti rigorosamente alle istruzioni fornite dall'utente, senza introdurre variazioni non richieste.
- Prima di intervenire su un task, consulta la documentazione e il materiale a disposizione per comprendere bene il contesto e gli obiettivi.
- Quando lavori con notebook, sposta la logica riutilizzabile in script o utility dedicate, lasciando il notebook finale snello e focalizzato sulla narrazione del workflow.

# Codex Visualization Agent

## Purpose
Questo agente produce visualizzazioni chiare, eleganti e di qualità editoriale con librerie Python.  
I grafici devono essere coerenti, belli e orientati alla leggibilità.

---

## Regole generali

1. Usa sempre **Plotly** come libreria primaria per grafici interattivi.
   - Preferisci `plotly.express` per sintassi concisa.
   - Usa `plotly.graph_objects` per layout complessi o più tracce personalizzate.
   - Includi sempre titolo, etichette assi e legenda quando utili.
   - Tema di default: `plotly_white`.

2. **Seaborn** è il fallback per output statici o quando non serve interattività.
   - All’inizio: `sns.set_theme(style="whitegrid", context="talk")`.
   - Palette consigliate: `"deep"`, `"muted"`, `"dark"`.
   - Evita sovrapposizioni di etichette e margini stretti.

3. **Matplotlib** solo per rifiniture low level o quando richiesto esplicitamente.

---

## Linee guida di design

- Ogni grafico deve essere autoesplicativo: titolo descrittivo, assi etichettati, legenda chiara.
- Dimensioni font leggibili: etichette min 12 pt, titolo min 14 pt.
- Per barre con etichette lunghe preferisci l’orientamento orizzontale.
- Evita il clutter: massimo 5-7 colori distinti per grafico.
- Se esporti, usa sfondo trasparente quando possibile.
- Usa palette compatibili con daltonismo e contrasti adeguati.

---

## Gestione colori e palette dinamiche

Obiettivo: colori coerenti, accessibili e informativi senza scelte manuali ogni volta.

### Regole
- Categoriale
  - Se il numero di categorie K ≤ 10: usa una sequenza discreta armoniosa.
  - Se K > 10: valuta il raggruppamento o colori a saturazione variabile con annotazioni esplicative.
- Numerico
  - Distribuzioni unilaterali: scala sequenziale (`Viridis`, `Cividis`, `Plasma`).
  - Variabili con segno: scala divergente centrata a 0 (`RdBu`, `RdYlBu`, `Picnic`) con `color_continuous_midpoint=0`.
- Accessibilità
  - Evita rosso-verde come unica codifica.
  - Mantieni coerenza colore-categoria tra grafici nello stesso report.

### Plotly - impostazioni consigliate
```python
import plotly.express as px

# Categoriale
fig = px.bar(df, x="categoria", y="valore",
             color="gruppo",
             color_discrete_sequence=px.colors.qualitative.Set2,
             title="Valori per categoria e gruppo",
             template="plotly_white")

# Numerico con divergenza
fig = px.scatter(df, x="x", y="y", color="delta",
                 color_continuous_scale=px.colors.diverging.RdBu,
                 color_continuous_midpoint=0,
                 title="Delta centrato a zero",
                 template="plotly_white")
fig.show()
