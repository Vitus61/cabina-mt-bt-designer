"""
Modulo per calcolo e progettazione impianti di terra MT/BT
Conforme a CEI 11-27, CEI 64-8, CEI 99-1
"""

from .earthing_calculator import (
    EarthingSystemDesigner,
    SoilType,
    SoilData,
    GroundingRequirements,
    GroundingConfiguration
)

__all__ = [
    'EarthingSystemDesigner',
    'SoilType', 
    'SoilData',
    'GroundingRequirements',
    'GroundingConfiguration'
]