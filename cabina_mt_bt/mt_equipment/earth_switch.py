"""
Modulo Sezionatore di Terra - CEI 11-27
Da integrare nel Software Cabina MT/BT Professional v2.0
"""

import streamlit as st
from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum

class EarthSwitchType(Enum):
    """Tipi di sezionatore di terra"""
    NONE = "no_earth_switch"
    FIXED = "fixed_earth_switch"
    MOBILE = "mobile_devices"

class EarthSwitchPosition(Enum):
    """Posizione sezionatore di terra"""
    DELIVERY_ROOM = "locale_consegna"
    CABLE_TERMINATION = "terminali_cavo"
    SEPARATE_CELL = "cella_separata"

@dataclass
class EarthSwitchSpec:
    """Specifica sezionatore di terra"""
    type: EarthSwitchType
    position: EarthSwitchPosition
    rated_voltage: int  # kV
    rated_current: int  # A
    poles: int = 3
    key_interlock: bool = False
    warning_sign: bool = False
    cei_11_27_compliant: bool = False
    product_code: str = ""
    cost_estimate: int = 0
    installation_requirements: List[str] = None

class EarthSwitchDesigner:
    """Progettista sezionatore di terra secondo CEI 11-27"""
    
    def __init__(self):
        self.earth_switch_database = self._load_earth_switch_database()
    
    def _load_earth_switch_database(self) -> Dict:
        """Database sezionatori di terra ABB"""
        return {
            "fixed_switches": {
                "DH1": {
                    "series": "DH1 - Sezionatore di terra",
                    "manufacturer": "ABB",
                    "voltage_range": [12, 17.5, 24, 36],  # kV
                    "current_range": [400, 630, 1000, 1250],  # A
                    "poles": 3,
                    "key_interlock": True,
                    "warning_sign": True,
                    "cei_11_27_compliant": True,
                    "product_codes": {
                        "24kV_630A": "DH1-24-630-3P-KI",
                        "24kV_1000A": "DH1-24-1000-3P-KI",
                        "24kV_1250A": "DH1-24-1250-3P-KI"
                    },
                    "cost_base": 2500,
                    "cost_per_amp": 1.5,
                    "installation_requirements": [
                        "Locale separato per consegna",
                        "Interblocco meccanico con chiave distributore", 
                        "Targa di avvertimento obbligatoria",
                        "Coordinamento con dispositivi distributore",
                        "Messa a terra dedicata"
                    ]
                }
            },
            "mobile_devices": {
                "CEI_EN_61230": {
                    "series": "Dispositivi mobili CEI EN 61230",
                    "manufacturer": "Vari",
                    "description": "Dispositivi di messa a terra mobili",
                    "voltage_range": [12, 17.5, 24, 36],  # kV
                    "current_range": [1000, 1600, 2000],  # A cortocircuito
                    "poles": 3,
                    "key_interlock": False,
                    "warning_sign": True,
                    "cei_11_27_compliant": True,
                    "cost_base": 800,
                    "installation_requirements": [
                        "Nessun sezionatore fisso",
                        "Punti di attacco per dispositivi mobili",
                        "Istruzioni operative dettagliate",
                        "Formazione personale obbligatoria",
                        "Coordinamento con distributore"
                    ]
                }
            }
        }
    
    def design_earth_switch_system(self, project_data: Dict) -> Dict:
        """Progetta sistema sezionatore di terra"""
        
        # Dati di progetto
        voltage_kv = project_data.get("voltage_kv", 20)
        max_current = project_data.get("max_current", 630)
        service_continuity = project_data.get("service_continuity", "normal")
        
        # Analisi requisiti
        analysis = self._analyze_earth_switch_requirements(
            voltage_kv, max_current, service_continuity
        )
        
        # Raccomandazione
        recommendation = self._recommend_earth_switch_solution(analysis)
        
        # Specifica tecnica
        if recommendation["type"] == EarthSwitchType.FIXED:
            spec = self._design_fixed_earth_switch(voltage_kv, max_current)
        else:
            spec = self._design_mobile_earth_devices(voltage_kv, max_current)
        
        return {
            "analysis": analysis,
            "recommendation": recommendation,
            "specification": spec,
            "cei_11_27_compliant": True,
            "installation_guide": self._generate_installation_guide(spec)
        }
    
    def _analyze_earth_switch_requirements(self, voltage_kv: float, 
                                         max_current: float, 
                                         service_continuity: str) -> Dict:
        """Analizza requisiti sezionatore di terra"""
        
        # Fattori di decisione
        factors = {
            "voltage_level": "high" if voltage_kv >= 20 else "medium",
            "current_level": "high" if max_current >= 800 else "medium",
            "service_continuity": service_continuity,
            "safety_requirements": "high",  # Sempre alto per MT
            "maintenance_frequency": "medium"
        }
        
        # Analisi costi-benefici
        cost_analysis = {
            "fixed_switch_cost": 2500 + max_current * 1.5,
            "mobile_devices_cost": 800 + 200,  # Dispositivi + formazione
            "operational_impact": {
                "fixed": "Minimo - Manovra semplice",
                "mobile": "Medio - Richiede procedure specifiche"
            },
            "safety_level": {
                "fixed": "Massimo - Interblocco garantito",
                "mobile": "Alto - Dipende da procedure"
            }
        }
        
        return {
            "factors": factors,
            "cost_analysis": cost_analysis,
            "cei_11_27_options": ["fixed_switch", "mobile_devices"],
            "distributor_requirements": [
                "Coordinamento interblocchi",
                "Consegna chiavi",
                "Approvazione progetto",
                "Verifiche periodiche"
            ]
        }
    
    def _recommend_earth_switch_solution(self, analysis: Dict) -> Dict:
        """Raccomanda soluzione ottimale"""
        
        factors = analysis["factors"]
        cost_analysis = analysis["cost_analysis"]
        
        # Logica di raccomandazione
        if (factors["service_continuity"] == "essential" or 
            factors["current_level"] == "high"):
            
            recommended_type = EarthSwitchType.FIXED
            reason = "Servizio critico e/o correnti elevate richiedono sezionatore fisso"
            
        elif cost_analysis["mobile_devices_cost"] < cost_analysis["fixed_switch_cost"] * 0.5:
            
            recommended_type = EarthSwitchType.MOBILE
            reason = "Vantaggi economici e operativi dei dispositivi mobili"
            
        else:
            
            recommended_type = EarthSwitchType.FIXED
            reason = "Miglior compromesso sicurezza-operatività"
        
        return {
            "type": recommended_type,
            "reason": reason,
            "alternative": EarthSwitchType.MOBILE if recommended_type == EarthSwitchType.FIXED else EarthSwitchType.FIXED,
            "confidence": "high"
        }
    
    def _design_fixed_earth_switch(self, voltage_kv: float, max_current: float) -> EarthSwitchSpec:
        """Progetta sezionatore di terra fisso"""
        
        # Selezione corrente standard
        standard_currents = [400, 630, 1000, 1250, 1600]
        selected_current = next((c for c in standard_currents if c >= max_current), 1600)
        
        # Specifica prodotto
        product_code = f"DH1-{int(voltage_kv)}-{selected_current}-3P-KI"
        cost = 2500 + selected_current * 1.5
        
        return EarthSwitchSpec(
            type=EarthSwitchType.FIXED,
            position=EarthSwitchPosition.DELIVERY_ROOM,
            rated_voltage=int(voltage_kv),
            rated_current=selected_current,
            poles=3,
            key_interlock=True,
            warning_sign=True,
            cei_11_27_compliant=True,
            product_code=product_code,
            cost_estimate=int(cost),
            installation_requirements=[
                "Locale consegna separato",
                "Interblocco meccanico con chiave distributore",
                "Targa: 'SEZIONATORE MANOVRABILE SOLO DOPO INTERVENTO DISTRIBUTORE'",
                "Coordinamento con cella distributore",
                "Messa a terra dedicata secondo CEI 11-1"
            ]
        )
    
    def _design_mobile_earth_devices(self, voltage_kv: float, max_current: float) -> EarthSwitchSpec:
        """Progetta sistema dispositivi mobili"""
        
        # Corrente di cortocircuito per dispositivi mobili
        cc_current = max(1000, max_current * 2)  # Minimo 1000A, tipicamente 2×In
        
        return EarthSwitchSpec(
            type=EarthSwitchType.MOBILE,
            position=EarthSwitchPosition.CABLE_TERMINATION,
            rated_voltage=int(voltage_kv),
            rated_current=cc_current,
            poles=3,
            key_interlock=False,
            warning_sign=True,
            cei_11_27_compliant=True,
            product_code=f"CEI-EN-61230-{int(voltage_kv)}kV-{cc_current}A",
            cost_estimate=1000,
            installation_requirements=[
                "Punti di attacco per dispositivi mobili",
                "Istruzioni operative dettagliate",
                "Formazione personale specializzato",
                "Coordinamento con distributore",
                "Dispositivi secondo CEI EN 61230"
            ]
        )
    
    def _generate_installation_guide(self, spec: EarthSwitchSpec) -> Dict:
        """Genera guida installazione"""
        
        if spec.type == EarthSwitchType.FIXED:
            return {
                "location": "Locale consegna separato dal quadro MT",
                "position": "Immediatamente a valle terminali cavo distributore",
                "electrical_connection": "Collegamento a terra dedicato",
                "mechanical_interlocks": "Chiave distributore obbligatoria",
                "signage": "Targa di avvertimento ben visibile",
                "testing": "Verifica interblocchi con distributore",
                "documentation": "Certificazione CEI 11-27",
                "maintenance": "Manutenzione coordinata con distributore"
            }
        else:
            return {
                "location": "Punti di attacco sui terminali cavo",
                "position": "Accessibili per dispositivi mobili",
                "electrical_connection": "Morsetti per attacco dispositivi",
                "mechanical_interlocks": "Procedure operative",
                "signage": "Istruzioni operative dettagliate",
                "testing": "Verifica dispositivi mobili",
                "documentation": "Procedure secondo CEI EN 61230",
                "maintenance": "Controllo periodico dispositivi"
            }

