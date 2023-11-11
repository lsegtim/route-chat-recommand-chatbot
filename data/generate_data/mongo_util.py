import os

# load from .env
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

load_dotenv()

uri = os.getenv("MONGODB_URI")

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# exit()

def create_db(client):
    # Create a new database named 'histomind'
    db = client['histomind']

    # Create a collection named 'users' in the 'histomind' database.
    users_collection = db['users']

    # Create a collection named 'locations' in the 'histomind' database.
    locations_collection = db['locations']

    # Create a collection named 'interactions' in the 'histomind' database.
    interactions_collection = db['interactions']

    return users_collection, locations_collection, interactions_collection


def add_data(defect_collection, drug_collection):
    # Add dummy data to the 'drug' collection.
    drug_data = [
        {'name': 'Hydrocortisone cream', 'defect_name': '1. Eczema 1677'},
        {'name': 'Tacrolimus ointment', 'defect_name': '1. Eczema 1677'},
        {'name': 'Pimecrolimus cream', 'defect_name': '1. Eczema 1677'},
        {'name': 'Dabrafenib', 'defect_name': '2. Melanoma 15.75k'},
        {'name': 'Trametinib', 'defect_name': '2. Melanoma 15.75k'},
        {'name': 'Pembrolizumab', 'defect_name': '2. Melanoma 15.75k'},
        {'name': 'Calcineurin inhibitors', 'defect_name': '3. Atopic Dermatitis - 1.25k'},
        {'name': 'Topical corticosteroids', 'defect_name': '3. Atopic Dermatitis - 1.25k'},
        {'name': 'PDE4 inhibitors', 'defect_name': '3. Atopic Dermatitis - 1.25k'},
        {'name': 'Imiquimod cream', 'defect_name': '4. Basal Cell Carcinoma (BCC) 3323'},
        {'name': 'Fluorouracil cream', 'defect_name': '4. Basal Cell Carcinoma (BCC) 3323'},
        {'name': 'Photodynamic therapy', 'defect_name': '4. Basal Cell Carcinoma (BCC) 3323'},
        {'name': 'Cryotherapy', 'defect_name': '5. Melanocytic Nevi (NV) - 7970'},
        {'name': 'Laser therapy', 'defect_name': '5. Melanocytic Nevi (NV) - 7970'},
        {'name': 'Excision', 'defect_name': '5. Melanocytic Nevi (NV) - 7970'},
        {'name': 'Cryotherapy', 'defect_name': '6. Benign Keratosis-like Lesions (BKL) 2624'},
        {'name': 'Curettage and electrodesiccation', 'defect_name': '6. Benign Keratosis-like Lesions (BKL) 2624'},
        {'name': 'Laser therapy', 'defect_name': '6. Benign Keratosis-like Lesions (BKL) 2624'},
        {'name': 'Topical corticosteroids',
         'defect_name': '7. Psoriasis pictures Lichen Planus and related diseases - 2k'},
        {'name': 'Vitamin D analogues', 'defect_name': '7. Psoriasis pictures Lichen Planus and related diseases - 2k'},
        {'name': 'Retinoids', 'defect_name': '7. Psoriasis pictures Lichen Planus and related diseases - 2k'},
        {'name': 'Cryotherapy', 'defect_name': '8. Seborrheic Keratoses and other Benign Tumors - 1.8k'},
        {'name': 'Curettage and electrodesiccation',
         'defect_name': '8. Seborrheic Keratoses and other Benign Tumors - 1.8k'},
        {'name': 'Laser therapy', 'defect_name': '8. Seborrheic Keratoses and other Benign Tumors - 1.8k'},
        {'name': 'Antifungal creams',
         'defect_name': '9. Tinea Ringworm Candidiasis and other Fungal Infections - 1.7k'},
        {'name': 'Antifungal pills', 'defect_name': '9. Tinea Ringworm Candidiasis and other Fungal Infections - 1.7k'},
        {'name': 'Antifungal shampoos',
         'defect_name': '9. Tinea Ringworm Candidiasis and other Fungal Infections - 1.7k'},
        {'name': 'Acyclovir', 'defect_name': '10. Warts Molluscum and other Viral Infections - 2103'},
        {'name': 'Imiquimoid', 'defect_name': '10. Warts Molluscum and other Viral Infections - 2103'},
        {'name': 'Podofilox', 'defect_name': '10. Warts Molluscum and other Viral Infections - 2103'}
    ]
    drug_collection.insert_many(drug_data)


def get_drugs_by_defect(drug_collection, defect_name):
    result = drug_collection.find({'defect_name': defect_name})
    drugs = []
    for r in result:
        drugs.append(r['name'])
    return drugs


# delete all data
def delete_all_data(defect_collection, drug_collection):
    defect_collection.delete_many({})
    drug_collection.delete_many({})
