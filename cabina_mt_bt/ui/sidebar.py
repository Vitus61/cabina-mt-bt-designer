"""
UI Sidebar - Gestione input dati di progetto + INTEGRAZIONE REPORT
"""

import streamlit as st
from calculations.loads import SimpleLoad
from datetime import datetime

# Import per report generation
try:
    from report.generators.relazione_tecnica_completa import genera_relazione_da_main
    REPORT_AVAILABLE = True
except ImportError:
    REPORT_AVAILABLE = False

def render_sidebar():
    """Sidebar per input dati di progetto"""
    
    st.sidebar.header("📄 DATI DISTRIBUTORE")
    
    # Tensione nominale
    voltage = st.sidebar.number_input(
        "Tensione nominale (kV)", 
        value=st.session_state['distributor_data']['voltage_kv'],
        min_value=10.0, max_value=36.0, step=0.5
    )
    st.session_state['distributor_data']['voltage_kv'] = voltage
    
    # Corrente cortocircuito
    icc = st.sidebar.number_input(
        "Icc trifase (kA)", 
        value=st.session_state['distributor_data']['icc_3phase_ka'],
        min_value=5.0, max_value=50.0, step=0.5
    )
    st.session_state['distributor_data']['icc_3phase_ka'] = icc
    
    # Stato neutro
    neutral = st.sidebar.selectbox(
        "Stato del neutro",
        options=['compensato', 'isolato', 'a terra'],
        index=['compensato', 'isolato', 'a terra'].index(st.session_state['distributor_data']['neutral_state'])
    )
    st.session_state['distributor_data']['neutral_state'] = neutral
    
    # Corrente guasto terra
    earth_current = st.sidebar.number_input(
        "Corrente guasto terra (A)", 
        value=st.session_state['distributor_data']['earth_fault_current_a'],
        min_value=1, max_value=500, step=1
    )
    st.session_state['distributor_data']['earth_fault_current_a'] = earth_current
    
    # Tempi eliminazione
    earth_time = st.sidebar.number_input(
        "Tempo eliminazione guasto terra (s)", 
        value=st.session_state['distributor_data']['earth_fault_time_s'],
        min_value=1.0, max_value=30.0, step=0.5
    )
    st.session_state['distributor_data']['earth_fault_time_s'] = earth_time
    
    st.sidebar.markdown("---")
    st.sidebar.header("⚡ CARICHI ELETTRICI")
    
    # Input carichi semplificato
    if st.sidebar.button("➕ Aggiungi Carico"):
        st.session_state['loads'].append(
            SimpleLoad("Nuovo Carico", "motori", 50, 1, 0.8, 0.85)
        )
        st.rerun()
    
    if st.sidebar.button("🗑️ Cancella e Ritorna alla Home"):
        # Reset completo del progetto
        st.session_state['loads'] = []
        st.session_state['current_step'] = 1
        st.session_state['completed_steps'] = set()
    
        # Cancella tutti i risultati di calcolo
        st.session_state['calculation_results'] = None
        st.session_state['transformer_config'] = None
        st.session_state['earth_switch_system'] = None
        st.session_state['mt_final_design'] = None
        st.session_state['bt_switchgear_config'] = None
        st.session_state['protection_coordination'] = None
    
        st.sidebar.success("🔄 Reset completo effettuato!")
        st.rerun()
        
        
    
    if st.sidebar.button("📋 Carica Esempio"):
        st.session_state['loads'] = [
            SimpleLoad("Motori Produzione", "motori", 150, 3, 0.8, 0.85),
            SimpleLoad("Illuminazione", "illuminazione", 25, 1, 1.0, 0.9),
            SimpleLoad("Prese Uffici", "prese", 50, 1, 1.0, 0.8),
            SimpleLoad("Climatizzazione", "riscaldamento", 40, 1, 0.9, 0.85),
        ]
        st.rerun()
    
    # Mostra numero carichi
    st.sidebar.metric("Carichi inseriti", len(st.session_state['loads']))
    
    st.sidebar.markdown("---")
    st.sidebar.header("🔧 PARAMETRI PROGETTO")
    
    # Tipo installazione
    installation = st.sidebar.selectbox(
        "Tipo installazione",
        options=['indoor', 'outdoor'],
        index=['indoor', 'outdoor'].index(st.session_state['project_params']['installation_type'])
    )
    st.session_state['project_params']['installation_type'] = installation
    
    # Continuità servizio
    continuity = st.sidebar.selectbox(
        "Continuità servizio",
        options=['normale', 'privilegiata', 'essenziale'],
        index=['normale', 'privilegiata', 'essenziale'].index(st.session_state['project_params']['service_continuity'])
    )
    st.session_state['project_params']['service_continuity'] = continuity
    
    # ✅ Ripristinata checkbox ridondanza trasformatori
    redundancy = st.sidebar.checkbox(
        "🔄 Ridondanza Trasformatori",
        value=st.session_state['project_params']['transformer_redundancy'],
        help="Due trasformatori in parallelo per maggiore continuità di servizio"
    )
    st.session_state['project_params']['transformer_redundancy'] = redundancy
    
    # CEI 0-16
    cei_016 = st.sidebar.checkbox(
        "Conformità CEI 0-16",
        value=st.session_state['project_params']['cei_016_required']
    )
    st.session_state['project_params']['cei_016_required'] = cei_016

    # ===== NUOVA SEZIONE REPORT =====
    st.sidebar.markdown("---")
    st.sidebar.header("📊 GENERAZIONE REPORT")
    
    # Controlla se ci sono dati di calcolo disponibili
    has_calculation_results = (
        st.session_state.get('calculation_results') is not None and
        st.session_state.get('transformer_config') is not None
    )
    
    if not REPORT_AVAILABLE:
        st.sidebar.error("❌ Moduli report non disponibili")
        return
    
    if not has_calculation_results:
        st.sidebar.warning("⚠️ Eseguire prima i calcoli della cabina")
        return
    
    # Input informazioni progetto per report
    with st.sidebar.expander("📋 Info Progetto", expanded=False):
        cliente = st.text_input("Cliente:", key="report_cliente", 
                               help="Nome del cliente o azienda")
        commessa = st.text_input("Commessa:", key="report_commessa",
                                help="Numero commessa o codice progetto") 
        ubicazione = st.text_input("Ubicazione:", key="report_ubicazione",
                                  help="Località di installazione")
        progettista = st.text_input("Progettista:", value="Ing. Maurizio", 
                                   key="report_progettista")
        
    # Pulsante generazione report
    if st.sidebar.button("📄 Genera Relazione Tecnica", key="genera_report_sidebar"):
        if cliente and commessa and ubicazione:
            genera_report_completo(cliente, commessa, ubicazione, progettista)
        else:
            st.sidebar.error("❌ Compilare Cliente, Commessa e Ubicazione")


