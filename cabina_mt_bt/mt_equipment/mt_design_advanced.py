"""
Progettazione avanzata quadro MT - Step 4 completo
"""

import streamlit as st
import pandas as pd
from database.products import UnitType

def step_4_mt_switchgear_design_advanced(db):
    """Step 4: Progettazione avanzata quadro MT con scelte tecniche guidate"""
    
    st.header("🔴 Step 4: Progettazione Quadro MT - Scelte Tecniche")
    
    if 3.5 not in st.session_state['completed_steps']:
        st.error("❌ Completa prima lo Step 3.5 (Sezionatore di Terra)")
        return
    
    # Recupera dati step precedenti
    distributor_data = st.session_state['distributor_data']
    transformer_config = st.session_state.get('transformer_config', {})
    
    # Inizializza session state per step 4
    _initialize_mt_session_state()
    
    # Dati di progetto per calcoli
    voltage_kv = distributor_data['voltage_kv']
    icc_ka = distributor_data['icc_3phase_ka']
    num_transformers = transformer_config.get('num_transformers', 2)
    transformer_power = transformer_config.get('power_kva', 400)
    total_power = transformer_power * num_transformers
    
    # Corrente nominale trasformatori
    transformer_current = (transformer_power * 1000) / (1.732 * voltage_kv * 1000)
    
    st.info(f"""
    **Dati di progetto da Step 3:**
    • Tensione: {voltage_kv} kV • Icc: {icc_ka} kA • Trasformatori: {num_transformers} x {transformer_power} kVA
    • Corrente nominale TR: {transformer_current:.0f} A • Potenza totale: {total_power} kVA
    """)
    
    # Progress sub-step con navigazione sequenziale
    current_substep = st.session_state['mt_design_step']
    _render_substep_progress(current_substep)
    
    # Navigazione sequenziale (solo il sub-step corrente è visibile)
    if current_substep == '4A':
        _step_4a_electrical_scheme(total_power)
    elif current_substep == '4B':
        _step_4b_units_configuration(voltage_kv, icc_ka, num_transformers, transformer_power, transformer_current, total_power)
    elif current_substep == '4C':
        _step_4c_equipment_selection(db, voltage_kv, icc_ka, total_power)
    elif current_substep == '4D':
        _step_4d_comparative_analysis(total_power)
    elif current_substep == '4E':
        _step_4e_final_verification(voltage_kv, icc_ka, total_power)
    else:
        st.error(f"Sub-step non valido: {current_substep}")
        st.session_state['mt_design_step'] = '4A'
        st.rerun()

def _render_substep_progress(current_substep):
    """Renderizza progress bar per i sub-step dello Step 4"""
    
    st.subheader("🔄 Avanzamento Progettazione")
    
    substeps = {
        '4A': "📐 Schema",
        '4B': "🏗️ Unità", 
        '4C': "⚡ Apparecchi",
        '4D': "📊 Confronti",
        '4E': "✅ Verifica"
    }
    
    # Progress visuale
    substep_order = ['4A', '4B', '4C', '4D', '4E']
    current_idx = substep_order.index(current_substep) if current_substep in substep_order else 0
    progress_value = current_idx / (len(substep_order) - 1)
    
    st.progress(progress_value, f"Sub-step {current_substep} di {len(substep_order)}")
    
    # Indicatori sub-step
    cols = st.columns(len(substeps))
    for i, (col, (step_id, step_name)) in enumerate(zip(cols, substeps.items())):
        with col:
            if step_id == current_substep:
                st.info(f"🔄 **{step_id}**")
            elif substep_order.index(step_id) < current_idx:
                st.success(f"✅ {step_id}")
            else:
                st.error(f"⭕ {step_id}")
            st.caption(step_name)
    
    st.markdown("---")

def _initialize_mt_session_state():
    """Inizializza session state specifico per step 4"""
    if 'mt_design_step' not in st.session_state:
        st.session_state['mt_design_step'] = '4A'
    
    if 'mt_electrical_scheme' not in st.session_state:
        st.session_state['mt_electrical_scheme'] = None
    
    if 'mt_units_config' not in st.session_state:
        st.session_state['mt_units_config'] = []
    
    if 'mt_equipment_selection' not in st.session_state:
        st.session_state['mt_equipment_selection'] = {}
    
    if 'mt_alternative_configs' not in st.session_state:
        st.session_state['mt_alternative_configs'] = []

