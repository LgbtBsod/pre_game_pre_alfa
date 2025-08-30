"""
Система эволюции и мутаций AI-EVOLVE
Генетические алгоритмы для развития персонажей
"""

from .evolution_system import (
    EvolutionSystem,
    Gene, Mutation, EvolutionTree, EvolutionProgress, GeneticCombination,
    GeneType, MutationType, EvolutionPath, EvolutionStage
)

__all__ = [
    'EvolutionSystem',
    'Gene', 'Mutation', 'EvolutionTree', 'EvolutionProgress', 'GeneticCombination',
    'GeneType', 'MutationType', 'EvolutionPath', 'EvolutionStage'
]