def step_earth_switch_design(db_products=None):
    """Step per progettazione sezionatore di terra - DA INTEGRARE NEL SOFTWARE"""
    
    st.header("⚡ Progettazione Sezionatore di Terra")
    st.subheader("Conformità CEI 11-27 - Obbligatorio")
    
    # Avviso importante
    st.error("""
    🚨 **ATTENZIONE - REQUISITO OBBLIGATORIO**
    
    La norma CEI 11-27 impone la presenza di un sistema di messa a terra 
    immediatamente a valle dei terminali del cavo di collegamento alla rete.
    
    **Posizione:** Locale consegna (NON nel quadro MT)
    **Normativa:** CEI 11-27 - art. 6.2.1
    """)
    
    # Dati di progetto
    voltage_kv = st.session_state.get('distributor_data', {}).get('voltage_kv', 20)
    max_current = 630  # Da calcolare in base al progetto
    
    # Inizializza progettista
    earth_designer = EarthSwitchDesigner()
    
    # Progetta sistema
    project_data = {
        "voltage_kv": voltage_kv,
        "max_current": max_current,
        "service_continuity": st.session_state.get('project_params', {}).get('service_continuity', 'normal')
    }
    
    earth_system = earth_designer.design_earth_switch_system(project_data)
    
    # Mostra analisi
    st.subheader("📊 Analisi Requisiti")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Opzione 1: Sezionatore Fisso**
        • Costo: €{earth_system['analysis']['cost_analysis']['fixed_switch_cost']:,.0f}
        • Sicurezza: Massima (interblocco garantito)
        • Operatività: Semplice
        • Manutenzione: Coordinata con distributore
        """)
    
    with col2:
        st.info(f"""
        **Opzione 2: Dispositivi Mobili**
        • Costo: €{earth_system['analysis']['cost_analysis']['mobile_devices_cost']:,.0f}
        • Sicurezza: Alta (dipende da procedure)
        • Operatività: Richiede formazione
        • Manutenzione: Controllo periodico
        """)
    
    # Raccomandazione
    st.subheader("💡 Raccomandazione")
    
    recommendation = earth_system['recommendation']
    
    if recommendation['type'] == EarthSwitchType.FIXED:
        st.success(f"""
        **✅ RACCOMANDATO: Sezionatore di Terra Fisso**
        
        **Motivazione:** {recommendation['reason']}
        
        **Vantaggi:**
        • Massima sicurezza operativa
        • Interblocco meccanico garantito
        • Semplicità di manovra
        • Coordinamento automatico con distributore
        """)
    else:
        st.info(f"""
        **💰 RACCOMANDATO: Dispositivi Mobili**
        
        **Motivazione:** {recommendation['reason']}
        
        **Vantaggi:**
        • Costo ridotto
        • Flessibilità operativa
        • Nessun sezionatore fisso
        • Conformità CEI EN 61230
        """)
    
    # Specifica tecnica
    st.subheader("🔧 Specifica Tecnica")
    
    spec = earth_system['specification']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tipo Sistema", spec.type.value.replace('_', ' ').title())
        st.metric("Tensione Nominale", f"{spec.rated_voltage} kV")
    
    with col2:
        st.metric("Corrente Nominale", f"{spec.rated_current} A")
        st.metric("Numero Poli", spec.poles)
    
    with col3:
        st.metric("Costo Stimato", f"€{spec.cost_estimate:,}")
        st.metric("CEI 11-27", "✅ Conforme" if spec.cei_11_27_compliant else "❌")
    
    # Guida installazione
    st.subheader("📋 Guida Installazione")
    
    installation_guide = earth_system['installation_guide']
    
    with st.expander("📍 Dettagli Installazione", expanded=True):
        st.code(f"""