def _step_4a_electrical_scheme(total_power):
    """4A. Scelta Schema Elettrico"""
    st.subheader("4A. Scelta Schema Elettrico")
    
    # Schemi elettrici disponibili
    electrical_schemes = {
        "single_busbar": {
            "name": "Sbarra Singola",
            "description": "Schema più semplice ed economico",
            "advantages": ["Costo ridotto", "Semplicità", "Minimo spazio"],
            "disadvantages": ["Interruzione servizio per manutenzione sbarra", "Continuità limitata"],
            "applications": ["Carichi non critici", "Budget limitato", "Spazio ristretto"],
            "min_units": 3,
            "recommended_power": "< 1500 kVA"
        },
        "sectioned_busbar": {
            "name": "Sbarra Singola Sezionata", 
            "description": "Sbarra con sezionatore di accoppiamento",
            "advantages": ["Flessibilità operativa", "Manutenzione parziale", "Costo contenuto"],
            "disadvantages": ["Complessità media", "Un unità aggiuntiva"],
            "applications": ["Carichi misti", "Buon compromesso", "Flessibilità futura"],
            "min_units": 4,
            "recommended_power": "500-2000 kVA"
        },
        "double_busbar": {
            "name": "Doppia Sbarra",
            "description": "Due sbarre indipendenti con accoppiamento",
            "advantages": ["Massima continuità", "Manutenzione senza interruzioni", "Flessibilità operativa"],
            "disadvantages": ["Costo elevato", "Complessità", "Spazio maggiore"],
            "applications": ["Carichi critici", "Ospedali", "Industrie continue"],
            "min_units": 5,
            "recommended_power": "> 1000 kVA"
        }
    }
    
    # Selezione schema
    col_scheme1, col_scheme2 = st.columns(2)
    
    with col_scheme1:
        st.write("**Seleziona Schema Elettrico:**")
        selected_scheme = st.radio(
            "Schema elettrico:",
            options=list(electrical_schemes.keys()),
            format_func=lambda x: electrical_schemes[x]["name"],
            key="electrical_scheme_radio"
        )
    
    with col_scheme2:
        scheme_data = electrical_schemes[selected_scheme]
        st.info(f"""
        **{scheme_data['name']}**
        
        {scheme_data['description']}
        
        **Vantaggi:**
        {chr(10).join([f"• {adv}" for adv in scheme_data['advantages']])}
        
        **Svantaggi:**  
        {chr(10).join([f"• {dis}" for dis in scheme_data['disadvantages']])}
        
        **Unità minime:** {scheme_data['min_units']}
        **Potenza consigliata:** {scheme_data['recommended_power']}
        """)
    
    # Raccomandazione automatica
    if total_power < 800:
        recommended = "single_busbar"
        reason = "Per potenze contenute, lo schema a sbarra singola è più economico"
    elif total_power < 1500:
        recommended = "sectioned_busbar" 
        reason = "Per potenze medie, la sbarra sezionata offre il miglior compromesso"
    else:
        recommended = "double_busbar"
        reason = "Per potenze elevate, la doppia sbarra garantisce massima continuità"
    
    if selected_scheme == recommended:
        st.success(f"✅ **Schema raccomandato per {total_power} kVA:** {reason}")
    else:
        st.warning(f"💡 **Raccomandazione:** {electrical_schemes[recommended]['name']} - {reason}")
    
    if st.button("➡️ Conferma Schema Elettrico", type="primary"):
        st.session_state['mt_electrical_scheme'] = {
            'type': selected_scheme,
            'data': scheme_data,
            'total_power': total_power,
            'recommended': selected_scheme == recommended
        }
        st.session_state['mt_design_step'] = '4B'
        st.success("✅ Schema elettrico confermato! Passaggio automatico a Configurazione Unità...")
        st.rerun()

