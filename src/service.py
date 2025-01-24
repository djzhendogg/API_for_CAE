import os
import copy
import numpy as np
import joblib
import pandas as pd

from fastapi import HTTPException

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

import tensorflow as tf
from keras.models import Model

from src.schemas import NewMonomers
from src.config import (
    DESCRIPTOR_SCALER_PATH,
    PROTEIN_MODEL_PATH,
    APTAMER_MODEL_PATH
)
from src.constants import (
    DNA_DESCR,
    PROTEIN_DESCR,
    PROTEIN_DESCR_APTAMER,
    RNA_DESCR
)

trained_prot_model = tf.keras.models.load_model(PROTEIN_MODEL_PATH)

prot_model = Model(
    inputs=trained_prot_model.input,
    outputs=trained_prot_model.get_layer('Latent').output
)
trained_aptamer_model = tf.keras.models.load_model(APTAMER_MODEL_PATH)

aptamer_model = Model(
    inputs=trained_aptamer_model.input,
    outputs=trained_aptamer_model.get_layer('Latent').output
)
print("import prot models")

class Kernel:
    """
    Class designed to process DNA/RNA/protein sequences with custom encoder using rdkit and peptide descriptors.
    """

    def __init__(
            self,
            polymer_type: str = 'protein',
            new_monomers: NewMonomers = None,
    ):
        """
        Initialisation.
        :param polymer_type: Polymers types. Possible values: 'protein', 'DNA', 'RNA'.
        :param skip_unprocessable: Set to True to skip sequences with unknown monomers and sequences with length >96.
        :param new_monomers: list of dicts with new monomers: {'name':'str', 'class':'protein/DNA/RNA', 'smiles':'str'}
        """

        self.max_sequence_length: int = 96
        self.num_of_descriptors = 43
        self.descriptors_scaler = joblib.load(DESCRIPTOR_SCALER_PATH)

        self.polymer_type = polymer_type
        self.descriptors: dict[str, list[float]] = {}
        self.read_precalculated_rdkit_descriptors()
        self.new_monomers = new_monomers
        self.add_monomer_to_descriptors()
        self.known_monomers = set(self.descriptors.keys())

    def read_precalculated_rdkit_descriptors(self):
        """
        Formalizes the descriptors_file_path depending on the polymer type.
        """
        if self.polymer_type == 'protein':
            self.descriptors = copy.deepcopy(PROTEIN_DESCR)
            self.num_of_descriptors = 46
        elif self.polymer_type == 'protein_for_aptamer':
            self.descriptors = copy.deepcopy(PROTEIN_DESCR_APTAMER)
        elif self.polymer_type == 'DNA':
            self.descriptors = copy.deepcopy(DNA_DESCR)
        elif self.polymer_type == 'RNA':
            self.descriptors = copy.deepcopy(RNA_DESCR)

    @staticmethod
    def load_model(encoding_strategy):
        if encoding_strategy == 'protein':
            return prot_model
        elif encoding_strategy == 'aptamer':
            return aptamer_model

    def calculate_monomer(
            self,
            designation: str,
            smiles: str,
    ) -> dict:
        descriptor_names = list(Chem.rdMolDescriptors.Properties.GetAvailableProperties())

        get_descriptors = Chem.rdMolDescriptors.Properties(descriptor_names)
        molecule = Chem.MolFromSmiles(smiles)
        descriptors = np.array(
            get_descriptors.ComputeProperties(molecule)
        ).reshape((1, -1))
        descriptors_set = self.descriptors_scaler.transform(descriptors).tolist()[0]
        return {designation: descriptors_set}

    def add_monomer_to_descriptors(self):
        if self.new_monomers:
            for designation in self.new_monomers.monomers:
                if designation.name not in set(self.descriptors.keys()):
                    new_monomer = self.calculate_monomer(designation.name, designation.smiles)
                    self.descriptors.update(new_monomer)
                    print("UPDATE MONOMER DESCR")
                else:
                    error_text = f'Monomer {designation} is already exists in core.'
                    raise HTTPException(status_code=422, detail=error_text)

    def length_filter(self, sequence_list, skip_unprocessable):
        processed_sequence_list: list[str] = []
        for sequence in sequence_list:
            if len(sequence) > self.max_sequence_length:
                if not skip_unprocessable:
                    error_text = 'There are the sequence whose length ' \
                                 f'exceeds the maximum = {self.max_sequence_length}: {sequence} ' \
                                 'Set skip_unprocessable as True in kernel or exclude if by yourself.'
                    raise HTTPException(status_code=422, detail=error_text)
                else:
                    continue
            else:
                processed_sequence_list.append(sequence.upper())
        return processed_sequence_list

    def unknown_monomer_filter(self, sequence_list, skip_unprocessable):
        processed_sequence_list: list[str] = []
        for sequence in sequence_list:
            if not set(sequence).issubset(self.known_monomers):
                if not skip_unprocessable:
                    error_text = f'There are unknown monomers in sequence: {sequence}. ' \
                                 'You can fix it with: ' \
                                 '1) adding new monomer in kernel;' \
                                 '2) setting skip_unprocessable as True;' \
                                 '3) excluding it by yourself.'
                    raise HTTPException(status_code=422, detail=error_text)
                else:
                    continue
            else:
                processed_sequence_list.append(sequence)
        return processed_sequence_list

    def sequence_to_descriptor_matrix(
            self,
            sequence: str
    ) -> tf.Tensor:
        """
        Сonverts a single sequence into a descriptor matrix.
        :param sequence: Alphanumeric sequence.
        :return: Tensor with shape (max_sequence_length, num_of_descriptors).
        """
        sequence_matrix: tf.Tensor = tf.zeros(shape=[0, self.num_of_descriptors])
        for monomer in sequence:
            monomer_params = tf.constant(
                self.descriptors[monomer],
                dtype=tf.float32
            )
            descriptors_array = tf.expand_dims(
                monomer_params,
                axis=0
            )
            sequence_matrix = tf.concat(
                [sequence_matrix, descriptors_array],
                axis=0
            )
        sequence_matrix = tf.transpose(sequence_matrix)
        paddings = tf.constant([[0, 0], [0, 96 - len(sequence)]])
        sequence_matrix = tf.pad(
            sequence_matrix,
            paddings=paddings,
            mode='CONSTANT',
            constant_values=0
        )
        return sequence_matrix

    def encoding(
            self,
            sequence_list
    ) -> tf.Tensor:
        """
        Сonverts a list of sequences into a  sequences/descriptor tensor.
        :return: Sequences/descriptor tensor.
        """
        container = []
        for sequence in sequence_list:
            seq_matrix = tf.expand_dims(
                self.sequence_to_descriptor_matrix(
                    sequence=sequence
                ),
                axis=0
            )
            container.append(seq_matrix)
        return tf.concat(container, axis=0)

    def generate_latent_representations(
            self,
            sequence_list,
            skip_unprocessable,
            encoding_strategy='protein'
    ) -> dict:
        """
        Processes the sequences/descriptor tensor using a model.
        :param sequence_list: Enumeration of sequences for filtering.
        :param skip_unprocessable: Set to True to skip sequences with unknown monomers and sequences with length >96.
        :param encoding_strategy: Selects a model for encoding. Possible values: 'protein', 'aptamer', 'nucleic_acids'.
        :return: Ready-made features.
        """
        result: dict[str, list[float]] = {}
        sequence_list_filter1 = self.length_filter(sequence_list, skip_unprocessable)
        sequence_list_filter2 = self.unknown_monomer_filter(sequence_list_filter1, skip_unprocessable)
        if not sequence_list_filter2:
            return {}
        encoded_sequence_list = self.encoding(sequence_list_filter2)

        model = self.load_model(encoding_strategy)
        latent_representation: np.ndarray = model.predict(
            encoded_sequence_list
        )
        for sequence, descriptors in zip(sequence_list_filter2, latent_representation):
            result[sequence] = descriptors.tolist()
        return result

if __name__ == "__main__":
    from src.schemas import NewMonomers, PolymerType, EncodingStrategy

    sqt = Kernel(
        polymer_type=PolymerType('protein'),
    )
    seq_list = ['RLSRIVVIRVSR']
    aaa = sqt.sequence_to_descriptor_matrix('RLSRIVVIRVSR').numpy()
    result = sqt.generate_latent_representations(seq_list, True, encoding_strategy=EncodingStrategy('protein'))
    print(result)
