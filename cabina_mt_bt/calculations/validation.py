"""
Validazioni dati di progetto
"""

import streamlit as st

def validate_distributor_data():
    """Valida dati distributore"""
    data = st.session_state['distributor_data']
    
    required_fields = ['voltage_kv', 'icc_3phase_ka', 'neutral_state', 'earth_fault_current_a']
    
    for field in required_fields:
        if not data.get(field):
            return False, f"Campo mancante: {field}"
    
    if data['voltage_kv'] < 10 or data['voltage_kv'] > 36:
        return False, "Tensione deve essere tra 10 e 36 kV"
    
    if data['icc_3phase_ka'] < 5 or data['icc_3phase_ka'] > 50:
        return False, "Icc deve essere tra 5 e 50 kA"
    
    return True, "OK"

def validate_loads():
    """Valida carichi elettrici"""
    if not st.session_state.get('loads'):
        return False, "Nessun carico inserito"
    
    if len(st.session_state['loads']) == 0:
        return False, "Aggiungi almeno un carico"
    
    return True, "OK"

def validate_calculation_results():
    """Valida risultati calcolo carichi"""
    results = st.session_state.get('calculation_results')
    
    if not results:
        return False, "Calcolo carichi non eseguito"
    
    if results.get('total_power_kva', 0) <= 0:
        return False, "Potenza calcolata non valida"
    
    return True, "OK"

def validate_transformer_config():
    """Valida configurazione trasformatori"""
    config = st.session_state.get('transformer_config')
    
    if not config:
        return False, "Configurazione trasformatori non completata"
    
    required_fields = ['num_transformers', 'power_kva', 'total_power']
    for field in required_fields:
        if not config.get(field):
            return False, f"Campo mancante: {field}"
    
    return True, "OK"

def validate_mt_design():
    """Valida progetto quadro MT"""
    design = st.session_state.get('mt_final_design')
    
    if not design:
        return False, "Progetto quadro MT non completato"
    
    if not design.get('design_completed'):
        return False, "Progettazione quadro MT non finalizzata"
    
    return True, "OK"