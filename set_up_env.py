import os
PROJECT_PATH = os.getcwd()
APTAMER_MODEL_PATH = os.path.join(PROJECT_PATH, 'src/models/aptamers/')
PROTEIN_MODEL_PATH = os.path.join(PROJECT_PATH, 'src/models/proteins/')
DESCRIPTOR_SCALER_PATH = os.path.join(PROJECT_PATH, 'src/models/descriptor_scaler.pkl')

if __name__ == "__main__":
    envs = f'{PROJECT_PATH=}\n' \
           f'{APTAMER_MODEL_PATH=}\n' \
           f'{PROTEIN_MODEL_PATH=}\n' \
           f'{DESCRIPTOR_SCALER_PATH=}\n'

    with open('.env', 'w') as f:
        f.write(envs)