"""Calcolatore carichi elettrici"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SimpleLoad:
    """Carico elettrico semplificato"""
    name: str
    type_str: str
    power_kw: float
    quantity: int = 1
    ku_factor: float = 1.0
    cos_phi: float = 0.85
    voltage: int = 400
    phases: int = 3

def get_kc_factor_simple(load_type_str: str, load_name: str = "") -> float:
    """Fattori contemporaneità CORRETTI"""
    
    type_lower = load_type_str.lower().strip()
    name_lower = load_name.lower().strip()
    
    # Fattori corretti e realistici
    if "illuminazione" in type_lower or "luci" in name_lower:
        return 1.0
    elif "prese" in type_lower or "presa" in type_lower:
        return 0.25
    elif "uffici" in name_lower or "office" in name_lower:
        return 0.25
    elif ("riscaldamento" in type_lower or "climatizzazione" in name_lower or 
          "hvac" in name_lower or "climate" in name_lower):
        return 1.0
    elif ("motori" in type_lower or "motore" in type_lower or 
          "compressor" in name_lower or "produzione" in name_lower):
        return 0.8
    elif "cucine" in type_lower or "cucina" in type_lower:
        return 0.7
    else:
        return 0.6

class LoadCalculator:
    """Calcolatore principale carichi"""
    
    def calculate_loads(self, loads: List[SimpleLoad]) -> Dict:
        """Calcola carichi con fattori corretti"""
        
        total_power_kw = 0
        total_power_kva = 0
        load_breakdown = []
        
        for load in loads:
            # Fattori contemporaneità corretti
            kc = get_kc_factor_simple(load.type_str, load.name)
            
            # Calcoli
            power_used_kw = load.power_kw * load.quantity * load.ku_factor * kc
            power_apparent_kva = power_used_kw / load.cos_phi
            current_a = (power_apparent_kva * 1000) / (1.732 * load.voltage)
            
            total_power_kw += power_used_kw
            total_power_kva += power_apparent_kva
            
            load_breakdown.append({
                "name": load.name,
                "type": load.type_str,
                "power_nominal_kw": load.power_kw * load.quantity,
                "ku_factor": load.ku_factor,
                "kc_factor": kc,
                "cos_phi": load.cos_phi,
                "power_used_kw": round(power_used_kw, 1),
                "power_apparent_kva": round(power_apparent_kva, 1),
                "current_a": round(current_a, 1)
            })
        
        return {
            "total_power_kw": round(total_power_kw, 1),
            "total_power_kva": round(total_power_kva, 1),
            "average_cos_phi": round(total_power_kw / total_power_kva, 2) if total_power_kva > 0 else 0.85,
            "load_breakdown": load_breakdown
        }