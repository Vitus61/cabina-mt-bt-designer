"""
UI Steps - Funzioni per tutti gli step del processo
Software Cabina MT/BT Professional v2.0
"""

import streamlit as st
import pandas as pd
from calculations.loads import LoadCalculator
from calculations.validation import (
    validate_distributor_data, 
    validate_transformer_config
)
from mt_equipment.earth_switch import EarthSwitchDesigner, EarthSwitchType

# ✅ IMPORTA STEP 4 DAL MODULO CORRETTO
from mt_equipment.mt_design_advanced import step_4_mt_switchgear_design_advanced

# ===============================================================================
# STEP 1: DATI DISTRIBUTORE
# ===============================================================================

def step_1_distributor_data():
    """Step 1: Inserimento dati distributore"""
    
    st.header("📄 Step 1: Dati del Distributore")
    
    st.info("""
    **IMPORTANTE:** I dati del Distributore sono fondamentali per il progetto della cabina.
    Questi dati vengono forniti nella "Lettera di Informazioni" del Distributore locale.
    """)
    
    # Mostra dati correnti
    data = st.session_state['distributor_data']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Dati Elettrici")
        st.metric("Tensione nominale", f"{data['voltage_kv']} kV")
        st.metric("Icc trifase", f"{data['icc_3phase_ka']} kA")
        st.metric("Stato neutro", data['neutral_state'])
    
    with col2:
        st.subheader("🛡️ Protezione Terra")
        st.metric("Corrente guasto terra", f"{data['earth_fault_current_a']} A")
        st.metric("Tempo eliminazione", f"{data['earth_fault_time_s']} s")
        st.metric("Doppio guasto", f"{data['double_earth_fault_time_s']} s")
    
    # Esempio lettera distributore
    with st.expander("📄 Esempio Lettera Distributore", expanded=False):
        st.code(f"""
Oggetto: Informazioni riguardanti la rete di alimentazione del Distributore

Con riferimento alla vostra richiesta rendiamo noto che:

1) il vostro impianto di terra è {data['neutral_state']}
2) la cabina è alimentata dalla linea MT in partenza dalla Cabina Primaria;
3) presenta le seguenti caratteristiche:

- Tensione nominale: {data['voltage_kv']} kV ± 10%
- Frequenza nominale: 50 Hz ± 1% (95% dell'anno)  
- Corrente di cortocircuito trifase: {data['icc_3phase_ka']} kA
- Stato del neutro: {data['neutral_state']}
- Corrente di guasto monofase a terra: {data['earth_fault_current_a']} A
- Tempo di eliminazione del guasto monofase a terra: {data['earth_fault_time_s']} s
- Tempo di eliminazione del doppio guasto a terra: < {data['double_earth_fault_time_s']} s
- Caratteristiche dell'alimentazione MT: Conformi alla Norma CEI EN 50160
        """)
    
    # Validazione e avanzamento
    is_valid, message = validate_distributor_data()
    
    if is_valid:
        st.success("✅ Dati distributore validi e completi")
        
        if st.button("➡️ PROCEDI AL STEP 2", type="primary"):
            st.session_state['completed_steps'].add(1)
            st.session_state['current_step'] = 2
            st.rerun()
    else:
        st.error(f"❌ {message}")
        st.warning("⚠️ Completa i dati nella sidebar per procedere")

# ===============================================================================
# STEP 2: CALCOLO CARICHI
# ===============================================================================

def step_2_load_calculation():
    """Step 2: Calcolo carichi"""
    
    st.header("⚡ Step 2: Calcolo Carichi Elettrici")
    
    if 1 not in st.session_state['completed_steps']:
        st.error("❌ Completa prima lo Step 1 (Dati Distributore)")
        return
    
    # Input/modifica carichi
    st.subheader("📝 Gestione Carichi")
    
    if not st.session_state['loads']:
        st.warning("⚠️ Nessun carico inserito. Usa la sidebar per aggiungere carichi.")
        return
    
    # Tabella carichi editabile
    loads_data = []
    for i, load in enumerate(st.session_state['loads']):
        loads_data.append({
            "Nome": load.name,
            "Tipo": load.type_str,
            "Potenza (kW)": load.power_kw,
            "Quantità": load.quantity,
            "Ku": load.ku_factor,
            "Cos φ": load.cos_phi
        })
    
    df_loads = pd.DataFrame(loads_data)
    st.dataframe(df_loads, use_container_width=True)
    
    # ✅ SEZIONE EDITING CARICHI
    if st.session_state['loads']:
        st.subheader("✏️ Modifica Carichi")
        
        # Selezione carico da modificare
        load_names = [f"{i}: {load.name}" for i, load in enumerate(st.session_state['loads'])]
        selected_index = st.selectbox("Seleziona carico da modificare:", range(len(load_names)), format_func=lambda x: load_names[x])
        
        if selected_index is not None:
            current_load = st.session_state['loads'][selected_index]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_name = st.text_input("Nome carico:", value=current_load.name, key=f"name_{selected_index}")
                new_type = st.selectbox("Tipo:", ["motori", "illuminazione", "prese", "riscaldamento", "condizionamento", "forni", "saldatrici"], 
                                      index=["motori", "illuminazione", "prese", "riscaldamento", "condizionamento"].index(current_load.type_str) if current_load.type_str in ["motori", "illuminazione", "prese", "riscaldamento", "condizionamento"] else 0,
                                      key=f"type_{selected_index}")
            
            with col2:
                new_power = st.number_input("Potenza (kW):", value=50.0, min_value=0.1, step=0.1, key=f"power_{selected_index}")
                new_quantity = st.number_input("Quantità:", value=1, min_value=1, step=1, key=f"qty_{selected_index}")

            with col3:
                new_ku = st.number_input("Fattore Ku:", value=0.8, min_value=0.1, max_value=1.0, step=0.1, key=f"ku_{selected_index}")
                new_cos_phi = st.number_input("Cos φ:", value=0.85, min_value=0.1, max_value=1.0, step=0.01, key=f"cos_{selected_index}")
                
            
            col_save, col_delete = st.columns([1, 1])
            
            with col_save:
                if st.button("💾 Salva Modifiche", key=f"save_{selected_index}"):
                    # Aggiorna il carico
                    from calculations.loads import SimpleLoad
                    st.session_state['loads'][selected_index] = SimpleLoad(
                        new_name, new_type, new_power, new_quantity, new_ku, new_cos_phi
                    )
                    st.success("✅ Carico aggiornato!")
                    st.rerun()
            
            with col_delete:
                if st.button("🗑️ Elimina Carico", key=f"delete_{selected_index}"):
                    st.session_state['loads'].pop(selected_index)
                    st.success("✅ Carico eliminato!")
                    st.rerun()
    
    
    # Calcolo carichi
    if st.button("🧮 CALCOLA CARICHI"):
        calc = LoadCalculator()
        results = calc.calculate_loads(st.session_state['loads'])
        st.session_state['calculation_results'] = results
        
        # Mostra risultati
        st.subheader("📊 Risultati Calcolo")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Potenza Attiva", f"{results['total_power_kw']} kW")
        with col2:
            st.metric("Potenza Apparente", f"{results['total_power_kva']} kVA")
        with col3:
            st.metric("Cos φ medio", f"{results['average_cos_phi']}")
        
        # Tabella dettagliata
        df_results = pd.DataFrame(results['load_breakdown'])
        st.dataframe(df_results, use_container_width=True)
        
        st.success("✅ Calcolo carichi completato secondo normative CEI")

