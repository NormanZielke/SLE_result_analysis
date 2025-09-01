# Regional Energy System Post-Processing

Dieses Projekt dient der **Auswertung und Visualisierung** von Energiesystem-Modellergebnissen (z. B. aus [oemof](https://oemof.org/) oder [eTraGo](https://github.com/openego/eTraGo)).  
Es werden **regionale** und **aggregierte** Ergebnisse verarbeitet, u. a.:

- Optimierte Kapazitäten (inkl. Potenzialvergleich)  
- Stromerzeugung und -importe  
- Wärmebereitstellung (hoch-, niedrig-temperatur, zentral/dezentral)  
- Nicht verwendete Technologien  

Die Ergebnisse werden automatisch als **CSV-Dateien** und **Plots (Balken & Torten)** gespeichert.

---

## 📂 Projektstruktur

```
.
├── class_region.py              # Klasse für eine einzelne Region
├── class_aggregated_region.py   # Klasse für Aggregationen (ALL_REGIONS / Summen)
├── calc_results.py              # Analyse- und Plot-Wrapper
├── plots.py                     # Plot-Funktionen mit Matplotlib
├── helpers.py                   # Hilfsfunktionen (CSV-Reader, Label-Mapping)
├── main.py                      # Einstiegspunkt: orchestriert die Auswertung
├── de.yml                       # Label-Mapping für Technologien/Komponenten
└── input_data/                  # Modell-Ergebnisse (scalars.csv, potentials)
```

Die **Ergebnisse** werden standardmäßig unter dem in `args["results_dir"]` definierten Ordner abgelegt, z. B.:

```
results/
 ├── 01_ALL_REGIONS/
 ├── 01_ALL_REGIONS_aggregated/
 ├── Single_Regions/
 └── Single_Region_aggregated/
```

---

## ⚙️ Voraussetzungen

- Python **3.9+**
- Installierte Pakete (siehe `requirements.txt`):
  - `pandas`
  - `matplotlib`
  - `pyyaml`

Installation im virtuellen Environment (empfohlen):

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

---

## 🚀 Anwendung

1. **Input-Daten vorbereiten**
   - Ergebnisse aus der Energiesystem-Optimierung als `scalars.csv` bereitstellen.
   - Struktur:
     - `input_data/01_ALL_REGIONS/.../scalars.csv`
     - `input_data/Single_Regions/{region_id}/.../scalars.csv`
   - Potenzial-Dateien (z. B. `electricity-pv_rooftop.csv`, `electricity-wind.csv`) im Verzeichnis `input_data/01_ALL_REGIONS/.../elements/` ablegen.

2. **Konfiguration prüfen**  
   In `main.py`:
   ```python
   args = {
       "region_id_dict": {
           "r120640428428": "Rüdersdorf",
           "r120640472472": "Strausberg",
           "r120670124124": "Erkner",
           "r120670201201": "Grünheide",
       },
       "renewables_pot_csv_directory": "input_data/01_ALL_REGIONS/2045_scenario/preprocessed/data/elements",
       "all_capacities": True,
       "results_dir": "results",  # Basisordner für Outputs
   }
   ```

3. **Skript starten**
   ```bash
   python main.py
   ```

4. **Ergebnisse ansehen**
   - CSVs und Diagramme werden im definierten `results_dir` abgelegt.
   - Beispiel: `results/Single_Regions/r120640472472/r120640472472_capacities_opt.svg`

---
