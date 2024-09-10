'''
가사와 분위기를 임베딩한 새로운 열 추가하는 파일
'''

import numpy as np
import os
import time

from pymongo import MongoClient, UpdateOne
from rag_embed import HuggingFaceEmbedding

from langchain_community.llms import Ollama
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

mongodb_atlas_cluster_uri = os.environ.get('MONGODB_URL')
client = MongoClient(mongodb_atlas_cluster_uri)
db = client['mel_lyrics']
collection = db['songs']

embed_model = HuggingFaceEmbedding()

def embed_lyrics():
    batch_size = 1000
    for doc in collection.find().batch_size(batch_size):
        if 'embedding' not in doc:
            lyrics = doc['lyric']
            embedding = embed_model.embed_query(lyrics)
            embedding_list = embedding.tolist()
            collection.update_one(
                {'_id': doc['_id']},
                {'$set': {'embedding': embedding_list}}
            )
            print(f"{doc['id']=}, done")
    print("All lyrics have been embedded.")

def embed_mood():
    batch_size = 1000
    for doc in collection.find().batch_size(batch_size):
        if 'mood_embedding' not in doc:
            mood = doc['mood']
            mood_embedding = embed_model.embed_query(mood)
            mood_embedding_list = mood_embedding.tolist()
            collection.update_one(
                {'_id': doc['_id']},
                {'$set': {'mood_embedding': mood_embedding_list}}
            )
            print(f"{doc['id']=}, done")
    print("All lyrics have been embedded.")

embed_lyrics()
embed_mood()