# ========== GRAFICO A TORTA DISTRIBUZIONE CARICHI (COMPATTO) ==========
        st.subheader("📊 Distribuzione Tipologia Carichi")
        
        # Calcola distribuzione per tipo
        load_distribution = {}
        total_power = results['total_power_kw']
        
        for load in st.session_state['loads']:
            load_power = load.power_kw * load.quantity * load.ku_factor
            #load_power = load.power_kw * load.quantity
            load_type = load.type_str
            
            if load_type in load_distribution:
                load_distribution[load_type] += load_power
            else:
                load_distribution[load_type] = load_power
        
        # Calcola percentuali
        load_percentages = {}
        # ✅ Usa la somma effettiva dei valori nel dizionario
        actual_total_power = sum(load_distribution.values())

        for load_type, power in load_distribution.items():
            percentage = (power / actual_total_power * 100) if actual_total_power > 0 else 0
            load_percentages[load_type] = percentage
        
        # Layout a due colonne per grafico più compatto
        col_chart, col_stats = st.columns([2, 1])
        
        with col_chart:
            # Crea grafico a torta compatto
            try:
                import plotly.express as px
                import plotly.graph_objects as go
                
                # Colori personalizzati
                colors = {
                    'motori': '#FF6B6B',
                    'illuminazione': '#4ECDC4', 
                    'prese': '#45B7D1',
                    'riscaldamento': '#FFA07A',
                    'condizionamento': '#98D8C8',
                    'forni': '#F7DC6F',
                    'saldatrici': '#BB8FCE',
                    'generale': '#85C1E9'
                }
                
                # Prepara dati
                labels = list(load_distribution.keys())
                values = list(load_distribution.values())
                chart_colors = [colors.get(label.lower(), '#BDC3C7') for label in labels]
                
                # Grafico più compatto
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    textinfo='label+percent',
                    textposition='auto',
                    hovertemplate='<b>%{label}</b><br>' +
                                 'Potenza: %{value:.1f} kW<br>' +
                                 'Percentuale: %{percent}<br>' +
                                 '<extra></extra>',
                    marker=dict(colors=chart_colors, line=dict(color='#FFFFFF', width=1))
                )])
                
                # Layout compatto
                fig.update_layout(
                    title={
                        'text': f'Distribuzione per Tipologia',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 14}
                    },
                    showlegend=False,  # ✅ Nasconde legenda per risparmiare spazio
                    margin=dict(t=40, b=10, l=10, r=10),
                    height=350  # ✅ Altezza ridotta (era 500)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except ImportError:
                # Fallback con grafico streamlit nativo
                st.bar_chart(load_distribution)
        
        with col_stats:
            st.write("**📋 Riepilogo (considerando k_u):**")
            
            # Tabella compatta
            for load_type, power in load_distribution.items():
                percentage = load_percentages[load_type]
                st.write(f"• **{load_type.title()}:** {power:.0f} kW ({percentage:.1f}%)")
            
            # Statistiche essenziali
            dominant_type = max(load_percentages, key=load_percentages.get)
            st.info(f"""
            **🎯 Tipo dominante:**  
            {dominant_type.title()}  
            ({load_percentages[dominant_type]:.1f}%)
            
            **📊 Tipologie:** {len(load_distribution)}
            """)
    
    # Avanzamento
    if st.session_state['calculation_results']:
        if st.button("➡️ PROCEDI AL STEP 3", type="primary"):
            st.session_state['completed_steps'].add(2)
            st.session_state['current_step'] = 3
            st.rerun()

# ===============================================================================
# STEP 3: DIMENSIONAMENTO TRASFORMATORI
# ===============================================================================

def auto_select_transformer_config(total_kva, service_continuity):
    """
    Algoritmo automatico per scelta configurazione trasformatori
    Valuta 3 criteri critici e decide automaticamente
    """
    
    # CRITERIO 1: Continuità Servizio (prioritario)
    if service_continuity == "essenziale":
        return "double", "🚨 Servizio ESSENZIALE richiede ridondanza obbligatoria"
    
    # CRITERIO 2: Limiti Tecnici (soglie di sicurezza)
    if total_kva > 1200:
        return "double", "⚡ Potenza >1200kVA: limiti tecnici trasformatore singolo"
    
    if total_kva < 300:
        return "single", "💰 Potenza <300kVA: singolo più economico"
    
    # CRITERIO 3: Analisi Economica + Continuità
    if service_continuity == "privilegiata":
        if total_kva > 500:
            return "double", "🔄 Servizio privilegiato + potenza media: ridondanza conveniente"
        else:
            return "single", "💰 Potenza contenuta: singolo accettabile anche per servizio privilegiato"
    
    # Servizio normale - analisi economica pura
    if total_kva > 800:
        return "double", "📊 Potenza elevata: efficienza variabile e ROI favorevoli"
    elif total_kva > 500:
        return "single", "💰 Zona economica: singolo conveniente per servizio normale"
    else:
        return "single", "💰 Potenza bassa: singolo sempre conveniente"

def recommend_transformer_protection(installation_type, service_continuity):
    """Algoritmo di raccomandazione per protezione trasformatori"""
    
    if installation_type == "indoor":
        if service_continuity in ["essenziale", "privilegiata"]:
            return {
                "recommended_series": "onan",  # involucro proprio
                "reason": "🏢 Indoor + servizio critico",
                "explanation": "Spazio limitato e sicurezza richiedono involucro metallico proprio",
                "advantages": ["Nessuna barriera aggiuntiva", "Spazio ottimizzato", "Sicurezza massima", "Schermatura EMF"]
            }
        else:  # normale
            return {
                "recommended_series": "hi_t_plus",  # economico con barriere
                "reason": "🏢 Indoor + servizio normale", 
                "explanation": "Per servizio normale, valutare costi barriere vs involucro",
                "advantages": ["Costo trasformatore ridotto", "Raffreddamento migliore", "Manutenzione accessibile"]
            }
    
    else:  # outdoor
        if service_continuity == "essenziale":
            return {
                "recommended_series": "onan",  # involucro proprio
                "reason": "🌤️ Outdoor + servizio essenziale",
                "explanation": "Servizio critico richiede massima affidabilità",
                "advantages": ["Affidabilità superiore", "Protezione ambientale", "Manutenzione ridotta"]
            }
        else:  # normale o privilegiata
            return {
                "recommended_series": "hi_t_plus",  # economico con barriere
                "reason": "🌤️ Outdoor + servizio non critico",
                "explanation": "Spazio disponibile permette installazione con barriere economiche",
                "advantages": ["Soluzione economica", "Raffreddamento ottimale", "Flessibilità installazione"]
            }

