'''
RAG 할 때 검색 및 결과 리턴하는 함수 정의
'''

from pymongo import MongoClient
import numpy as np
import os
from rag_embed import HuggingFaceEmbedding

lyric_embed_model = HuggingFaceEmbedding()
mood_embed_model = HuggingFaceEmbedding()
models = [lyric_embed_model, mood_embed_model]

def generate_embedding(text, model):
    embed_text = model(text)
    return embed_text

def hybrid_search(collection, atmosphere_query, lyrics_query, top_k=5):
    
    # 쿼리 임베딩 생성
    atmosphere_embedding = generate_embedding(atmosphere_query, model=mood_embed_model)
    lyrics_embedding = generate_embedding(lyrics_query, model=lyric_embed_model)

    # 분위기 기반 검색
    atmosphere_pipeline = [
        {
            "$vectorSearch": {
                "index": "hybrid_vector_index",
                "queryVector": atmosphere_embedding.tolist(),
                "path": "mood_embedding",
                "numCandidates": top_k * 200,
                "limit": top_k * 20
            }
        },
        {
            "$project": {
                "title": 1,
                "singer": 1,
                "lyric": 1,
                "mood": 1,
                "atmosphere_score": { "$meta": "vectorSearchScore" }
            }
        }
    ]

    # 가사 기반 검색
    lyrics_pipeline = [
        {
            "$vectorSearch": {
                "index": "hybrid_vector_index",
                "queryVector": lyrics_embedding.tolist(),
                "path": "embedding",
                "numCandidates": top_k * 200,
                "limit": top_k * 20
            }
        },
        {
            "$project": {
                "title": 1,
                "singer": 1,
                "lyric": 1,
                "mood": 1,
                "lyrics_score": { "$meta": "vectorSearchScore" }
            }
        }
    ]

    # 두 쿼리 실행
    atmosphere_results = list(collection.aggregate(atmosphere_pipeline))
    lyrics_results = list(collection.aggregate(lyrics_pipeline))

    # 결과 결합 및 점수 계산
    combined_results = {}

    for result in atmosphere_results + lyrics_results:
        id = result['_id']
        if id not in combined_results:
            combined_results[id] = result
            combined_results[id]['total_score'] = 0
            if 'atmosphere_score' in result:
                combined_results[id]['total_score'] += result['atmosphere_score']
            
            if 'lyrics_score' in result:
                combined_results[id]['total_score'] += result['lyrics_score']
        else:
            if 'atmosphere_score' in result:
                combined_results[id]['total_score'] += result['atmosphere_score']
                combined_results[id]['atmosphere_score'] = result['atmosphere_score']
            
            if 'lyrics_score' in result:
                combined_results[id]['total_score'] += result['lyrics_score']
                combined_results[id]['lyrics_score'] = result['lyrics_score']

    # 결과 정렬 및 상위 k개 선택
    sorted_results = sorted(combined_results.values(), key=lambda x: x['total_score'], reverse=True)[:top_k]

    return sorted_results


# 사용 예시
if __name__ == '__main__':
    mongodb_atlas_cluster_uri = os.environ.get('MONGODB_URI')
    client = MongoClient(mongodb_atlas_cluster_uri)
    db = client['mel_lyrics']
    collection = db['songs']
    
    atmosphere = "강아지와 주인이 대화하는 상황"
    lyrics = """꺾어 버리는 한마디
    깎여 버리는 웃음기
    모든 게 다 바닥난 채
    떨고 있었다

    맘의 온도는 하강 중
    서서히 얼어붙던 중
    넌 달려와 뜨겁게 날 끌어안았다

    걱정하는 눈빛으로
    바라봐 주는 너
    고생했어 오늘도 (오늘도)
    한마디에

    걷잡을 수 없이
    스르륵 녹아내려요
    죽어가던 마음을
    기적처럼 살려 낸 그 순간

    따뜻한 눈물이
    주르륵 흘러내려요
    너의 그 미소가
    다시 버텨 낼 수 있게 해 줘요

    걱정 마 괜찮아
    옆에 내가 있잖아
    너의 그 말이 날
    다시 일어서게 해

    기막힌 우연처럼
    나타나 줬던 너
    두 팔 벌려
    웃으며 (어서 와)
    안아 주면

    걷잡을 수 없이
    스르륵 녹아내려요
    죽어가던 마음을
    기적처럼 살려 낸 그 순간

    따뜻한 눈물이
    주르륵 흘러내려요
    너의 그 미소가
    다시 버텨 낼 수 있게 해 줘요

    나에게 넌 행운이야 놀라움 뿐이야
    이젠 내 차례
    Love you hold you give you all I got

    걷잡을 수 없이
    스르륵 녹아내려요
    죽어가던 마음을
    기적처럼 살려 낸 그 순간

    따뜻한 눈물이
    주르륵 흘러내려요
    너의 그 미소가
    다시 버텨 낼 수 있게 해 줘요
    """
    search_results = hybrid_search(collection, atmosphere, lyrics, top_k=5)

    for result in search_results:
        print("Result keys:", result.keys())
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Singer: {result.get('singer', 'N/A')}")
        print(f"Atmosphere Score: {result.get('atmosphere_score', 'N/A')}")
        print(f"Lyrics Score: {result.get('lyrics_score', 'N/A')}")
        print(f"Total Score: {result.get('total_score', 'N/A'):.4f}")
        print("---")

    print(f"Number of results: {len(search_results)}")