def genera_report_completo(cliente, commessa, ubicazione, progettista):
    """Genera il report completo dalla sidebar"""
    
    try:
        with st.sidebar:
            # Progress bar
            progress = st.progress(0)
            status = st.empty()
            
            status.text("🔄 Preparazione dati...")
            progress.progress(25)
            
            # Crea oggetto dati progetto
            info_progetto = {
                'cliente': cliente,
                'commessa': commessa,
                'ubicazione': ubicazione, 
                'progettista': progettista,
                'revisione': '00',
                'data_progetto': datetime.now().strftime("%d/%m/%Y")
            }
            
            status.text("📊 Estrazione dati di calcolo...")
            progress.progress(50)
            
            # Crea oggetto "cabina" dai dati di session_state
            cabina_obj = CreaOggettoCabinaDaSessionState()
            
            status.text("📄 Generazione PDF...")
            progress.progress(75)
            
            # Genera il report
            pdf_file = genera_relazione_da_main(cabina_obj, info_progetto)
            
            status.text("✅ Completato!")
            progress.progress(100)
            
            # Rimuovi progress dopo successo
            progress.empty()
            status.empty()
            
            # Mostra successo
            st.success("✅ Relazione tecnica generata!")
            
            # Download button
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="📥 Scarica PDF",
                    data=file.read(),
                    file_name=f"Relazione_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="download_report_sidebar"
                )
            
            # Info sul file
            import os
            file_size = os.path.getsize(pdf_file) / 1024  # KB
            st.info(f"📄 Dimensione: {file_size:.1f} KB")
            
    except Exception as e:
        st.sidebar.error(f"❌ Errore generazione report: {str(e)}")
        # Debug info
        with st.sidebar.expander("🔍 Debug Info", expanded=False):
            st.write("Session State disponibile:")
            st.write({
                'calculation_results': bool(st.session_state.get('calculation_results')),
                'transformer_config': bool(st.session_state.get('transformer_config')),
                'loads': len(st.session_state.get('loads', [])),
                'distributor_data': bool(st.session_state.get('distributor_data'))
            })