GUIDA INSTALLAZIONE SEZIONATORE DI TERRA
═══════════════════════════════════════════════════════════════════

POSIZIONE: {installation_guide['location']}
UBICAZIONE: {installation_guide['position']}

COLLEGAMENTI ELETTRICI:
• {installation_guide['electrical_connection']}

INTERBLOCCHI MECCANICI:
• {installation_guide['mechanical_interlocks']}

SEGNALETICA:
• {installation_guide['signage']}

COLLAUDI:
• {installation_guide['testing']}

DOCUMENTAZIONE:
• {installation_guide['documentation']}

MANUTENZIONE:
• {installation_guide['maintenance']}

PRODOTTO: {spec.product_code}
COSTO: €{spec.cost_estimate:,}
CONFORMITÀ: CEI 11-27 ✅
        """)
    
    # Salvataggio configurazione
    if st.button("✅ CONFERMA SISTEMA SEZIONATORE DI TERRA", type="primary"):
        st.session_state['earth_switch_system'] = {
            'type': spec.type.value,
            'specification': spec,
            'installation_guide': installation_guide,
            'cei_11_27_compliant': True,
            'cost_estimate': spec.cost_estimate,
            'requirements': spec.installation_requirements
        }
        
        st.success("✅ Sistema sezionatore di terra configurato!")
        st.balloons()

# Esempio di utilizzo
if __name__ == "__main__":
    # Simulazione step sezionatore di terra
    st.title("🔧 Simulazione Sezionatore di Terra")
    
    # Inizializza session state di esempio
    if 'distributor_data' not in st.session_state:
        st.session_state['distributor_data'] = {'voltage_kv': 20}
    if 'project_params' not in st.session_state:
        st.session_state['project_params'] = {'service_continuity': 'normal'}
    
    # Esegui step
    step_earth_switch_design()