def _step_4b_units_configuration(voltage_kv, icc_ka, num_transformers, transformer_power, transformer_current, total_power):
    """4B. Configurazione Unità Funzionali"""
    st.subheader("4B. Configurazione Unità Funzionali")
    
    if not st.session_state['mt_electrical_scheme']:
        st.error("❌ Completa prima il Step 4A (Schema Elettrico)")
        if st.button("⬅️ Torna a Schema Elettrico"):
            st.session_state['mt_design_step'] = '4A'
            st.rerun()
        return
    
    scheme_info = st.session_state['mt_electrical_scheme']
    scheme_type = scheme_info['type']
    min_units = scheme_info['data']['min_units']
    
    st.info(f"**Schema selezionato:** {scheme_info['data']['name']} - Minimo {min_units} unità")
    
    # Unità obbligatorie basate su schema e trasformatori
    mandatory_units = []
    
    # DG sempre obbligatorio
    mandatory_units.append({
        'type': 'DG',
        'description': 'Dispositivo Generale',
        'current': transformer_current * num_transformers,
        'function': 'Protezione generale e sezionamento',
        'mandatory': True
    })
    
    # Partenze trasformatori
    for i in range(num_transformers):
        mandatory_units.append({
            'type': f'TR{i+1}',
            'description': f'Partenza Trasformatore {i+1}',
            'current': transformer_current,
            'function': f'Alimentazione TR {transformer_power} kVA',
            'mandatory': True
        })
    
    # Unità per schema specifico
    if scheme_type == "sectioned_busbar":
        mandatory_units.append({
            'type': 'SECT',
            'description': 'Sezionatore Accoppiamento',
            'current': max(transformer_current * num_transformers, 630),
            'function': 'Accoppiamento sezioni sbarra',
            'mandatory': True
        })
    elif scheme_type == "double_busbar":
        mandatory_units.append({
            'type': 'COUP',
            'description': 'Accoppiamento Sbarre',
            'current': max(transformer_current * num_transformers, 1250),
            'function': 'Accoppiamento doppia sbarra',
            'mandatory': True
        })
    
    # Visualizza unità obbligatorie
    st.write("**🔴 Unità Obbligatorie:**")
    mandatory_df_data = []
    for unit in mandatory_units:
        mandatory_df_data.append({
            "Tipo": unit['type'],
            "Descrizione": unit['description'], 
            "Corrente": f"{unit['current']:.0f} A",
            "Funzione": unit['function']
        })
    
    mandatory_df = pd.DataFrame(mandatory_df_data)
    st.dataframe(mandatory_df, use_container_width=True)
    
    # Calcola configurazione finale e salva
    col_back, col_confirm = st.columns([1, 3])
    
    with col_back:
        if st.button("⬅️ Indietro"):
            st.session_state['mt_design_step'] = '4A'
            st.rerun()
    
    with col_confirm:
        if st.button("➡️ Conferma Configurazione Unità", type="primary"):
            total_width = len(mandatory_units) * 500  # Stima semplice
            total_cost = len(mandatory_units) * 10000  # Stima semplice
            
            st.session_state['mt_units_config'] = {
                'final_units': mandatory_units,
                'total_units': len(mandatory_units),
                'total_width': total_width,
                'total_cost': total_cost
            }
            st.session_state['mt_design_step'] = '4C'
            st.success("✅ Configurazione unità confermata! Passaggio automatico a Selezione Apparecchiature...")
            st.rerun()

def _step_4c_equipment_selection(db, voltage_kv, icc_ka, total_power):
    """4C. Selezione Apparecchiature"""
    st.subheader("4C. ⚡ Selezione Apparecchiature")
    
    if not st.session_state['mt_units_config']:
        st.error("❌ Completa prima il Step 4B (Configurazione Unità)")
        if st.button("⬅️ Torna a Configurazione Unità"):
            st.session_state['mt_design_step'] = '4B'
            st.rerun()
        return
    
    units_config = st.session_state['mt_units_config']
    final_units = units_config['final_units']
    
    # Selezione semplificata per ogni unità
    equipment_selection = {}
    total_equipment_cost = 0
    
    for i, unit in enumerate(final_units):
        st.write(f"**Unità {i+1}: {unit['description']} ({unit['current']:.0f}A)**")
        
        # Ottieni interruttore e relè dal database
        breaker = db.get_mt_breaker_by_specs(
            current=unit['current'],
            voltage_kv=voltage_kv,
            breaking_ka=icc_ka,
            indoor=True
        )
        
        relay_app = "DG" if unit['type'] == 'DG' else "Feeder"
        relay = db.get_protection_relay_by_application(relay_app)
        
        unit_cost = breaker.cost_estimate + relay.cost_estimate + 1000  # +1000 per TA/TV
        total_equipment_cost += unit_cost
        
        equipment_selection[unit['type']] = {
            'breaker': breaker,
            'relay': relay,
            'unit_total': unit_cost
        }
        
        st.info(f"**{breaker.series}** + **{relay.series}** = €{unit_cost:,}")
    
    # Riepilogo costi
    st.subheader("💰 Riepilogo Costi")
    total_mt_cost = units_config['total_cost'] + total_equipment_cost
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Costo Quadro", f"€{units_config['total_cost']:,}")
    with col2:
        st.metric("Costo Apparecchi", f"€{total_equipment_cost:,}")
    with col3:
        st.metric("**TOTALE MT**", f"€{total_mt_cost:,}")
    
    if st.button("➡️ Conferma Selezione Apparecchiature"):
        st.session_state['mt_equipment_selection'] = {
            'equipment': equipment_selection,
            'total_cost': total_equipment_cost,
            'total_mt_cost': total_mt_cost
        }
        st.session_state['mt_design_step'] = '4D'
        st.rerun()

