'''
MongoDB Atlass에 벡터 인덱스 추가하는 파일
'''

from pymongo.mongo_client import MongoClient
from pymongo.operations import SearchIndexModel
import os

def create_vector_index():
    mongodb_atlas_cluster_uri = os.environ.get('MONGODB_URI')
    client = MongoClient(mongodb_atlas_cluster_uri)

    database = client["mel_lyrics"]
    collection = database["songs"]

    search_index_model = SearchIndexModel(
        definition={
            "mappings": {
                "dynamic": False,
                "fields": {
                    "lyric": {
                        "type": "string"
                    }
                }
            }
        },
        name="lyric_text_index",
    )

    result = collection.create_search_index(model=search_index_model)

    indexes = collection.list_indexes()
    for index in indexes:
        print(index)

if __name__ == "__main__":
    create_vector_index()