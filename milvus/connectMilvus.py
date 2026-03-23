from pymilvus import MilvusClient
from config import URI, USER, PASSWORD

client = MilvusClient(uri=URI, user=USER, password=PASSWORD)

collections = client.list_collections()
print("Collections:", collections)