def _step_4d_comparative_analysis(total_power):
    """4D. Analisi Comparative"""
    st.subheader("4D. 📊 Analisi Comparative")
    
    if not st.session_state['mt_equipment_selection']:
        st.error("❌ Completa prima il Step 4C (Selezione Apparecchiature)")
        if st.button("⬅️ Torna a Selezione Apparecchiature"):
            st.session_state['mt_design_step'] = '4C'
            st.rerun()
        return
    
    current_cost = st.session_state['mt_equipment_selection']['total_mt_cost']
    
    # Configurazione attuale vs alternative semplificate
    comparison_data = [
        {
            'Configurazione': 'Selezionata',
            'Costo': f"€{current_cost:,}",
            'Costo/kVA': f"€{current_cost/total_power:.0f}",
            'Stato': '✅ ATTUALE'
        },
        {
            'Configurazione': 'Alternativa Economica',
            'Costo': f"€{current_cost*0.85:,.0f}",
            'Costo/kVA': f"€{current_cost*0.85/total_power:.0f}",
            'Stato': '⚪ Disponibile'
        },
        {
            'Configurazione': 'Alternativa Premium',
            'Costo': f"€{current_cost*1.25:,.0f}",
            'Costo/kVA': f"€{current_cost*1.25/total_power:.0f}",
            'Stato': '⚪ Disponibile'
        }
    ]
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)
    
    col_back, col_confirm = st.columns([1, 3])
    
    with col_back:
        if st.button("⬅️ Indietro"):
            st.session_state['mt_design_step'] = '4C'
            st.rerun()
    
    with col_confirm:
        if st.button("➡️ Procedi alla Verifica Finale", type="primary"):
            st.session_state['mt_alternative_configs'] = comparison_data
            st.session_state['mt_design_step'] = '4E'
            st.success("✅ Analisi completata! Passaggio automatico a Verifica Finale...")
            st.rerun()

def _step_4e_final_verification(voltage_kv, icc_ka, total_power):
    """4E. Verifica e Conferma Finale"""
    st.subheader("4E. ✅ Verifica e Conferma Finale")
    
    if not st.session_state['mt_alternative_configs']:
        st.error("❌ Completa prima il Step 4D (Analisi Comparative)")
        if st.button("⬅️ Torna ad Analisi Comparative"):
            st.session_state['mt_design_step'] = '4D'
            st.rerun()
        return
    
    st.success(" Progettazione Quadro MT Completata")
    
    # Riepilogo esecutivo
    scheme_data = st.session_state['mt_electrical_scheme']
    units_data = st.session_state['mt_units_config']
    equipment_data = st.session_state['mt_equipment_selection']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Schema Elettrico", scheme_data['data']['name'])
        st.metric("Unità Funzionali", units_data['total_units'])
    with col2:
        st.metric("Costo Totale MT", f"€{equipment_data['total_mt_cost']:,}")
        st.metric("Tensione Nominale", f"{voltage_kv} kV")
    with col3:
        st.metric("Icc di Progetto", f"{icc_ka} kA")
        st.metric("Costo/kVA", f"€{equipment_data['total_mt_cost']/total_power:.0f}")
    
    # Conferma finale
    col_back, col_confirm = st.columns([1, 3])
    
    with col_back:
        if st.button("⬅️ Indietro"):
            st.session_state['mt_design_step'] = '4D'
            st.rerun()
    
    with col_confirm:
        if st.button("✅ CONFERMA PROGETTO QUADRO MT", type="primary"):
            # Salva configurazione finale completa
            st.session_state['mt_final_design'] = {
                'scheme': scheme_data,
                'units': units_data,
                'equipment': equipment_data,
                'total_cost': equipment_data['total_mt_cost'],
                'design_completed': True
            }
            
            st.session_state['completed_steps'].add(4)
            st.session_state['current_step'] = 5
            st.balloons()
            st.success("🎉 **Progettazione Quadro MT completata con successo!**")
            st.rerun()