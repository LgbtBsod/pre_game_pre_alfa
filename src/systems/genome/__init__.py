#!/usr/bin/env python3
"""
Genome System Package
"""

from .genome_system import (
    Gene, Chromosome, Genome, GenomeManager, genome_manager,
    GeneType, GeneDominance
)

__all__ = [
    'Gene',
    'Chromosome', 
    'Genome',
    'GenomeManager',
    'genome_manager',
    'GeneType',
    'GeneDominance'
]
