"""
Software Cabina MT/BT Professional v2.0
Flusso Guidato Step-by-Step per Progettazione Cabine
"""

import streamlit as st
import sys
import os

# Import per report generation
try:
    from report.generators.relazione_tecnica_completa import genera_relazione_da_main
    from report.utils.streamlit_integration import interfaccia_report_sidebar
    REPORT_AVAILABLE = True
except ImportError as e:
    REPORT_AVAILABLE = False
    st.warning(f"⚠️ Moduli report non disponibili: {e}")

# Aggiungi la cartella del progetto al path per gli import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import dai nostri moduli
from config.settings import APP_CONFIG, VERSION
from database.products import ProductDatabase
from ui.sidebar import render_sidebar
from ui.progress import render_progress_bar, initialize_session_state
from ui.steps import (
    step_1_distributor_data,
    step_2_load_calculation, 
    step_3_transformer_sizing,
    step_3_5_earth_switch_design,
    step_4_mt_switchgear_design,  # ✅ NOME CORRETTO DELLA FUNZIONE
    step_5_protection_coordination,
    step_6_bt_switchgear_design,
    step_7_final_analysis
)

def main():
    """App principale con flusso guidato"""
    
    # Setup pagina
    st.set_page_config(**APP_CONFIG)
    
    # Inizializzazione
    initialize_session_state()
    
    # Header
    st.title("⚡ Software Cabina MT/BT Professional v2.0")
    st.markdown(f"**Versione {VERSION} - Progettazione Guidata Step-by-Step**")
    
    # Carica database
    try:
        db = ProductDatabase()
    except Exception as e:
        st.error(f"❌ Errore caricamento database: {e}")
        return
    
    # Sidebar per input dati
    render_sidebar()
    
    # Progress bar su tutta la larghezza
    current_step = render_progress_bar()
    
    st.markdown("---")
    
    # ✅ Router per step - CORRETTI I NOMI DELLE FUNZIONI
    step_functions = {
        1: step_1_distributor_data,
        2: step_2_load_calculation,
        3: lambda: step_3_transformer_sizing(db),
        3.5: step_3_5_earth_switch_design,  # ✅ Step 3.5 aggiunto
        4: lambda: step_4_mt_switchgear_design(db),  # ✅ NOME CORRETTO
        5: step_5_protection_coordination,
        6: lambda: step_6_bt_switchgear_design(db),
        7: step_7_final_analysis
    }
    
    if current_step in step_functions:
        step_functions[current_step]()
    else:
        st.error(f"Step non valido: {current_step}")

if __name__ == "__main__":
    main()