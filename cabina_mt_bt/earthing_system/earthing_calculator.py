"""
Calcolatore Impianto di Terra MT/BT
Conforme a CEI 11-27, CEI 64-8, CEI 99-1
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum
import math

class SoilType(Enum):
    """Tipi di terreno con resistività tipiche"""
    ARGILLA_UMIDA = "Argilla umida"
    ARGILLA_SECCA = "Argilla secca"  
    SABBIA_UMIDA = "Sabbia umida"
    SABBIA_SECCA = "Sabbia secca"
    GHIAIA_UMIDA = "Ghiaia umida"
    GHIAIA_SECCA = "Ghiaia secca"
    TERRENO_COLTIVATO = "Terreno coltivato"
    ROCCIA = "Roccia"

class GroundingConfiguration(Enum):
    """Configurazioni dispersori"""
    ANELLO_PERIMETRALE = "Anello perimetrale"
    DISPERSORI_VERTICALI = "Dispersori verticali"
    SISTEMA_MISTO = "Sistema misto"
    PIASTRA_METALLICA = "Piastra metallica"

@dataclass
class SoilData:
    """Dati del terreno"""
    soil_type: SoilType
    resistivity_ohm_m: float
    depth_m: float = 0.8
    seasonal_factor: float = 1.2  # Fattore stagionale
    
@dataclass
class GroundingRequirements:
    """Requisiti impianto di terra"""
    earth_fault_current_a: float
    fault_duration_s: float
    max_earth_resistance_ohm: float
    max_touch_voltage_v: float = 50  # CEI 64-8
    max_step_voltage_v: float = 125  # CEI 64-8
    
@dataclass
class GroundingResult:
    """Risultati calcolo impianto terra"""
    total_resistance_ohm: float
    conductor_section_mm2: float
    disperser_length_m: float
    disperser_count: int
    touch_voltage_v: float
    step_voltage_v: float
    is_compliant: bool
    total_cost_eur: int
    conductor_type: str
    configuration: GroundingConfiguration

class EarthingSystemDesigner:
    """Designer principale per impianti di terra MT/BT"""
    
    def __init__(self):
        """Inizializza il designer con database materiali"""
        self.soil_resistivity = self._load_soil_resistivity()
        self.conductor_specs = self._load_conductor_specs()
        self.disperser_specs = self._load_disperser_specs()
        
    def _load_soil_resistivity(self) -> Dict[SoilType, Tuple[float, float]]:
        """Database resistività terreni (min, max) in Ω·m"""
        return {
            SoilType.ARGILLA_UMIDA: (20, 100),
            SoilType.ARGILLA_SECCA: (100, 300),
            SoilType.SABBIA_UMIDA: (50, 200),
            SoilType.SABBIA_SECCA: (200, 1000),
            SoilType.GHIAIA_UMIDA: (100, 300),
            SoilType.GHIAIA_SECCA: (500, 2000),
            SoilType.TERRENO_COLTIVATO: (30, 150),
            SoilType.ROCCIA: (1000, 10000)
        }
    
    def _load_conductor_specs(self) -> Dict[str, Dict]:
        """Specifiche conduttori di terra secondo CEI"""
        return {
            "cu_nudo": {
                "material": "Rame nudo",
                "min_section_mt": 50,  # mm² per MT
                "min_section_bt": 25,  # mm² per BT
                "cost_per_m": 15.0,    # €/m per 50mm²
                "corrosion_resistance": "excellent"
            },
            "acciaio_zincato": {
                "material": "Acciaio zincato",
                "min_section_mt": 80,  # mm² per MT  
                "min_section_bt": 50,  # mm² per BT
                "cost_per_m": 8.0,     # €/m per 50mm²
                "corrosion_resistance": "good"
            },
            "acciaio_rivestito": {
                "material": "Acciaio rivestito rame",
                "min_section_mt": 50,  # mm² per MT
                "min_section_bt": 25,  # mm² per BT
                "cost_per_m": 12.0,    # €/m per 50mm²
                "corrosion_resistance": "excellent"
            }
        }
    
    def _load_disperser_specs(self) -> Dict[str, Dict]:
        """Specifiche dispersori secondo CEI"""
        return {
            "picchetto_acciaio": {
                "length_m": 1.5,
                "diameter_mm": 20,
                "resistance_ohm_per_m": 0.1,  # Approssimazione
                "cost_each": 25.0,
                "installation_cost": 50.0
            },
            "piastra_rame": {
                "area_m2": 1.0,
                "thickness_mm": 3,
                "resistance_ohm": 0.05,  # Per piastra standard
                "cost_each": 180.0,
                "installation_cost": 100.0
            },
            "dispersore_profondo": {
                "length_m": 3.0,
                "diameter_mm": 25,
                "resistance_ohm_per_m": 0.08,
                "cost_each": 75.0,
                "installation_cost": 150.0
            }
        }
    
    def estimate_soil_resistivity(self, soil_type: SoilType, 
                                seasonal_correction: bool = True) -> float:
        """Stima resistività terreno con correzioni stagionali"""
        
        min_res, max_res = self.soil_resistivity[soil_type]
        # Usa valore medio con tendenza conservativa (+20%)
        base_resistivity = (min_res + max_res) / 2 * 1.2
        
        if seasonal_correction:
            # Fattore stagionale per condizioni sfavorevoli
            base_resistivity *= 1.5
            
        return base_resistivity
    
    def calculate_required_resistance(self, fault_current_a: float, 
                                    max_touch_voltage_v: float = 50) -> float:
        """Calcola resistenza di terra massima ammissibile"""
        
        # CEI 64-8: Rt ≤ Uc / Ig
        # dove Uc = tensione di contatto massima, Ig = corrente di guasto
        required_resistance = max_touch_voltage_v / fault_current_a
        
        # Margine di sicurezza 20%
        return required_resistance * 0.8
    
    def calculate_conductor_section(self, fault_current_a: float, 
                                  duration_s: float,
                                  material: str = "cu_nudo") -> float:
        """Calcola sezione conduttore terra secondo CEI 11-27"""
        
        # Formula CEI: S = I × √t / k
        # dove k dipende dal materiale (rame = 143, acciaio = 78)
        
        k_values = {
            "cu_nudo": 143,
            "acciaio_zincato": 78,
            "acciaio_rivestito": 143
        }
        
        k = k_values.get(material, 143)
        calculated_section = fault_current_a * math.sqrt(duration_s) / k
        
        # Verifica sezione minima normativa
        min_section = self.conductor_specs[material]["min_section_mt"]
        
        return max(calculated_section, min_section)
    
    def calculate_ring_resistance(self, perimeter_m: float, 
                                resistivity_ohm_m: float,
                                conductor_diameter_mm: float = 10) -> float:
        """Calcola resistenza anello perimetrale"""
        
        # Formula approssimata per anello rettangolare
        # R = ρ / (2π × L) × ln(2L/a)
        # dove L = perimetro, a = raggio equivalente conduttore
        
        conductor_radius_m = conductor_diameter_mm / 2000  # mm → m
        
        if perimeter_m <= 0 or conductor_radius_m <= 0:
            return float('inf')
            
        resistance = (resistivity_ohm_m / (2 * math.pi * perimeter_m)) * \
                    math.log(2 * perimeter_m / conductor_radius_m)
        
        return resistance
    
    def calculate_vertical_dispersers(self, target_resistance_ohm: float,
                                   resistivity_ohm_m: float,
                                   disperser_length_m: float = 1.5) -> int:
        """Calcola numero dispersori verticali necessari"""
        
        # Resistenza singolo dispersore verticale
        # R = ρ / (2π × L)
        single_resistance = resistivity_ohm_m / (2 * math.pi * disperser_length_m)
        
        # Numero dispersori (con fattore efficienza 0.7 per mutua induttanza)
        efficiency_factor = 0.7
        n_dispersers = single_resistance / (target_resistance_ohm * efficiency_factor)
        
        return max(2, int(math.ceil(n_dispersers)))  # Minimo 2 dispersori
    
    def verify_touch_step_voltages(self, earth_resistance_ohm: float,
                                 fault_current_a: float,
                                 surface_resistivity_ohm_m: float = 3000) -> Tuple[float, float]:
        """Verifica tensioni di passo e contatto"""
        
        # Tensione totale verso terra
        earth_voltage = earth_resistance_ohm * fault_current_a
        
        # Tensione di contatto (approssimazione conservativa)
        # Considera fattori di riduzione per configurazione impianto
        touch_voltage = earth_voltage * 0.3  # Fattore tipico per impianti ben progettati
        
        # Tensione di passo (generalmente inferiore a quella di contatto)
        step_voltage = earth_voltage * 0.2
        
        return touch_voltage, step_voltage
    
    def design_earthing_system(self, 
                             soil_data: SoilData,
                             requirements: GroundingRequirements,
                             cabin_dimensions: Tuple[float, float],  # lunghezza, larghezza
                             preferred_config: GroundingConfiguration = None) -> GroundingResult:
        """Progetta sistema completo di terra"""
        
        length_m, width_m = cabin_dimensions
        perimeter_m = 2 * (length_m + width_m)
        
        # Calcola resistività effettiva con fattori di correzione
        effective_resistivity = soil_data.resistivity_ohm_m * soil_data.seasonal_factor
        
        # Calcola sezione conduttore
        conductor_section = self.calculate_conductor_section(
            requirements.earth_fault_current_a,
            requirements.fault_duration_s
        )
        
        # Prova diverse configurazioni
        configurations = []
        
        # 1. Anello perimetrale
        ring_resistance = self.calculate_ring_resistance(perimeter_m, effective_resistivity)
        configurations.append({
            'config': GroundingConfiguration.ANELLO_PERIMETRALE,
            'resistance': ring_resistance,
            'disperser_length': perimeter_m,
            'disperser_count': 1,
            'cost': perimeter_m * 15 + 500  # conduttore + scavo
        })
        
        # 2. Dispersori verticali
        n_vertical = self.calculate_vertical_dispersers(
            requirements.max_earth_resistance_ohm,
            effective_resistivity
        )
        vertical_resistance = effective_resistivity / (2 * math.pi * 1.5) / (n_vertical * 0.7)
        configurations.append({
            'config': GroundingConfiguration.DISPERSORI_VERTICALI,
            'resistance': vertical_resistance,
            'disperser_length': n_vertical * 1.5,
            'disperser_count': n_vertical,
            'cost': n_vertical * 75 + perimeter_m * 8  # picchetti + collegamento
        })
        
        # 3. Sistema misto (anello + dispersori)
        mixed_resistance = 1 / (1/ring_resistance + 1/vertical_resistance)
        configurations.append({
            'config': GroundingConfiguration.SISTEMA_MISTO,
            'resistance': mixed_resistance,
            'disperser_length': perimeter_m + n_vertical * 1.5,
            'disperser_count': n_vertical + 1,
            'cost': perimeter_m * 15 + n_vertical * 75 + 800
        })
        
        # Seleziona configurazione ottimale
        valid_configs = [c for c in configurations 
                        if c['resistance'] <= requirements.max_earth_resistance_ohm]
        
        if not valid_configs:
            # Nessuna configurazione soddisfa i requisiti - usa la migliore disponibile
            best_config = min(configurations, key=lambda x: x['resistance'])
            is_compliant = False
        else:
            # Seleziona la più economica tra quelle valide
            best_config = min(valid_configs, key=lambda x: x['cost'])
            is_compliant = True
        
        # Verifica tensioni di sicurezza
        touch_v, step_v = self.verify_touch_step_voltages(
            best_config['resistance'],
            requirements.earth_fault_current_a
        )
        
        # Verifica conformità tensioni
        voltage_compliant = (touch_v <= requirements.max_touch_voltage_v and 
                           step_v <= requirements.max_step_voltage_v)
        
        return GroundingResult(
            total_resistance_ohm=best_config['resistance'],
            conductor_section_mm2=conductor_section,
            disperser_length_m=best_config['disperser_length'],
            disperser_count=best_config['disperser_count'],
            touch_voltage_v=touch_v,
            step_voltage_v=step_v,
            is_compliant=is_compliant and voltage_compliant,
            total_cost_eur=int(best_config['cost']),
            conductor_type="Rame nudo 50 mm²",
            configuration=best_config['config']
        )
    
    def generate_materials_list(self, result: GroundingResult,
                              cabin_dimensions: Tuple[float, float]) -> Dict[str, Dict]:
        """Genera lista materiali per l'impianto"""
        
        length_m, width_m = cabin_dimensions
        perimeter_m = 2 * (length_m + width_m)
        
        materials = {
            "conduttore_terra": {
                "description": f"Conduttore rame nudo {result.conductor_section_mm2:.0f} mm²",
                "quantity": f"{result.disperser_length_m:.1f} m",
                "unit_cost": "€15/m",
                "total_cost": int(result.disperser_length_m * 15)
            },
            "dispersori": {
                "description": f"Dispersori {result.configuration.value}",
                "quantity": f"{result.disperser_count} pz",
                "unit_cost": "€75/pz",
                "total_cost": result.disperser_count * 75
            },
            "giunzioni": {
                "description": "Morsetti e giunzioni",
                "quantity": f"{result.disperser_count + 4} pz",
                "unit_cost": "€25/pz", 
                "total_cost": (result.disperser_count + 4) * 25
            },
            "scavo": {
                "description": "Scavo e ripristino",
                "quantity": f"{result.disperser_length_m:.1f} m",
                "unit_cost": "€8/m",
                "total_cost": int(result.disperser_length_m * 8)
            }
        }
        
        return materials