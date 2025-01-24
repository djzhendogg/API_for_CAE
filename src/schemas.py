from typing import List
from pydantic import BaseModel, Field
from enum import Enum

class PolymerType(str, Enum):
    protein = 'protein'
    protein_for_aptamer = 'protein_for_aptamer'
    dna = 'DNA'
    rna = 'RNA'


class EncodingStrategy(str, Enum):
    protein = 'protein'
    aptamers = 'aptamer'


class Monomer(BaseModel):
    name: str = Field(max_length=1)
    smiles: str


class NewMonomers(BaseModel):
    monomers: List[Monomer]


class SeqQuantKernelModel(BaseModel):
    max_sequence_length: int
    num_of_descriptors: int
    known_monomers: set[str]
    polymer_type: PolymerType
