"""
UI Progress - Progress bar e gestione session state
"""

import streamlit as st

def initialize_session_state():
    """Inizializza tutti i session state necessari"""
    
    # Dati distributore
    if 'distributor_data' not in st.session_state:
        st.session_state['distributor_data'] = {
            'voltage_kv': 20.0,
            'icc_3phase_ka': 12.5,
            'neutral_state': 'compensato',
            'earth_fault_current_a': 50,
            'earth_fault_time_s': 10.0,
            'double_earth_fault_time_s': 0.2,
            'cei_en_50160_compliant': True
        }
    
    # Carichi
    if 'loads' not in st.session_state:
        st.session_state['loads'] = []
    
    # Parametri progetto
    if 'project_params' not in st.session_state:
        st.session_state['project_params'] = {
            'installation_type': 'indoor',
            'service_continuity': 'normale',
            'transformer_redundancy': False,  # ✅ Ripristinata checkbox ridondanza
            'cei_016_required': True
        }
    
    # Risultati calcoli
    if 'calculation_results' not in st.session_state:
        st.session_state['calculation_results'] = None
    
    # Step corrente
    if 'current_step' not in st.session_state:
        st.session_state['current_step'] = 1
    
    # Step completati
    if 'completed_steps' not in st.session_state:
        st.session_state['completed_steps'] = set()

def render_progress_bar():
    """Progress bar con step del progetto"""
    
    step_names = [
        "Dati Distributore",
        "Calcolo Carichi", 
        "Trasformatori",
        "Sezionatore di Terra",
        "Quadro MT",
        "Coordinamento",
        "Quadro BT",
        "Analisi Finale"
    ]
    
    current_step = st.session_state['current_step']
    completed_steps = st.session_state['completed_steps']
    
    # Progress bar visuale
    progress_value = len(completed_steps) / len(step_names)
    st.progress(progress_value, f"Progresso: {len(completed_steps)}/{len(step_names)} step completati")
    
    # Indicatori step
    cols = st.columns(len(step_names))
    for i, (col, step_name) in enumerate(zip(cols, step_names), 1):
        with col:
            if i in completed_steps:
                st.success(f"✅ Step {i}")
            elif i == current_step:
                st.info(f"🔄 Step {i}")
            else:
                st.error(f"⭕ Step {i}")
            st.caption(step_name)
    
    return current_step