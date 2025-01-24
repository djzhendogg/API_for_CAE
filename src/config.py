import os
from dotenv import load_dotenv

load_dotenv()


DESCRIPTOR_SCALER_PATH = os.getenv('DESCRIPTOR_SCALER_PATH')
PROTEIN_MODEL_PATH = os.getenv('PROTEIN_MODEL_PATH')
APTAMER_MODEL_PATH = os.getenv('APTAMER_MODEL_PATH')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_NAME = os.getenv('DB_NAME')
DB_PASS = os.getenv('DB_PASS')