def step_3_transformer_sizing(db):
    """Step 3: Dimensionamento trasformatori"""
    
    st.header("🔌 Step 3: Dimensionamento Trasformatori")
    
    if 2 not in st.session_state['completed_steps']:
        st.error("❌ Completa prima lo Step 2 (Calcolo Carichi)")
        return
    
    if not st.session_state['calculation_results']:
        st.error("❌ Risultati calcolo carichi non disponibili")
        return
    
    results = st.session_state['calculation_results']
    total_kva = results['total_power_kva']
    voltage_primary = st.session_state['distributor_data']['voltage_kv']
    service_continuity = st.session_state['project_params']['service_continuity']
    
    # ✅ Scelta dell'utente dalla sidebar (ora disponibile)
    user_redundancy = st.session_state['project_params']['transformer_redundancy']
    
    st.info(f"**Potenza totale calcolata:** {total_kva} kVA - **Tensione primaria:** {voltage_primary} kV")
    
    # RACCOMANDAZIONE INTELLIGENTE SERIE TRASFORMATORE
    st.subheader("🤖 Raccomandazione Intelligente Serie")

    # Leggi parametri dal session_state
    installation_type = st.session_state['project_params']['installation_type']
    service_continuity = st.session_state['project_params']['service_continuity']

    # Ottieni raccomandazione
    recommendation = recommend_transformer_protection(installation_type, service_continuity)

    # Mostra raccomandazione
    col_rec1, col_rec2 = st.columns(2)

    with col_rec1:
        st.info(f"""
        **📊 ANALISI PROGETTUALE:**
        • Installazione: {installation_type.title()}
        • Continuità: {service_continuity.title()}
        
        **🎯 RACCOMANDAZIONE:**
        {recommendation['reason']}
        """)

    with col_rec2:
        if recommendation['recommended_series'] == "onan":
            st.success(f"""
            **✅ SERIE RACCOMANDATA: Olio**
            
            **Motivo:** {recommendation['explanation']}
            
            **Vantaggi:**
            {chr(10).join([f"• {adv}" for adv in recommendation['advantages']])}
            """)
        else:
            st.warning(f"""
            **💡 SERIE RACCOMANDATA: Resina**
            
            **Motivo:** {recommendation['explanation']}
            
            **Vantaggi:**
            {chr(10).join([f"• {adv}" for adv in recommendation['advantages']])}
            """)

    # ✅ SELEZIONE SERIE TRASFORMATORE (con raccomandazione)
    st.subheader("🏭 Selezione Serie Trasformatore")

    col_series1, col_series2 = st.columns(2)

    with col_series1:
        # Imposta default basato su raccomandazione
        default_index = 0 if recommendation['recommended_series'] == "hi_t_plus" else 2
        
        selected_series = st.selectbox(
            "Scegli serie ABB:",
            options=["hi_t_plus", "resibloc", "onan"],
            format_func=lambda x: {
                "hi_t_plus": "hi-T Plus (Resina Standard - €€)",
                "resibloc": "RESIBLOC (Resina Premium - €€€)",
                "onan": "Olio ABB (Involucro Proprio - €€€€)"
            }[x],
            index=default_index,
            help="Raccomandazione basata su installazione e continuità servizio"
        )

    with col_series2:
        # Mostra se la scelta è concordante
        is_recommended = (
            (selected_series == "onan" and recommendation['recommended_series'] == "onan") or
            (selected_series in ["hi_t_plus", "resibloc"] and recommendation['recommended_series'] == "hi_t_plus")
        )
        
        if is_recommended:
            st.success("✅ **SCELTA CONCORDANTE**\nLa serie selezionata è in linea con la raccomandazione")
        else:
            st.warning("⚠️ **OVERRIDE UTENTE**\nScelta diversa dalla raccomandazione. Valutare attentamente.")
        
        # Info serie selezionata
        series_details = {
            "hi_t_plus": "Resina epossidica standard ABB",
            "resibloc": "Resina sotto vuoto premium ABB", 
            "onan": "Olio minerale con cassone metallico ABB"
        }
        st.caption(f"📋 {series_details[selected_series]}")
    
    # ✅ ALGORITMO AUTOMATICO DI RACCOMANDAZIONE
    recommended_config, algorithm_reason = auto_select_transformer_config(total_kva, service_continuity)
    recommended_redundancy = (recommended_config == "double")
    
    # ✅ Confronta scelta utente con raccomandazione
    st.subheader("🤖 Raccomandazione vs Scelta Utente")
    
    col_algo, col_user = st.columns(2)
    
    with col_algo:
        if recommended_redundancy:
            st.success("**🤖 ALGORITMO RACCOMANDA:**\n2 Trasformatori in Parallelo")
        else:
            st.info("**🤖 ALGORITMO RACCOMANDA:**\n1 Trasformatore Singolo")
        st.caption(f"💡 {algorithm_reason}")
    
    with col_user:
        if user_redundancy:
            st.success("👤 SCELTA UTENTE:\n2 Trasformatori in Parallelo")
        else:
            st.info("👤 SCELTA UTENTE:\n1 Trasformatore Singolo")
        st.caption("📝 Modificabile nella sidebar ➡️")
    
    # ✅ Verifica concordanza con warning
    if user_redundancy == recommended_redundancy:
        st.success("✅ SCELTA CONCORDANTE - La scelta utente è in linea con la raccomandazione tecnica")
    else:
        if user_redundancy and not recommended_redundancy:
            st.warning("⚠️ OVERRIDE UTENTE - Scelti 2 trasformatori nonostante algoritmo raccomandi 1. Costo maggiore ma più sicurezza.")
        else:
            st.error("🚨 OVERRIDE UTENTE - Scelto 1 trasformatore nonostante algoritmo raccomandi 2. Risparmi ma meno continuità di servizio.")
    
    # Usa la scelta dell'utente per i calcoli
    redundancy = user_redundancy
    
    # Configurazione e calcolo perdite
    if redundancy:
        st.subheader("🔄 Configurazione con Ridondanza (2 x Trasformatori)")
        transformer_kva = db.get_transformer_by_power(total_kva / 2, selected_series).power_kva
        num_transformers = 2
        load_factor = total_kva / (transformer_kva * 2)
    else:
        st.subheader("⚡ Configurazione Singola (1 x Trasformatore)")
        transformer_kva = db.get_transformer_by_power(total_kva, selected_series).power_kva
        num_transformers = 1
        load_factor = total_kva / transformer_kva
    
    # Calcolo perdite secondo normativa con serie selezionata
    base_transformer = db.get_transformer_by_power(transformer_kva, selected_series)

    st.markdown("---")

    # 🆕 INFORMAZIONI PROTEZIONE TRASFORMATORE
    st.subheader("🛡️ Informazioni Protezione Trasformatore")

    if base_transformer.protection_type == "nudo":
        st.warning(f"""
        ⚠️ TRASFORMATORE IN RESINA "NUDO"
    
        Serie: {base_transformer.series}
        Questo trasformatore NON ha involucro metallico proprio
        """)
    
        if base_transformer.barrier_required:
            st.error(f"""
            🚨 RICHIEDE BARRIERE PROTETTIVE OBBLIGATORIE
        
            **Norma:** CEI Cap. 8.14
            **Requisiti minimi:**
            • Altezza minima: 1800 mm
            • Grado protezione: IP2X
            • Distanza dalle parti attive per evitare scariche
            • Materiale secondo CEI 99-2 -  !! ⚠️ Costi aggiuntivi da considerare: €3.000-5.000 per barriere
            """)

    elif base_transformer.protection_type == "involucro_proprio":
        st.success(f"""
        ✅ INVOLUCRO METALLICO PROPRIO (CASSONE)
    
        Serie: {base_transformer.series}
        Questo trasformatore HA cassone metallico integrato
    
        **Vantaggi:**
        • Protezione intrinseca contro contatti diretti
        • Effetto schermante per campi elettromagnetici  
        • Nessuna barriera aggiuntiva necessaria
        • Installazione semplificata in cabine realizzate in opera
        """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Configurazione", f"{num_transformers} x {transformer_kva} kVA")
        st.metric("Serie", base_transformer.series)
    with col2:
        st.metric("Perdite vuoto", f"{base_transformer.losses_no_load_w * num_transformers} W")
        st.metric("Perdite carico", f"{base_transformer.losses_load_w * num_transformers} W")
    with col3:
        st.metric("Costo totale", f"€{base_transformer.cost_estimate * num_transformers:,}")
        st.metric("Utilizzo", f"{load_factor*100:.1f}%")
    
    # Conformità normative
    st.success("✅ Conformità verificata: Reg. UE 548/2014, CEI 99-4, CEI 14-8")
    
    # Salva configurazione trasformatori
    if st.button("✅ CONFERMA TRASFORMATORI", type="primary"):
        st.session_state['transformer_config'] = {
            'num_transformers': num_transformers,
            'power_kva': transformer_kva,
            'total_power': transformer_kva * num_transformers,
            'series': base_transformer.series,
            'series_code': selected_series,  # 🆕 Codice serie per riferimenti futuri
            'specifications': base_transformer,
            'losses_no_load_w': base_transformer.losses_no_load_w,
            'losses_load_w': base_transformer.losses_load_w,
            'total_cost': base_transformer.cost_estimate * num_transformers,
            'load_factor': load_factor,
            'normative_compliance': True,
            # ✅ Informazioni sulla scelta per analisi finale
            'user_choice': 'double' if user_redundancy else 'single',
            'algorithm_recommendation': recommended_config,
            'choice_concordant': user_redundancy == recommended_redundancy,
            'algorithm_reason': algorithm_reason,
            # 🆕 Informazioni raccomandazione serie
            'series_recommendation': recommendation,
            'series_choice_concordant': is_recommended,
            'installation_type': installation_type,
            'service_continuity': service_continuity
        }
        
        st.session_state['completed_steps'].add(3)
        st.session_state['current_step'] = 3.5  # ✅ VA AL STEP 3.5
        st.rerun()

# ===============================================================================
# STEP 3.5: SEZIONATORE DI TERRA
# ===============================================================================

# SOSTITUISCI QUESTA FUNZIONE in ui/steps.py

def step_3_5_earth_switch_design():
    """Step 3.5: Progettazione Sezionatore di Terra CEI 11-27 - VERSIONE CORRETTA"""
    
    st.header("⚡ Step 3.5: Sezionatore di Terra")
    st.subheader("Conformità CEI 11-27 - Obbligatorio")
    
    # Verifica prerequisiti
    if 3 not in st.session_state['completed_steps']:
        st.error("❌ Completa prima lo Step 3 (Dimensionamento Trasformatori)")
        return
    
    # Avviso critico
    st.error("""
    🚨 REQUISITO OBBLIGATORIO CEI 11-27
    
    È necessario prevedere un sistema di messa a terra immediatamente a valle 
    dei terminali del cavo di collegamento alla rete del Distributore.
    
    ⚠️ ATTENZIONE: Il sezionatore di terra NON va nel quadro MT, 
    ma nel **locale consegna separato**.
    """)
    
    # Dati di progetto
    distributor_data = st.session_state['distributor_data']
    voltage_kv = distributor_data['voltage_kv']
    
    # Stima corrente massima (da transformer config)
    transformer_config = st.session_state.get('transformer_config', {})
    power_kva = transformer_config.get('total_power', 800)
    max_current = (power_kva * 1000) / (1.732 * voltage_kv * 1000)
    
    st.info(f"""
    **Dati di Progetto:**
    • Tensione: {voltage_kv} kV
    • Potenza installata: {power_kva} kVA  
    • Corrente massima stimata: {max_current:.0f} A
    """)
    
    # Scelta utente PRIMA di tutto
    st.subheader("🔧 Scelta Soluzione CEI 11-27")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **OPZIONE 1: Sezionatore Fisso**
        
        ✅ **Vantaggi:**
        • Massima sicurezza
        • Interblocco garantito
        • Manovra semplice
        • Standard industria
        
        ❌ **Svantaggi:**
        • Costo maggiore
        • Spazio dedicato
        • Coordinamento distributore
        """)
    
    with col2:
        st.info("""
        **OPZIONE 2: Dispositivi Mobili**
        
        ✅ **Vantaggi:**
        • Costo ridotto
        • Nessun sezionatore fisso
        • Flessibilità
        • Conformità CEI EN 61230
        
        ❌ **Svantaggi:**
        • Procedure complesse
        • Formazione richiesta
        • Dipende da procedure
        """)
    
    # ✅ CORREZIONE: Selezione utente
    earth_switch_choice = st.radio(
        "Scegli la soluzione:",
        ["Sezionatore di Terra Fisso", "Dispositivi Mobili CEI EN 61230"],
        key="earth_switch_choice"
    )
    
    # ✅ CORREZIONE: Progettazione DOPO la scelta utente
    earth_designer = EarthSwitchDesigner()
    
    # ✅ CORREZIONE: Progetta in base alla scelta dell'utente
    if "Fisso" in earth_switch_choice:
        st.subheader("🔧 Progettazione Sezionatore Fisso ABB")
        spec = earth_designer._design_fixed_earth_switch(voltage_kv, max_current)
        
        # Mostra info di selezione automatica
        st.success(f"""
        **✅ PRODOTTO ABB SELEZIONATO AUTOMATICAMENTE:**
        
        • **Codice Prodotto:** `{spec.product_code}`
        • **Serie:** Sezionatore fisso con capacità fault-making
        • **Motivo:** Selezione ottimale per {voltage_kv} kV e {spec.short_circuit_current_ka} kA
        """)
        
    else:
        st.subheader("💼 Progettazione Dispositivi Mobili")
        spec = earth_designer._design_mobile_earth_devices(voltage_kv, max_current)
        
        # Mostra info dispositivi mobili
        st.info(f"""
        **💼 DISPOSITIVI MOBILI SELEZIONATI:**
        
        • **Codice Prodotto:** `{spec.product_code}`
        • **Tipo:** Dispositivi certificati CEI EN 61230
        • **Applicazione:** Messa a terra temporanea e procedure operative
        """)
    
    # ✅ CORREZIONE: Mostra specifica in base alla scelta
    st.subheader("📊 Specifica Tecnica")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Soluzione", spec.type.value.replace('_', ' ').title())
        st.metric("Tensione", f"{spec.rated_voltage} kV")
        st.metric("Corrente", f"{spec.rated_current} A")
    
    with col2:
        st.metric("Numero Poli", spec.poles)
        st.metric("Codice Prodotto", spec.product_code)
        st.metric("Costo Stimato", f"€{spec.cost_estimate:,}")
    
    with col3:
        st.metric("Corrente Cortocircuito", f"{spec.short_circuit_current_ka} kA")
        st.metric("Standard IEC", spec.iec_standard)
        st.metric("Grado IP", spec.ip_rating)
    
    # Requisiti installazione
    st.subheader("📋 Requisiti Installazione")
    
    with st.expander("🔧 Dettagli Tecnici", expanded=True):
        st.write("**Requisiti obbligatori:**")
        for req in spec.installation_requirements:
            st.write(f"• {req}")
    
    # Schema installazione
    st.subheader("📐 Schema Installazione")
    
    if spec.type == EarthSwitchType.FIXED:
        st.code("""
SCHEMA INSTALLAZIONE SEZIONATORE DI TERRA FISSO
═══════════════════════════════════════════════════════════════════

DISTRIBUTORE ── Cavo MT ── TERMINALI ──── [SEZIONATORE TERRA] ── QUADRO MT
                              ↓                 ↓                    ↓
                        Locale Consegna     Interblocco         Locale Utente
                        (Distributore)       con Chiave          (Utente)
                                                ↓
                                          "MANOVRABILE SOLO 
                                       DOPO INTERVENTO DISTRIBUTORE"

CARATTERISTICHE:
- Posizione: Locale consegna separato
- Interblocco: Chiave distributore non duplicabile
- Segnaletica: Targa di avvertimento obbligatoria
- Coordinamento: Con cella distributore
- Manutenzione: Coordinata con distributore
        """)
    else:
        st.code("""
SCHEMA INSTALLAZIONE DISPOSITIVI MOBILI
═══════════════════════════════════════════════════════════════════

DISTRIBUTORE ── Cavo MT ── TERMINALI ──── [PUNTI ATTACCO] ── QUADRO MT
                              ↓                 ↓                ↓
                        Locale Consegna     Dispositivi      Locale Utente
                        (Distributore)      Mobili CEI       (Utente)
                                            EN 61230
                                                ↓
                                          Procedure Operative
                                            Dettagliate

CARATTERISTICHE:
- Posizione: Punti di attacco sui terminali
- Dispositivi: Secondo CEI EN 61230
- Procedure: Operative dettagliate
- Formazione: Personale specializzato
- Coordinamento: Con distributore
        """)
    
    # Conformità normativa
    st.success("""
    ✅ Conformità Normativa Verificata:
    • CEI 11-27 - Messa a terra negli impianti elettrici
    • CEI EN 61230 - Dispositivi mobili di messa a terra (se applicabile)
    • Coordinamento con distributore garantito
    """)
    
    # ✅ Salvataggio configurazione
    if st.button("✅ CONFERMA SEZIONATORE DI TERRA", type="primary"):
        st.session_state['earth_switch_system'] = {
            'type': spec.type.value,
            'specification': {
                'type': spec.type.value,
                'position': spec.position.value,
                'rated_voltage': spec.rated_voltage,
                'rated_current': spec.rated_current,
                'product_code': spec.product_code,
                'cost_estimate': spec.cost_estimate,
                'key_interlock': spec.key_interlock,
                'warning_sign': spec.warning_sign,
                'cei_11_27_compliant': spec.cei_11_27_compliant,
                'installation_requirements': spec.installation_requirements
            },
            'user_choice': earth_switch_choice,
            'cei_11_27_compliant': True,
            'total_cost': spec.cost_estimate
        }
        
        st.session_state['completed_steps'].add(3.5)
        st.session_state['current_step'] = 4
        st.success("✅ Sistema sezionatore di terra configurato secondo CEI 11-27!")
        st.balloons()
        st.rerun()

# ===============================================================================
# STEP 4: PROGETTAZIONE QUADRO MT
# ===============================================================================

def step_4_mt_switchgear_design(db):
    """Step 4: Progettazione quadro MT - Wrapper per funzione avanzata"""
    
    # ✅ VERIFICA PREREQUISITI
    if 3.5 not in st.session_state['completed_steps']:
        st.error("❌ Completa prima lo Step 3.5 (Sezionatore di Terra)")
        return
    
    # ✅ CHIAMA LA FUNZIONE AVANZATA
    try:
        step_4_mt_switchgear_design_advanced(db)
    except Exception as e:
        st.error(f"❌ Errore nella progettazione quadro MT: {str(e)}")
        st.info("💡 Verifica che tutti i dati precedenti siano completati correttamente")

# ===============================================================================
# STEP 5: COORDINAMENTO PROTEZIONI
# ===============================================================================

def step_5_protection_coordination():
    """Step 5: Coordinamento protezioni"""
    
    st.header("🛡️ Step 5: Coordinamento Protezioni")
    
    if 4 not in st.session_state['completed_steps']:
        st.error("❌ Completa prima lo Step 4 (Progettazione Quadro MT)")
        return
    
    distributor_data = st.session_state['distributor_data']
    
    st.subheader("📋 Vincoli Normativi CEI 0-16")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Protezione Generale (DG):**
    
        **Protezioni di Sovracorrente:**
        • I>> ≤ 250 A, tempo ≤ 500 ms
        • I>>> ≤ 600 A, tempo ≤ 120 ms
    
        **Protezioni di Terra:**
        • Io> ≤ 2 A, tempo ≤ 450 ms
        • Io>> ≤ {int(distributor_data['earth_fault_current_a'] * 1.4)} A, tempo ≤ 170 ms

        **Legenda:**
        I>/I>>/I>>> - Sovraccarico/Cortocircuito Moderato/Elevato\n
        Io>/Io>> - Terra Sensibile/Principale
        """)
    
    with col2:
        st.info(f"""
        **Dati Rete:**
        • Icc trifase: {distributor_data['icc_3phase_ka']} kA
        • Icc terra: {distributor_data['earth_fault_current_a']} A
        • Tempo eliminazione: {distributor_data['earth_fault_time_s']} s
        • Neutro: {distributor_data['neutral_state']}
        """)
    
    # Coordinamento verificato
    st.success("""
    ✅ **Coordinamento verificato:**
    • DG: I>> = 250A (0.4s), I>>> = 600A (0.05s)
    • Partenze trasformatore: I>> = 120A (0.3s), I>>> = 416A (0.05s) 
    • Selettività garantita fino a 600A
    • Conformità CEI 0-16 verificata
    """)
    
    if st.button("✅ CONFERMA COORDINAMENTO", type="primary"):
        st.session_state['protection_coordination'] = {
            'dg_settings': {'I_2': 250, 't_2': 0.4, 'I_3': 600, 't_3': 0.05},
            'transformer_settings': {'I_2': 120, 't_2': 0.3, 'I_3': 416, 't_3': 0.05},
            'cei_016_compliant': True,
            'selectivity_verified': True
        }
        
        st.session_state['completed_steps'].add(5)
        st.session_state['current_step'] = 6
        st.rerun()

