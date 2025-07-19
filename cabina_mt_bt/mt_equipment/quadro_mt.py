"""
Quadro MT Completo - Tutti i dispositivi necessari
File: mt_equipment/quadro_mt.py
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class UnitType(Enum):
    """Tipi di unità funzionali MT"""
    ARRIVO_LINEA = "arrivo_linea"
    PARTENZA_TRASFORMATORE = "partenza_trasformatore"
    PARTENZA_RISERVA = "partenza_riserva"
    UNITA_MISURE = "unita_misure"

class BreakerType(Enum):
    """Tipi di interruttore MT"""
    VUOTO_INDOOR = "vuoto_indoor"
    SF6_INDOOR = "sf6_indoor"
    SF6_OUTDOOR = "sf6_outdoor"

class ProtectionType(Enum):
    """Tipi di protezione"""
    REF601 = "REF601"
    REF615 = "REF615"
    REF630 = "REF630"

@dataclass
class MTBreaker:
    """Interruttore MT con caratteristiche complete"""
    series: str
    type: BreakerType
    rated_current: int  # A
    rated_voltage: int  # kV
    breaking_capacity: int  # kA
    insulation_medium: str
    operation_type: str = "manuale"
    auxiliary_contacts: str = "6NA+6NC"
    trip_release: bool = True
    close_release: bool = True
    operation_counter: bool = True
    cost_estimate: int = 0

@dataclass
class MTSectionalizer:
    """Sezionatore MT"""
    type: str  # "linea" o "terra"
    rated_current: int  # A
    rated_voltage: int  # kV
    insulation_medium: str  # "SF6" o "aria"
    key_interlocks: bool = True
    mechanical_interlocks: bool = True
    position_indication: bool = True
    cost_estimate: int = 0

@dataclass
class ProtectionRelay:
    """Relè di protezione MT"""
    model: str
    type: ProtectionType
    functions: List[str]
    cei_016_compliant: bool
    communication: List[str]
    data_logger: bool = False
    applications: List[str] = None
    cost_estimate: int = 0

@dataclass
class CurrentTransformer:
    """Trasformatore di corrente MT"""
    primary_current: int  # A
    rated_power: int  # VA
    secondary_current: int = 5  # A
    accuracy_class_measurement: str = "0.5"
    accuracy_class_protection: str = "5P10"
    rated_voltage: int = 0  # kV
    type: str = "standard"  # "standard", "toroidal", "sensor"
    cost_estimate: int = 0

@dataclass
class VoltageTransformer:
    """Trasformatore di tensione MT"""
    primary_voltage: int  # V
    rated_power: int  # VA
    secondary_voltage: int = 100  # V
    accuracy_class_measurement: str = "0.5"
    accuracy_class_protection: str = "3P"
    type: str = "standard"  # "standard", "capacitive"
    cost_estimate: int = 0

@dataclass
class VoltagePresence:
    """Presenza tensione"""
    rated_voltage: int  # kV
    indication_type: str = "LED"  # "LED", "lampada", "digitale"
    phases: int = 3
    cost_estimate: int = 150

@dataclass
class DigitalInstrument:
    """Strumentazione digitale"""
    type: str  # "amperometro", "voltmetro", "wattmetro", "multimetro"
    measurement_range: str
    accuracy_class: str = "0.5"
    display_type: str = "LCD"
    communication: str = "Modbus RTU"
    cost_estimate: int = 0

@dataclass
class AuxiliaryEquipment:
    """Equipaggiamenti ausiliari"""
    type: str  # "alimentatore", "resistenza", "ventilazione", "illuminazione"
    specification: str
    power_consumption: int = 0  # W
    cost_estimate: int = 0

@dataclass
class MTUnit:
    """Unità funzionale MT completa"""
    unit_type: UnitType
    unit_name: str
    breaker: MTBreaker
    line_sectionalizer: MTSectionalizer
    earth_sectionalizer: MTSectionalizer
    protection_relay: ProtectionRelay
    current_transformers: List[CurrentTransformer]
    voltage_transformers: List[VoltageTransformer]
    voltage_presence: VoltagePresence
    digital_instruments: List[DigitalInstrument]
    auxiliary_equipment: List[AuxiliaryEquipment]
    
    def get_total_cost(self) -> int:
        """Calcola costo totale unità"""
        total = (self.breaker.cost_estimate + 
                self.line_sectionalizer.cost_estimate +
                self.earth_sectionalizer.cost_estimate +
                self.protection_relay.cost_estimate +
                self.voltage_presence.cost_estimate)
        
        for ct in self.current_transformers:
            total += ct.cost_estimate
        for vt in self.voltage_transformers:
            total += vt.cost_estimate
        for instr in self.digital_instruments:
            total += instr.cost_estimate
        for aux in self.auxiliary_equipment:
            total += aux.cost_estimate
            
        return total

class MTSwitchgear:
    """Quadro MT completo con tutte le unità"""
    
    def __init__(self, product_database=None):
        self.product_db = product_database
        self.units: List[MTUnit] = []
        self.panel_specifications = {
            "series": "ABB UniSec",
            "protection_degree": "IP3X",
            "internal_arc_classification": "IAC A FL 25kA",
            "rated_voltage": 24,  # kV
            "rated_current": 1250,  # A
            "breaking_capacity": 25,  # kA
            "dimensions": {"height": 2000, "width": 1554, "depth": 1248}  # mm
        }
    
    def create_arrivo_linea_unit(self, network_data: Dict) -> MTUnit:
        """Crea unità arrivo linea (DG) con tutti i dispositivi"""
        
        # Seleziona interruttore MT
        required_current = network_data.get("max_current", 100)
        voltage_kv = network_data.get("voltage_kv", 20)
        breaking_capacity = network_data.get("breaking_capacity_ka", 25)
        
        breaker = self._select_mt_breaker(required_current, voltage_kv, breaking_capacity)
        
        # Sezionatori
        line_sectionalizer = MTSectionalizer(
            type="linea",
            rated_current=breaker.rated_current,
            rated_voltage=breaker.rated_voltage,
            insulation_medium="SF6",
            cost_estimate=1200
        )
        
        earth_sectionalizer = MTSectionalizer(
            type="terra",
            rated_current=breaker.rated_current,
            rated_voltage=breaker.rated_voltage,
            insulation_medium="SF6",
            cost_estimate=800
        )
        
        # Relè protezione DG (con comunicazione)
        protection_relay = ProtectionRelay(
            model="REF601",
            type=ProtectionType.REF601,
            functions=["51", "50", "51N", "50N", "68"],
            cei_016_compliant=True,
            communication=["Modbus RTU", "RS485"],
            data_logger=True,
            applications=["DG", "Dispositivo Generale"],
            cost_estimate=2800
        )
        
        # TA per DG (correnti più elevate)
        current_transformers = [
            CurrentTransformer(
                primary_current=max(250, required_current),
                rated_power=15,
                type="sensor",
                cost_estimate=800
            ) for _ in range(3)  # 3 fasi
        ]
        
        # TA toroidale per terra
        current_transformers.append(
            CurrentTransformer(
                primary_current=100,
                rated_power=10,
                type="toroidal",
                accuracy_class_protection="5P10",
                cost_estimate=250
            )
        )
        
        # TV per misure
        voltage_transformers = [
            VoltageTransformer(
                primary_voltage=voltage_kv * 1000,
                rated_power=50,
                cost_estimate=650
            ) for _ in range(3)  # 3 fasi
        ]
        
        # Presenza tensione
        voltage_presence = VoltagePresence(
            rated_voltage=voltage_kv,
            indication_type="LED",
            cost_estimate=200
        )
        
        # Strumentazione DG
        digital_instruments = [
            DigitalInstrument(
                type="multimetro",
                measurement_range=f"0-{breaker.rated_current}A, 0-{voltage_kv}kV",
                cost_estimate=1500
            ),
            DigitalInstrument(
                type="wattmetro",
                measurement_range="0-2000kW",
                cost_estimate=800
            )
        ]
        
        # Ausiliari DG
        auxiliary_equipment = [
            AuxiliaryEquipment(
                type="alimentatore",
                specification="24V DC 5A",
                power_consumption=50,
                cost_estimate=300
            ),
            AuxiliaryEquipment(
                type="resistenza",
                specification="Anticondensa 100W",
                power_consumption=100,
                cost_estimate=150
            )
        ]
        
        return MTUnit(
            unit_type=UnitType.ARRIVO_LINEA,
            unit_name="Arrivo Linea - DG",
            breaker=breaker,
            line_sectionalizer=line_sectionalizer,
            earth_sectionalizer=earth_sectionalizer,
            protection_relay=protection_relay,
            current_transformers=current_transformers,
            voltage_transformers=voltage_transformers,
            voltage_presence=voltage_presence,
            digital_instruments=digital_instruments,
            auxiliary_equipment=auxiliary_equipment
        )
    
    def create_partenza_trasformatore_unit(self, transformer_data: Dict, unit_number: int) -> MTUnit:
        """Crea unità partenza trasformatore con tutti i dispositivi"""
        
        # Calcola corrente primaria trasformatore
        power_kva = transformer_data.get("power_kva", 400)
        voltage_kv = transformer_data.get("voltage_primary_kv", 20)
        primary_current = power_kva * 1000 / (1.732 * voltage_kv * 1000)
        
        # Seleziona interruttore MT
        breaker = self._select_mt_breaker(primary_current * 1.25, voltage_kv, 16)
        
        # Sezionatori
        line_sectionalizer = MTSectionalizer(
            type="linea",
            rated_current=breaker.rated_current,
            rated_voltage=breaker.rated_voltage,
            insulation_medium="SF6",
            cost_estimate=1200
        )
        
        earth_sectionalizer = MTSectionalizer(
            type="terra",
            rated_current=breaker.rated_current,
            rated_voltage=breaker.rated_voltage,
            insulation_medium="SF6",
            cost_estimate=800
        )
        
        # Relè protezione trasformatore (senza comunicazione)
        protection_relay = ProtectionRelay(
            model="REF601",
            type=ProtectionType.REF601,
            functions=["51", "50", "51N", "50N", "68"],
            cei_016_compliant=True,
            communication=["Modbus RTU"],
            data_logger=False,
            applications=["Trasformatore", "Partenza"],
            cost_estimate=2500
        )
        
        # TA per trasformatore
        ta_primary = max(30, int(primary_current * 1.5))
        current_transformers = [
            CurrentTransformer(
                primary_current=ta_primary,
                rated_power=15,
                type="standard",
                cost_estimate=320
            ) for _ in range(3)  # 3 fasi
        ]
        
        # TA toroidale per terra
        current_transformers.append(
            CurrentTransformer(
                primary_current=100,
                rated_power=10,
                type="toroidal",
                accuracy_class_protection="5P10",
                cost_estimate=250
            )
        )
        
        # TV per misure (condivisi o dedicati)
        voltage_transformers = [
            VoltageTransformer(
                primary_voltage=voltage_kv * 1000,
                rated_power=25,
                cost_estimate=650
            ) for _ in range(3)  # 3 fasi
        ]
        
        # Presenza tensione
        voltage_presence = VoltagePresence(
            rated_voltage=voltage_kv,
            indication_type="LED",
            cost_estimate=200
        )
        
        # Strumentazione trasformatore
        digital_instruments = [
            DigitalInstrument(
                type="amperometro",
                measurement_range=f"0-{ta_primary}A",
                cost_estimate=400
            ),
            DigitalInstrument(
                type="voltmetro",
                measurement_range=f"0-{voltage_kv}kV",
                cost_estimate=400
            )
        ]
        
        # Ausiliari trasformatore
        auxiliary_equipment = [
            AuxiliaryEquipment(
                type="resistenza",
                specification="Anticondensa 50W",
                power_consumption=50,
                cost_estimate=100
            )
        ]
        
        return MTUnit(
            unit_type=UnitType.PARTENZA_TRASFORMATORE,
            unit_name=f"Partenza Trasformatore {unit_number}",
            breaker=breaker,
            line_sectionalizer=line_sectionalizer,
            earth_sectionalizer=earth_sectionalizer,
            protection_relay=protection_relay,
            current_transformers=current_transformers,
            voltage_transformers=voltage_transformers,
            voltage_presence=voltage_presence,
            digital_instruments=digital_instruments,
            auxiliary_equipment=auxiliary_equipment
        )
    
    def _select_mt_breaker(self, required_current: float, voltage_kv: float, breaking_capacity_ka: float) -> MTBreaker:
        """Seleziona interruttore MT appropriato"""
        
        # Usa database prodotti se disponibile
        if self.product_db:
            breaker_spec = self.product_db.get_mt_breaker_by_current(
                required_current, voltage_kv, breaking_capacity_ka
            )
            
            return MTBreaker(
                series=breaker_spec.series,
                type=BreakerType.VUOTO_INDOOR if "vuoto" in breaker_spec.insulation_medium else BreakerType.SF6_INDOOR,
                rated_current=breaker_spec.rated_current,
                rated_voltage=breaker_spec.rated_voltage,
                breaking_capacity=breaker_spec.breaking_capacity,
                insulation_medium=breaker_spec.insulation_medium,
                cost_estimate=breaker_spec.cost_estimate
            )
        
        # Selezione manuale se database non disponibile
        if voltage_kv <= 24 and breaking_capacity_ka <= 25:
            breaker_type = BreakerType.VUOTO_INDOOR
            series = "HySec p230"
            insulation = "vuoto"
        else:
            breaker_type = BreakerType.SF6_INDOOR
            series = "HySec SF6"
            insulation = "SF6"
        
        # Seleziona corrente standard
        standard_currents = [200, 400, 630, 800, 1000, 1250, 1600]
        selected_current = next((c for c in standard_currents if c >= required_current), 1600)
        
        return MTBreaker(
            series=series,
            type=breaker_type,
            rated_current=selected_current,
            rated_voltage=int(voltage_kv),
            breaking_capacity=int(breaking_capacity_ka),
            insulation_medium=insulation,
            cost_estimate=4500 + selected_current * 3.5
        )
    
    def design_complete_switchgear(self, project_data: Dict) -> Dict:
        """Progetta quadro MT completo con tutti i dispositivi"""
        
        # Dati rete
        network_data = project_data.get("network", {})
        
        # Crea unità arrivo linea
        arrivo_unit = self.create_arrivo_linea_unit(network_data)
        self.units.append(arrivo_unit)
        
        # Crea unità partenze trasformatore
        transformers = project_data.get("transformers", [])
        for i, transformer in enumerate(transformers, 1):
            partenza_unit = self.create_partenza_trasformatore_unit(transformer, i)
            self.units.append(partenza_unit)
        
        # Calcola costi e dimensioni
        total_cost = sum(unit.get_total_cost() for unit in self.units)
        panel_width = 500 + (len(self.units) * 500)  # 500mm per unità
        
        # Aggiorna dimensioni quadro
        self.panel_specifications["dimensions"]["width"] = panel_width
        
        return {
            "panel_specifications": self.panel_specifications,
            "units": self.units,
            "total_cost": total_cost,
            "unit_count": len(self.units),
            "total_width": panel_width,
            "summary": self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict:
        """Genera sommario del quadro MT"""
        
        device_count = {
            "interruttori_mt": len(self.units),
            "rele_protezione": len(self.units),
            "ta_misura": sum(len([ct for ct in unit.current_transformers if ct.type != "toroidal"]) for unit in self.units),
            "ta_toroidali": sum(len([ct for ct in unit.current_transformers if ct.type == "toroidal"]) for unit in self.units),
            "tv_misura": sum(len(unit.voltage_transformers) for unit in self.units),
            "sezionatori": len(self.units) * 2,  # linea + terra
            "strumentazione": sum(len(unit.digital_instruments) for unit in self.units),
            "ausiliari": sum(len(unit.auxiliary_equipment) for unit in self.units)
        }
        
        return {
            "device_count": device_count,
            "cei_016_compliant": True,
            "protection_functions": ["51", "50", "51N", "50N", "68"],
            "communication_available": True,
            "data_logging": True
        }
    
    def get_unit_by_type(self, unit_type: UnitType) -> List[MTUnit]:
        """Ottieni unità per tipo"""
        return [unit for unit in self.units if unit.unit_type == unit_type]
    
    def get_total_power_consumption(self) -> int:
        """Calcola consumo totale ausiliari"""
        total = 0
        for unit in self.units:
            for aux in unit.auxiliary_equipment:
                total += aux.power_consumption
        return total