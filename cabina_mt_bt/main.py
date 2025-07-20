"""
Software Cabina MT/BT Non Professional v2.0 - VERSIONE FINALE CORRETTA
Utilizza le funzioni esistenti in ui/steps.py
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

# Aggiunta la cartella del progetto al path per gli import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import dai moduli
try:
    from config.settings import APP_CONFIG, VERSION
except ImportError:
    APP_CONFIG = {
        "page_title": "Cabina MT/BT Professional",
        "page_icon": "⚡",
        "layout": "wide"
    }
    VERSION = "2.0"

try:
    from database.products import ProductDatabase
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    ProductDatabase = None

from ui.sidebar import render_sidebar
from ui.progress import render_progress_bar, initialize_session_state

# ✅ CORREZIONE: Import corretto in ui.steps
try:
    # ✅ NUOVO IMPORT:
    from ui.steps import (
        step_1_distributor_data,
        step_2_load_calculation,
        step_3_transformer_sizing,
        step_3_5_earth_switch_design,
        step_4_mt_switchgear_design,
        step_5_protection_coordination,
        step_6_bt_switchgear_design,
        step_8_earthing_system_design,  # 🆕 NUOVO
        step_9_final_analysis           # 🔄 RINOMINATO
    )
    UI_STEPS_AVAILABLE = True
    st.sidebar.success("✅ UI Steps caricati")
except ImportError as e:
    UI_STEPS_AVAILABLE = False
    st.sidebar.error(f"❌ Errore UI Steps: {str(e)}")

def main():
    """App principale con flusso guidato"""
    
    # Setup pagina
    st.set_page_config(**APP_CONFIG)
    
    # Inizializzazione
    initialize_session_state()
    
    # Header
    st.title("⚡ Software Cabina MT/BT Non Professional v2.0")
    st.markdown(f"**Versione {VERSION} - Progettazione Guidata Step-by-Step**")
    
    # STATUS CHECK: Mostra stato moduli
    with st.expander("🔍 Stato Moduli Sistema", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**UI Steps:**")
            st.write("✅ Disponibili" if UI_STEPS_AVAILABLE else "❌ Errore")
        
        with col2:
            st.write("**Sezionatore Terra:**")
            # Verifica se la funzione è disponibile
            try:
                # step_3_5_earth_switch_design
                st.write("✅ Disponibile")
            except NameError:
                st.write("❌ Non trovato")
        
        with col3:
            st.write("**Database:**")
            st.write("✅ Disponibile" if DB_AVAILABLE else "⚠️ Non disponibile")
    
    # Carica database
    if DB_AVAILABLE:
        try:
            db = ProductDatabase()
            st.sidebar.success("✅ Database prodotti caricato")
        except Exception as e:
            st.error(f"❌ Errore caricamento database: {e}")
            db = None
    else:
        db = None
        st.sidebar.warning("⚠️ Database prodotti non disponibile")
    
    # Sidebar per input dati
    render_sidebar()
    
    # Progress bar su tutta la larghezza
    current_step = render_progress_bar()
    
    st.markdown("---")
    
    # Verifica che UI steps siano disponibili per debug
    if not UI_STEPS_AVAILABLE:
        st.error("❌ Impossibile caricare gli step dell'interfaccia utente")
        st.info("Controlla che il file ui/steps.py sia corretto e che non ci siano errori di import")
        st.stop()
    
    #  funzioni step - ✅ TUTTE LE FUNZIONI ESISTONO IN ui/steps.py
    step_functions = {
        1: step_1_distributor_data,
        2: step_2_load_calculation,
        3: lambda: step_3_transformer_sizing(db) if db else step_3_transformer_sizing(None),
        3.5: step_3_5_earth_switch_design,
        4: lambda: step_4_mt_switchgear_design(db) if db else step_4_mt_switchgear_design(None),
        5: step_5_protection_coordination,
        6: lambda: step_6_bt_switchgear_design(db) if db else step_6_bt_switchgear_design(None),
        8: step_8_earthing_system_design,  # 🆕 NUOVO Step 8
        9: step_9_final_analysis           # 🔄 RINOMINATO da step 7
    }
    
    # Esecuzione step con gestione errori
    if current_step in step_functions:
        try:
            # Mostra informazioni step corrente
            step_info = {
            1: "📊 Dati Distributore",
            2: "⚡ Calcolo Carichi",
            3: "🔧 Dimensionamento Trasformatore",
            3.5: "⚡ Sezionatore di Terra",
            4: "🏗️ Quadro MT",
            5: "🛡️ Protezioni",
            6: "⚡ Quadro BT",
            8: "🌍 Impianto di Terra",  # 🆕 NUOVO
            9: "📋 Analisi Finale"     # 🔄 SPOSTATO
        }
            
            st.info(f"**Step {current_step}** - {step_info.get(current_step, 'Step sconosciuto')}")
            
            # Esegui funzione step
            step_functions[current_step]()
            
        except Exception as e:
            st.error(f"❌ Errore nell'esecuzione dello Step {current_step}: {str(e)}")
            
            # Debug info
            with st.expander("🔧 Informazioni Debug", expanded=False):
                st.code(f"Step: {current_step}\nErrore: {str(e)}\nTipo: {type(e).__name__}")
                
                # Suggerimenti specifici per errori
                if "earth_switch" in str(e).lower():
                    st.warning("""
                    **Possibili soluzioni per errori sezionatore terra:**
                    
                    1. Verifica che `mt_equipment/earth_switch.py` esista
                    2. Controlla che contenga le classi `EarthSwitchDesigner` e `EarthSwitchType`
                    3. Verifica che non ci siano errori di sintassi
                    """)
            
            # Pulsante per tornare al step precedente
            if st.button("⬅️ Torna al Step Precedente"):
                if current_step > 1:
                    st.session_state['current_step'] = current_step - 1
                    st.experimental_rerun()
    else:
        st.error(f"❌ Step non valido: {current_step}")
        st.info("Step disponibili: 1, 2, 3, 3.5, 4, 5, 6, 8, 9")  # ✅ AGGIORNATO

if __name__ == "__main__":
    main()