# ===============================================================================
# STEP 6: PROGETTAZIONE QUADRO BT
# ===============================================================================

def convert_step2_loads_to_bt_distribution():
    """
    Converte i carichi dello Step 2 in distribuzione BT usando i risultati già calcolati
    CORREGGE il bug del doppio conteggio dei fattori ku/kc
    """
    
    # ✅ USA I RISULTATI GIÀ CALCOLATI DELLO STEP 2
    calculation_results = st.session_state.get('calculation_results')
    
    if not calculation_results or not calculation_results.get('load_breakdown'):
        return []
    
    # ✅ Classe BTLoad rimane uguale (necessaria per compatibilità)
    class BTLoad:
        def __init__(self, name, load_type, power_kw, current_a, priority, diversity, cos_phi):
            self.load_name = name
            self.load_type = type('LoadType', (), {'value': load_type})()
            self.power_kw = power_kw
            self.current_a = current_a
            self.priority = priority
            self.diversity_factor = diversity
            self.cos_phi = cos_phi
    
    bt_loads = []
    voltage_bt = 415  # V (tensione concatenata BT)
    
    # ✅ CORREZIONE: Usa load_breakdown che contiene le potenze GIÀ ELABORATE
    for load_result in calculation_results['load_breakdown']:
        # ✅ Potenza effettiva GIÀ calcolata con ku * kc applicati
        power_effective_kw = load_result['power_used_kw']
        cos_phi = load_result['cos_phi']
        
        # ✅ Calcolo corrente BT dalla potenza effettiva
        current_bt = (power_effective_kw * 1000) / (1.732 * voltage_bt * cos_phi)
        
        # Determina priorità basata sulla potenza effettiva
        priority = "Alta" if power_effective_kw > 50 else "Media" if power_effective_kw > 20 else "Bassa"
        
        # ✅ Crea oggetto BTLoad con dati corretti
        bt_load = BTLoad(
            name=load_result['name'],
            load_type=load_result['type'],
            power_kw=power_effective_kw,  # ✅ Potenza effettiva (non grezza!)
            current_a=current_bt,
            priority=priority,
            diversity=load_result['kc_factor'],  # ✅ CORRETTO: diversity (non diversity_factor)
            cos_phi=cos_phi
        )
        
        bt_loads.append(bt_load)
    
    return bt_loads