def CreaOggettoCabinaDaSessionState():
    """Crea oggetto compatibile con report generator dai dati session_state"""
    
    class CabinaReport:
        def __init__(self):
            # DATI DISTRIBUTORE
            distributor = st.session_state.get('distributor_data', {})
            self.tensione_mt = distributor.get('voltage_kv', 20)
            self.tensione_bt = 400  # Standard BT
            
            # DATI CALCOLO CARICHI
            calc_results = st.session_state.get('calculation_results', {})
            self.potenza_installata = calc_results.get('total_power_kw', 0)
            
            # CONFIGURAZIONE TRASFORMATORE
            transformer_config = st.session_state.get('transformer_config', {})
            self.potenza_trasformatore = transformer_config.get('power_kva', self.potenza_installata)
            
            # CORRENTI CALCOLATE (se disponibili dai calcoli)
            if self.potenza_trasformatore and self.tensione_mt:
                self.corrente_nominale_mt = round(self.potenza_trasformatore / (1.732 * self.tensione_mt), 1)
            else:
                self.corrente_nominale_mt = 'N/A'
                
            if self.potenza_trasformatore:
                self.corrente_nominale_bt = round(self.potenza_trasformatore / (1.732 * self.tensione_bt * 1000) * 1000000, 1)
            else:
                self.corrente_nominale_bt = 'N/A'
            
            # CORTOCIRCUITI
            self.icc_mt_max = distributor.get('icc_3phase_ka', 25)
            self.icc_mt_min = self.icc_mt_max * 0.8  # Stima conservativa
            
            # Calcolo approssimativo Icc BT (da affinare con calcoli reali se disponibili)
            if hasattr(self, 'potenza_trasformatore') and self.potenza_trasformatore:
                # Formula semplificata per Icc BT
                vcc_percent = 4  # 4% standard per trasformatori in resina
                self.icc_bt_max = round((self.potenza_trasformatore * 100) / (vcc_percent * self.tensione_bt * 1.732), 1)
                self.icc_bt_min = self.icc_bt_max * 0.5  # A fondo linea stimato
            else:
                self.icc_bt_max = 'N/A'
                self.icc_bt_min = 'N/A'
            
            # PARAMETRI DI PROGETTO
            project_params = st.session_state.get('project_params', {})
            self.sistema_distribuzione = "TT"  # Standard per cabine private
            self.lunghezza_cavo_bt = 50  # Valore tipico - da parametrizzare se necessario
            
            # DATI TRASFORMATORE
            self.tipo_trasformatore = "Resina"  # Standard per cabine private
            self.tensione_cortocircuito = "4%"   # Standard per trasformatori in resina
            self.perdite_vuoto = round(self.potenza_trasformatore * 0.3, 0) if self.potenza_trasformatore else 'N/A'  # Stima
            self.perdite_carico = round(self.potenza_trasformatore * 0.8, 0) if self.potenza_trasformatore else 'N/A'  # Stima
            
            # APPARECCHIATURE MT (da configurazioni reali se disponibili)
            mt_design = st.session_state.get('mt_final_design', {})
            self.interruttore_mt_selezionato = {
                'marca': 'ABB',
                'modello': 'VD4',
                'corrente_nominale': 630,  # Standard per cabine MT
                'potere_interruzione': max(25, self.icc_mt_max * 1.2)  # Margine di sicurezza
            }
            
            # APPARECCHIATURE BT (da configurazioni reali se disponibili)
            bt_config = st.session_state.get('bt_switchgear_config', {})
            self.interruttore_bt_selezionato = {
                'marca': 'ABB',
                'modello': 'E6V', 
                'corrente_nominale': 1600,  # Da dimensionare in base alla corrente BT
                'potere_interruzione': 50   # Standard per interruttori BT
            }
            
            # PROTEZIONI (da configurazioni reali se disponibili)
            protection_config = st.session_state.get('protection_coordination', {})
            self.taratura_51 = round(self.corrente_nominale_mt * 1.25, 1) if isinstance(self.corrente_nominale_mt, (int, float)) else 'N/A'
            self.taratura_50 = round(self.corrente_nominale_mt * 10, 1) if isinstance(self.corrente_nominale_mt, (int, float)) else 'N/A'
            self.taratura_51N = round(self.corrente_nominale_mt * 0.2, 1) if isinstance(self.corrente_nominale_mt, (int, float)) else 'N/A'
            
            # IMPIANTO DI TERRA (valori tipici - da personalizzare)
            self.resistivita_terreno = 100  # Ω·m (valore medio)
            self.resistenza_terra_calcolata = 1.0  # Ω (da calcoli reali)
            self.sezione_dispersore = 50  # mm² (standard)
            
    return CabinaReport()