import requests
from dotenv import load_dotenv


load_dotenv()

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

NEW_MONOMER = {
    'monomers': [
        {
            'name': 'X',
            'smiles': 'OC',
        },
    ],
}

# get_existing_monomers
response = requests.get('http://localhost:8080/monomers/DNA', headers=headers)
assert response.status_code == 200

response = requests.get('http://localhost:8080/monomers/RNA', headers=headers)
assert response.status_code == 200

response = requests.get('http://localhost:8080/monomers/protein_for_aptamer', headers=headers)
assert response.status_code == 200

response = requests.get('http://localhost:8080/monomers/protein', headers=headers)
assert response.status_code == 200

# get_kernel_info
response = requests.post('http://localhost:8080/kernel_info/protein', headers=headers, json=NEW_MONOMER)
# assert response.status_code == 200

response = requests.post('http://localhost:8080/kernel_info/protein_for_aptamer', headers=headers, json=NEW_MONOMER)
# assert response.status_code == 200

response = requests.post('http://localhost:8080/kernel_info/DNA', headers=headers, json=NEW_MONOMER)
# assert response.status_code == 200

response = requests.post('http://localhost:8080/kernel_info/RNA', headers=headers, json=NEW_MONOMER)
# assert response.status_code == 200

# generate_latent_representations
sequences = ['CGX']
params = {
    'sequences': ','.join(sequences),
    'polymer_type': 'protein_for_aptamer',
    'encoding_strategy': 'aptamers',
    'skip_unprocessable': 'true',
}

response = requests.post('http://localhost:8080/encode_sequence', params=params, headers=headers, json=NEW_MONOMER)
assert response.status_code == 200

params = {
    'sequences': ','.join(sequences),
    'polymer_type': 'protein_for_aptamer',
    'encoding_strategy': 'aptamers',
    'skip_unprocessable': 'false',
}

response = requests.post('http://localhost:8080/encode_sequence', params=params, headers=headers)
assert response.status_code == 422

params = {
    'sequences': ','.join(sequences),
    'polymer_type': 'protein_for_aptamer',
    'encoding_strategy': 'aptamers',
    'skip_unprocessable': 'true',
}

response = requests.post('http://localhost:8080/encode_sequence', params=params, headers=headers)
assert response.status_code == 200

sequences = ['AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
             'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA']
params = {
    'sequences': ','.join(sequences),
    'polymer_type': 'protein_for_aptamer',
    'encoding_strategy': 'aptamer',
    'skip_unprocessable': 'false',
}

response = requests.post('http://localhost:8080/encode_sequence', params=params, headers=headers, json=NEW_MONOMER)
assert response.status_code == 422

params = {
    'sequences': ','.join(sequences),
    'polymer_type': 'protein_for_aptamer',
    'encoding_strategy': 'aptamer',
    'skip_unprocessable': 'true',
}

response = requests.post('http://localhost:8080/encode_sequence', params=params, headers=headers, json=NEW_MONOMER)
assert response.status_code == 200

sequences = ['A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A',
             'A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A',
             'A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A',
             'A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A',
             'A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A',
             'A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A',
             'A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A']
params = {
    'sequences': ','.join(sequences),
    'polymer_type': 'protein_for_aptamer',
    'encoding_strategy': 'aptamer',
    'skip_unprocessable': 'true',
}

response = requests.post('http://localhost:8080/encode_sequence', params=params, headers=headers, json=NEW_MONOMER)
assert response.status_code == 422