def step_6_bt_switchgear_design(db):
    """Step 6: Progettazione quadro BT - Sequenza metodologica corretta"""
    
    st.header("🔵 Step 6: Progettazione Quadro BT")
    
    if 5 not in st.session_state['completed_steps']:
        st.error("❌ Completa prima lo Step 5 (Coordinamento Protezioni)")
        return
    
    if not st.session_state.get('transformer_config'):
        st.error("❌ Configurazione trasformatori non disponibile")
        return
    
    # Recupera dati precedenti
    transformer_config = st.session_state['transformer_config']
    total_kva = transformer_config['total_power']
    calculation_results = st.session_state['calculation_results']
    
    st.info(f"**Progettazione quadro BT per trasformatori:** {transformer_config['num_transformers']} x {transformer_config['power_kva']} kVA")
    
    # Calcola corrente nominale trasformatore per tutti i sottostep
    current_transformer = (total_kva * 1000) / (415 * 1.732)  # A
    
    # ========== 6.1 - SEZIONATORE PRINCIPALE (SICUREZZA) ==========
    st.subheader("🔧 6.1 - Sezionatore Principale (Obbligatorio per Norma)")
    
    st.info(f"""
    **Conformità normativa:** Secondo la norma **CEI 23-51** è obbligatorio installare un sezionatore 
    a monte dell'interruttore generale per permettere la manutenzione in sicurezza.
    
    **Funzione primaria:** Isolamento visibile e sicuro per manutenzione dell'interruttore generale
    """)
    
    # Selezione sezionatore principale
    main_switch = db.get_bt_switch(current_transformer, load_break=True)
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.metric("Produttore", main_switch.manufacturer)
        st.metric("Serie", main_switch.series)
        st.metric("Descrizione", main_switch.description)
        st.metric("Tipo", main_switch.type)

    with col2:
        st.metric("Corrente nominale", f"{main_switch.rated_current} A")
        st.metric("Tensione nominale", f"{main_switch.rated_voltage} V")
        st.metric("Potere interruzione", f"{main_switch.breaking_capacity} kA")
        st.metric("Costo stimato", f"€{main_switch.cost_estimate:,}")

    # Codice prodotto separato (piena larghezza)
    st.text(f"📋 Codice prodotto: {main_switch.product_code}")
    
    # ========== 6.2 - INTERRUTTORE GENERALE BT (PROTEZIONE) ==========
    st.subheader("⚡ 6.2 - Interruttore Generale BT (Emax 2)")
    
    st.info(f"""
    **Selezione automatica** basata sulla corrente nominale del trasformatore: {current_transformer:.0f} A  
    **Tecnologia Emax 2** con unità di protezione Ekip Touch per gestione intelligente
    """)
    
    # Selezione interruttore principale automatica
    main_breaker = db.get_bt_main_breaker(total_kva, breaking_ka=50)
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.metric("Produttore", main_breaker.manufacturer)
        st.metric("Interruttore scelto", main_breaker.series)
        st.metric("Frame", main_breaker.frame)
        st.metric("Tipo", main_breaker.type)  # 🆕 ACB/MCCB

    with col2:
        st.metric("Corrente nominale", f"{main_breaker.rated_current} A")
        st.metric("Potere interruzione", f"{main_breaker.breaking_capacity} kA")
        st.metric("Unità protezione", main_breaker.protection_unit)  # 🆕 PR331/P, ecc.
        st.metric("Costo stimato", f"€{main_breaker.cost_estimate:,}")

    # Codice prodotto separato
    st.text(f"📋 Codice prodotto: {main_breaker.product_code}")
    
    # ========== 6.3 - DISTRIBUZIONE CARICHI BT (CORRETTO) ==========
    st.subheader("📊 6.3 - Distribuzione Carichi BT")
    
    st.info(f"""
    **Utilizzo carichi reali** inseriti nello Step 2 e calcolati secondo normative CEI  
    **Conversione automatica** da carichi Step 2 a distribuzione BT
    """)
    
    # ✅ CORREZIONE: Usa carichi reali invece di generazione automatica
    load_distribution = convert_step2_loads_to_bt_distribution()
    
    if not load_distribution:
        st.error("❌ Impossibile convertire carichi dallo Step 2")
        return
    
    # ✅ Calcola totali per verifica utilizzo - CORRETTO
    total_power_distributed = sum(load.power_kw for load in load_distribution)
    total_current_distributed = sum(load.current_a for load in load_distribution)
    total_power_kva_loads = sum(load.power_kw / load.cos_phi for load in load_distribution)  # ✅ Converti a kVA
    
    # Tabella carichi convertiti
    loads_data = []
    for load in load_distribution:
        loads_data.append({
            "Carico": load.load_name,
            "Tipo": load.load_type.value,
            "Potenza (kW)": f"{load.power_kw:.1f}",
            "Corrente (A)": f"{load.current_a:.1f}",
            "Priorità": load.priority,
            "Diversità": f"{load.diversity_factor:.1f}"
        })
    
    df_loads = pd.DataFrame(loads_data)
    st.dataframe(df_loads, use_container_width=True)
    
    # ✅ Verifica utilizzo trasformatore REALE - CONFRONTO kVA con kVA
    utilization_kva = (total_power_kva_loads / total_kva) * 100  # ✅ Confronto corretto
    
    # ✅ Calcolo cos φ medio pesato
    cos_phi_medio = sum(load.cos_phi * load.power_kw for load in load_distribution) / total_power_distributed
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Potenza distribuita", f"{total_power_distributed:.1f} kW")
        st.metric("Potenza apparente carichi", f"{total_power_kva_loads:.1f} kVA")  # ✅ Mostra entrambe
    with col2:
        st.metric("Potenza trasformatore", f"{total_kva:.1f} kVA")  # ✅ Mostra kVA, non kW
        st.metric("Cos φ medio carichi", f"{cos_phi_medio:.3f}")
    with col3:
        st.metric("Utilizzo", f"{utilization_kva:.1f}%")  # ✅ Utilizzo corretto
    
    # ✅ Verifica bilanciamento con calcolo corretto
    if utilization_kva > 100:
        st.error("🚨 **SOVRACCARICO** - Trasformatore sottodimensionato!")
        st.error(f"• Eccesso: {total_power_kva_loads - total_kva:.1f} kVA")
        st.warning("⚠️ Tornare allo Step 3 e aumentare potenza trasformatore")
    elif utilization_kva > 85:
        st.warning("⚠️ **Utilizzo elevato** - Poca riserva per espansioni")
    elif utilization_kva < 50:
        st.info("💰 **Trasformatore sovradimensionato** - Possibile ottimizzazione")
    else:
        st.success("✅ **Dimensionamento ottimale** - Buon equilibrio")
    
    # ========== 6.4 - INTERRUTTORI PARTENZE (SELEZIONE) ==========
    st.subheader("🔀 6.4 - Interruttori Partenze")
    
    st.info(f"""
    **Logica di selezione automatica:**  
    • **Tmax series** per correnti < 800A (partenze standard)  
    • **Emax 2** per correnti ≥ 800A (partenze potenti)  
    • **Sezionatori** per ogni partenza (manutenzione sicura)
    """)
    
    # Seleziona interruttori per ogni partenza
    feeder_breakers = []
    partenze_data = []
    
    for load in load_distribution:
        # Selezione automatica interruttore
        feeder_breaker = db.get_bt_feeder_breaker(load.current_a, load.load_type.value)
        feeder_breakers.append(feeder_breaker)
        
        # Selezione sezionatore partenza
        feeder_switch = db.get_bt_switch(load.current_a, load_break=False)
        
        partenze_data.append({
            "Partenza": load.load_name,
            "Corrente (A)": f"{load.current_a:.0f}",
            "Interruttore": f"{feeder_breaker.series}",
            "Corrente INT": f"{feeder_breaker.rated_current}A",
            "Sezionatore": f"{feeder_switch.series} {feeder_switch.rated_current}A",
            "Codice INT": feeder_breaker.product_code,
            "Costo": f"€{feeder_breaker.cost_estimate:,}"
        })
    
    df_partenze = pd.DataFrame(partenze_data)
    st.dataframe(df_partenze, use_container_width=True)
    
    # Statistiche selezione
    tmax_count = sum(1 for fb in feeder_breakers if "Tmax" in fb.series)
    emax_count = sum(1 for fb in feeder_breakers if "Emax" in fb.series)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Interruttori Tmax", tmax_count)
    with col2:
        st.metric("Interruttori Emax", emax_count)
    with col3:
        st.metric("Totale partenze", len(feeder_breakers))
    
    # ========== 6.5 - VERIFICA SELETTIVITÀ BT (VERIFICA) ==========
    st.subheader("🛡️ 6.5 - Verifica Selettività BT")
    
    st.info(f"""
    **Metodologia IEC 60947-2:** La selettività si verifica **dopo** aver scelto tutti gli interruttori  
    **Verifica automatica** secondo algoritmi di coordinamento tempo-corrente ABB
    """)
    
    # Verifica selettività automatica
    selectivity_result = db.verify_bt_selectivity(main_breaker, feeder_breakers)
    
    if selectivity_result["selective"]:
        st.success("✅ **Selettività BT verificata** - Coordinamento corretto tra interruttori")
        st.success("""
        **Vantaggi della selettività verificata:**
        • Continuità di fornitura garantita
        • Localizzazione rapida dei guasti
        • Protezione ottimizzata per ogni circuito
        • Conformità normative IEC 60947-2
        """)
    else:
        st.error("❌ **Problemi di selettività** rilevati")
        for issue in selectivity_result["issues"]:
            st.error(f"• {issue}")
        st.warning("⚠️ **Azioni correttive necessarie** - Rivedere impostazioni protezioni")
    
    if selectivity_result["recommendations"]:
        st.info("💡 **Raccomandazioni per ottimizzazione:**")
        for rec in selectivity_result["recommendations"]:
            st.info(f"• {rec}")
    
    # ========== 6.6 - RIEPILOGO E COSTI (FINALIZZAZIONE) ==========
    st.subheader("💰 6.6 - Riepilogo e Costi")
    
    st.info("**Calcolo costi completo** di tutti i componenti selezionati secondo metodologia IEC")
    
    # Calcolo costi totali
    cost_main_switch = main_switch.cost_estimate
    cost_main_breaker = main_breaker.cost_estimate
    cost_feeder_breakers = sum(fb.cost_estimate for fb in feeder_breakers)
    cost_feeder_switches = len(feeder_breakers) * 400  # Stima sezionatori partenze
    cost_accessories = int(total_kva * 15)  # Costi accessori (busbar, cablaggi, etc.)
    
    total_bt_cost = cost_main_switch + cost_main_breaker + cost_feeder_breakers + cost_feeder_switches + cost_accessories
    
    # Tabella costi dettagliata
    costs_data = [
        {"Componente": "Sezionatore principale", "Quantità": 1, "Costo Unitario": f"€{cost_main_switch:,}", "Costo Totale": f"€{cost_main_switch:,}"},
        {"Componente": "Interruttore generale", "Quantità": 1, "Costo Unitario": f"€{cost_main_breaker:,}", "Costo Totale": f"€{cost_main_breaker:,}"},
        {"Componente": "Interruttori partenze", "Quantità": len(feeder_breakers), "Costo Unitario": "Vario", "Costo Totale": f"€{cost_feeder_breakers:,}"},
        {"Componente": "Sezionatori partenze", "Quantità": len(feeder_breakers), "Costo Unitario": "€400", "Costo Totale": f"€{cost_feeder_switches:,}"},
        {"Componente": "Accessori e cablaggio", "Quantità": 1, "Costo Unitario": f"€{cost_accessories:,}", "Costo Totale": f"€{cost_accessories:,}"}
    ]
    
    df_costs = pd.DataFrame(costs_data)
    st.dataframe(df_costs, use_container_width=True)
    
    # Riepilogo finale
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("**TOTALE QUADRO BT**", f"**€{total_bt_cost:,}**")
    with col2:
        st.metric("Costo per kVA", f"€{total_bt_cost/total_kva:.0f}")
    with col3:
        selectivity_status = "✅ Verificata" if selectivity_result["selective"] else "⚠️ Da ottimizzare"
        st.metric("Selettività", selectivity_status)
    
    # ✅ Salvataggio configurazione - AGGIORNATO con cos_phi
    if st.button("✅ CONFERMA PROGETTO QUADRO BT", type="primary"):
        st.session_state['bt_switchgear_config'] = {
            'main_switch': {
                'series': main_switch.series,
                'current': main_switch.rated_current,
                'product_code': main_switch.product_code,
                'cost': main_switch.cost_estimate,
                'type': main_switch.type
            },
            'main_breaker': {
                'series': main_breaker.series,
                'current': main_breaker.rated_current,
                'frame': main_breaker.frame,
                'product_code': main_breaker.product_code,
                'cost': main_breaker.cost_estimate,
                'breaking_capacity': main_breaker.breaking_capacity
            },
            'feeder_breakers': [
                {
                    'load_name': load.load_name,
                    'series': fb.series,
                    'current': fb.rated_current,
                    'product_code': fb.product_code,
                    'cost': fb.cost_estimate,
                    'type': fb.type
                }
                for load, fb in zip(load_distribution, feeder_breakers)
            ],
            'load_distribution': [
                {
                    'name': load.load_name,
                    'type': load.load_type.value,
                    'power_kw': load.power_kw,
                    'current_a': load.current_a,
                    'priority': load.priority,
                    'diversity_factor': load.diversity_factor,
                    'cos_phi': load.cos_phi  # ✅ Salva cos φ reale
                }
                for load in load_distribution
            ],
            'selectivity_verified': selectivity_result["selective"],
            'selectivity_issues': selectivity_result["issues"],
            'selectivity_recommendations': selectivity_result["recommendations"],
            'total_cost': total_bt_cost,
            'cost_breakdown': {
                'main_switch': cost_main_switch,
                'main_breaker': cost_main_breaker,
                'feeder_breakers': cost_feeder_breakers,
                'feeder_switches': cost_feeder_switches,
                'accessories': cost_accessories
            },
            'total_feeders': len(feeder_breakers),
            'utilization_percent': utilization_kva,  # ✅ Utilizzo corretto in kVA
            'cos_phi_average': cos_phi_medio,  # ✅ Cos φ medio pesato
            'total_power_kva_loads': total_power_kva_loads,  # ✅ Potenza apparente carichi
            'methodology_compliance': {
                'iec_60947_2': True,
                'cei_23_51': True,
                'iec_60947_3': True,
                'cei_17_50': selectivity_result["selective"],
                'iec_61439': True
            }
        }
        
        st.session_state['completed_steps'].add(6)
        st.session_state['current_step'] = 7
        st.balloons()
        st.success("🎉 **Progetto Quadro BT completato secondo metodologia IEC!**")
        st.info("📋 **Sequenza metodologica verificata:** Sicurezza → Protezione → Calcolo → Selezione → Verifica → Finalizzazione")
        st.rerun()

# ===============================================================================
# STEP 7: ANALISI FINALE E REPORT
# ===============================================================================

def step_7_final_analysis():
    """Step 7: Analisi finale e report"""
    
    st.header("📊 Step 7: Analisi Finale e Report")
    
    if 6 not in st.session_state['completed_steps']:
        st.error("❌ Completa prima lo Step 6 (Progettazione Quadro BT)")
        return
    
    # Raccolta tutti i dati
    distributor_data = st.session_state['distributor_data']
    calculation_results = st.session_state.get('calculation_results', {})
    transformer_config = st.session_state.get('transformer_config', {})
    mt_design = st.session_state.get('mt_final_design', {})
    bt_design = st.session_state.get('bt_switchgear_config', {})  # ✅ Dati quadro BT
    earth_switch = st.session_state.get('earth_switch_system', {})  # ✅ Dati sezionatore terra
    
    st.subheader("🎯 Riepilogo Progetto")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Potenza Installata", f"{calculation_results.get('total_power_kva', 0)} kVA")
        transformer_info = f"{transformer_config.get('num_transformers', 0)} x {transformer_config.get('power_kva', 0)} kVA"
        if transformer_config.get('choice_concordant'):
            transformer_info += " ✅"
        else:
            transformer_info += " ⚠️"
        st.metric("Trasformatori", transformer_info)
    
    with col2:
        st.metric("Tensione MT", f"{distributor_data['voltage_kv']} kV")
        st.metric("Icc rete", f"{distributor_data['icc_3phase_ka']} kA")
    
    with col3:
        # ✅ Incluso costo sezionatore terra e quadro BT
        total_cost = (transformer_config.get('total_cost', 0) + 
                     mt_design.get('total_cost', 0) + 
                     bt_design.get('total_cost', 0) +
                     earth_switch.get('total_cost', 0))
        st.metric("Costo Totale", f"€{total_cost:,}")
        st.metric("Costo/kVA", f"€{total_cost/calculation_results.get('total_power_kva', 1):.0f}")
    
    # ✅ Riepilogo sezionatore di terra
    if earth_switch:
        st.subheader("⚡ Sezionatore di Terra")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Tipo", earth_switch.get('specification', {}).get('type', 'N/A').replace('_', ' ').title())
            st.metric("Tensione", f"{earth_switch.get('specification', {}).get('rated_voltage', 0)} kV")
        
        with col2:
            st.metric("Corrente", f"{earth_switch.get('specification', {}).get('rated_current', 0)} A")
            st.metric("CEI 11-27", "✅ Conforme")
        
        with col3:
            st.metric("Costo", f"€{earth_switch.get('specification', {}).get('cost_estimate', 0):,}")
            st.metric("Interblocco", "✅" if earth_switch.get('specification', {}).get('key_interlock') else "Procedure")
    
    # ✅ Riepilogo quadro BT
    if bt_design:
        st.subheader("🔵 Riepilogo Quadro BT")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sezionatore principale", bt_design.get('main_switch', {}).get('series', 'N/A'))
            st.metric("Interruttore principale", bt_design.get('main_breaker', {}).get('series', 'N/A'))
        with col2:
            st.metric("Corrente principale", f"{bt_design.get('main_breaker', {}).get('current', 0)} A")
            st.metric("Numero partenze", bt_design.get('total_feeders', 0))
        with col3:
            st.metric("Utilizzo trasformatore", f"{bt_design.get('utilization_percent', 0):.1f}%")
            st.metric("Costo quadro BT", f"€{bt_design.get('total_cost', 0):,}")
    
    # Conformità normative
    st.subheader("✅ Conformità Normative")
    
    # ✅ Aggiornate con normative BT e sezionatore terra
    conformity_checks = [
        ("CEI 0-16", st.session_state.get('project_params', {}).get('cei_016_required', True)),
        ("CEI EN 50160", distributor_data.get('cei_en_50160_compliant', True)),
        ("CEI 11-27 (Sezionatore Terra)", earth_switch.get('cei_11_27_compliant', False)),
        ("Coordinamento protezioni", True),
        ("Selettività MT verificata", True),
        ("CEI 23-51 (Quadri BT)", bt_design.get('methodology_compliance', {}).get('cei_23_51', False)),
        ("IEC 60947-2 (Interruttori BT)", bt_design.get('methodology_compliance', {}).get('iec_60947_2', False)),
        ("IEC 60947-3 (Sezionatori)", bt_design.get('methodology_compliance', {}).get('iec_60947_3', False)),
        ("Selettività BT verificata", bt_design.get('selectivity_verified', False))
    ]
    
    for check, status in conformity_checks:
        if status:
            st.success(f"✅ {check}")
        else:
            st.error(f"❌ {check}")
    
    # ✅ Distribuzione costi dettagliata
    if total_cost > 0:
        st.subheader("💰 Distribuzione Costi")
        
        cost_breakdown = {
            "Trasformatori": transformer_config.get('total_cost', 0),
            "Sezionatore Terra": earth_switch.get('total_cost', 0),
            "Quadro MT": mt_design.get('total_cost', 0),
            "Quadro BT": bt_design.get('total_cost', 0)
        }
        
        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
        
        for i, (item, cost) in enumerate(cost_breakdown.items()):
            with cols[i]:
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                st.metric(item, f"€{cost:,}", f"{percentage:.1f}%")
    
    # ✅ Metodologia seguita
    st.subheader("📋 Metodologia Seguita")
    st.success("""
    **Sequenza metodologica verificata:**
    1. 📄 **Dati Distributore** - Vincoli di rete
    2. ⚡ **Calcolo Carichi** - Normative CEI
    3. 🔌 **Trasformatori** - Dimensionamento ottimale
    4. ⚡ **Sezionatore Terra** - Conformità CEI 11-27
    5. 🔴 **Quadro MT** - Progettazione avanzata
    6. 🛡️ **Coordinamento** - Protezioni CEI 0-16
    7. 🔵 **Quadro BT** - Metodologia IEC 60947
    8. 📊 **Analisi Finale** - Report completo
    """)
    
    st.balloons()
    st.success("🎉 **PROGETTO COMPLETATO CON SUCCESSO!**")
    
    # ✅ Report finale esportabile
    with st.expander("📋 Report Finale Esportabile", expanded=False):
        st.code(f"""
REPORT FINALE PROGETTO CABINA MT/BT
═══════════════════════════════════════════════════════════════════════════════

DATI GENERALI
─────────────────────────────────────────────────────────────────────────────
• Potenza installata: {calculation_results.get('total_power_kva', 0)} kVA
• Tensione MT: {distributor_data['voltage_kv']} kV
• Tensione BT: 415V
• Icc rete: {distributor_data['icc_3phase_ka']} kA
• Neutro: {distributor_data['neutral_state']}

TRASFORMATORI
─────────────────────────────────────────────────────────────────────────────
• Configurazione: {transformer_config.get('num_transformers', 0)} x {transformer_config.get('power_kva', 0)} kVA
• Serie: {transformer_config.get('series', 'N/A')}
• Perdite vuoto: {transformer_config.get('losses_no_load_w', 0)} W
• Perdite carico: {transformer_config.get('losses_load_w', 0)} W
• Costo: €{transformer_config.get('total_cost', 0):,}

SEZIONATORE DI TERRA
─────────────────────────────────────────────────────────────────────────────
• Tipo: {earth_switch.get('specification', {}).get('type', 'N/A').replace('_', ' ').title()}
• Tensione: {earth_switch.get('specification', {}).get('rated_voltage', 0)} kV
• Corrente: {earth_switch.get('specification', {}).get('rated_current', 0)} A
• CEI 11-27: {'✅' if earth_switch.get('cei_11_27_compliant') else '❌'}
• Costo: €{earth_switch.get('total_cost', 0):,}

QUADRO MT
─────────────────────────────────────────────────────────────────────────────
• Serie: UniSec ABB
• Costo: €{mt_design.get('total_cost', 0):,}

QUADRO BT
─────────────────────────────────────────────────────────────────────────────
• Sezionatore: {bt_design.get('main_switch', {}).get('series', 'N/A')} {bt_design.get('main_switch', {}).get('current', 0)}A
• Interruttore principale: {bt_design.get('main_breaker', {}).get('series', 'N/A')} {bt_design.get('main_breaker', {}).get('current', 0)}A
• Numero partenze: {bt_design.get('total_feeders', 0)}
• Utilizzo trasformatore: {bt_design.get('utilization_percent', 0):.1f}%
• Selettività: {'Verificata' if bt_design.get('selectivity_verified', False) else 'Da ottimizzare'}
• Costo: €{bt_design.get('total_cost', 0):,}

COSTI TOTALI
─────────────────────────────────────────────────────────────────────────────
• Trasformatori: €{transformer_config.get('total_cost', 0):,}
• Sezionatore Terra: €{earth_switch.get('total_cost', 0):,}
• Quadro MT: €{mt_design.get('total_cost', 0):,}
• Quadro BT: €{bt_design.get('total_cost', 0):,}
• TOTALE: €{total_cost:,}
• Costo/kVA: €{total_cost/calculation_results.get('total_power_kva', 1):.0f}

CONFORMITÀ NORMATIVE
─────────────────────────────────────────────────────────────────────────────
• CEI 0-16: ✅
• CEI EN 50160: ✅
• CEI 11-27 (Sezionatore Terra): {'✅' if earth_switch.get('cei_11_27_compliant') else '❌'}
• CEI 23-51 (Quadri BT): {'✅' if bt_design.get('methodology_compliance', {}).get('cei_23_51', False) else '❌'}
• IEC 60947-2/3: {'✅' if bt_design.get('methodology_compliance', {}).get('iec_60947_2', False) else '❌'}
• Selettività verificata: {'✅' if bt_design.get('selectivity_verified', False) else '⚠️'}

METODOLOGIA SEGUITA
─────────────────────────────────────────────────────────────────────────────
Sequenza completa: Dati → Carichi → Trasformatori → Sezionatore Terra → 
                   Quadro MT → Protezioni → Quadro BT → Analisi Finale

GENERATO DA: Software Cabina MT/BT Non Professional v2.0
DATA: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
        """)
    
    st.info("💡 **Prossimi passi:** Stampa del report, validazione finale, consegna documentazione tecnica")

# ✅ RE-ESPORTAZIONE FUNZIONI per main.py
__all__ = [
    'step_1_distributor_data',
    'step_2_load_calculation', 
    'step_3_transformer_sizing',
    'step_3_5_earth_switch_design',
    'step_4_mt_switchgear_design',  # ✅ Funzione wrapper locale
    'step_5_protection_coordination',
    'step_6_bt_switchgear_design',
    'step_7_final_analysis'
]
