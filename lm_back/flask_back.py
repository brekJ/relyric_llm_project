from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool, AgentExecutor, ZeroShotAgent
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.schema import LLMResult, AgentAction, AgentFinish
from langchain.agents.agent import AgentOutputParser

from typing import Union
import re
import os
import json

from pymongo import MongoClient

# 자모 분석 관련 함수 임포트 (ko_sound_distance.py 파일에서)
from ko_sound_distance import split_jamo, process_word, jamo_euclidean_distance

# RAG 관련 함수 임포트 (vector_rag.py 파일에서)
from vector_rag import hybrid_search

os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # GPU 1 사용

app = Flask(__name__)
CORS(app)

# MongoDB 연결 설정
mongodb_atlas_cluster_uri = os.environ['MONGODB_URL']
client = MongoClient(mongodb_atlas_cluster_uri)
db = client['mel_lyrics']
collection = db['songs']

# LLM 설정
llm = Ollama(
    base_url=os.environ['OLLAMA_URL'],
    model="JunoAI",
    temperature=0.0
)

def retrieve_similar_lyrics(atmosphere, input_lyrics, top_k=2):
    search_results = hybrid_search(collection, atmosphere, input_lyrics, top_k=top_k)
    relevant_lyrics = "\n".join([f"{result.get('title', 'N/A')} - {result.get('singer', 'N/A')}\n{result.get('lyric', 'N/A')[:500]}..." for result in search_results])
    return relevant_lyrics

class LyricsOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        
        match = re.match(r"Thought:(.*?)Action:(.*?)Action Input:(.*)", llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        
        thought = match.group(1).strip()
        action = match.group(2).strip()
        action_input = match.group(3).strip()
        
        return AgentAction(tool=action, tool_input=action_input, log=llm_output)

class LyricsStreamHandler(StreamingStdOutCallbackHandler):
    def __init__(self):
        self.tokens = []
        self.lyrics_started = False

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        if not self.lyrics_started and "Final Answer:" in token:
            self.lyrics_started = True
            token = token.split("Final Answer:")[-1].strip()
        if self.lyrics_started:
            self.tokens.append(token)

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        pass

    def get_generated_lyrics(self) -> str:
        return ''.join(self.tokens)

def create_lyrics_agent(llm):
    tools = [
        Tool(
            name="SplitJamo",
            func=split_jamo,
            description="한글 단어를 자모 단위로 분리합니다. 입력: 한글 단어, 출력: 자모 단위로 분리된 문자열"
        ),
        Tool(
            name="ProcessWord",
            func=process_word,
            description="한글 단어를 발음 기반으로 처리하고 자모 단위로 분리합니다. 입력: 한글 단어, 출력: 자모 단위로 분리된 리스트"
        ),
        Tool(
            name="JamoEuclideanDistance",
            func=jamo_euclidean_distance,
            description="두 한글 단어 간의 자모 기반 유클리디안 거리를 계산합니다. 입력: 두 개의 한글 단어, 출력: 거리 값"
        ),
        Tool(
            name="RetrieveSimilarLyrics",
            func=retrieve_similar_lyrics,
            description="주어진 분위기와 입력 가사와 유사한 가사를 검색합니다. 입력: 분위기, 입력 가사, 출력: 유사한 가사 목록"
        )
    ]

    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix="""당신은 한국어 가사를 생성하는 AI 작사가입니다. 주어진 가사를 새로운 분위기에 맞게 개사해야 합니다.

다음 조건을 반드시 지켜주세요:

[상위 조건]
-- 출력 가사만 출력하세요. 추가 설명이나 주석을 포함하지 마세요.
-- 입력 가사와 정확히 동일한 줄 수, 띄어쓰기, 줄바꿈을 사용하여 출력 가사를 작성하세요.
-- 입력된 분위기에 어울리도록 작성하세요.
-- 입력 가사와 출력 가사의 리듬 및 음절 수를 각 줄마다 정확히 일치시키세요.

[중위 조건]
-- 입력 가사의 리듬과 Rhyme을 유지하세요.
-- 입력 가사의 단어의 음절과 강세, 발음을 고려하세요. 필요하다면 제공된 자모 분석 도구를 사용하세요.
-- 입력 가사와 동일한 단어를 사용할 수 있지만 남발하지 마세요.

[하위 조건]
-- 발음하기 쉽고, 노래부르기에 적합하도록 작성하세요.

제공된 도구를 사용하여 단어의 발음 유사성을 분석하고, 이를 바탕으로 더 적절한 단어를 선택할 수 있습니다. 
또한, RetrieveSimilarLyrics 도구를 사용하여 추가적인 참고 가사를 얻을 수 있습니다.""",
        suffix="""Human: {input}

AI: 네, 알겠습니다. 주어진 조건과 도구를 활용하여 새로운 가사를 생성하겠습니다.

{agent_scratchpad}""",
        input_variables=["input", "agent_scratchpad"]
    )

    memory = ConversationBufferMemory(memory_key="chat_history")

    llm_chain = LLMChain(llm=llm, prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
    return AgentExecutor.from_agent_and_tools(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        memory=memory,
        handle_parsing_errors=True,
        max_iterations=2
    )

def generate_lyrics_with_agent(llm, input_lyrics, atmosphere):
    agent_executor = create_lyrics_agent(llm)
    stream_handler = LyricsStreamHandler()
    
    try:
        # RAG를 사용하여 초기 참고 가사 검색
        initial_reference_lyrics = retrieve_similar_lyrics(atmosphere, input_lyrics)
        
        # 모든 입력을 단일 문자열로 결합
        combined_input = f"""입력 가사를 '{atmosphere}' 분위기로 개사해주세요.

입력 가사:
{input_lyrics}

새로운 분위기: {atmosphere}

참고 가사:
{initial_reference_lyrics}"""

        result = agent_executor.run(
            input=combined_input,
            callbacks=[stream_handler]
        )
        
        print(f"Agent Result: {result}")
        
        generated_lyrics = stream_handler.get_generated_lyrics()
        generated_lyrics = re.sub(r'\n\s*\n', '\n', generated_lyrics.strip())
        
        if not generated_lyrics:
            raise ValueError("생성된 가사가 비어있습니다.")
        
        return generated_lyrics
    except Exception as e:
        print(f"Error in generate_lyrics_with_agent: {str(e)}")
        raise

@app.route('/api/ollama', methods=['POST'])
def process_lyrics():
    try:
        data = request.json
        input_lyrics = data['input']
        atmosphere = data['atmosphere']

        new_lyrics = generate_lyrics_with_agent(llm, input_lyrics, atmosphere)

        def generate():
            for line in new_lyrics.split('\n'):
                response_data = json.dumps({'text': line + '\n'})
                yield f"data: {response_data}\n\n"
            yield f"data: {json.dumps({'status': 'completed'})}\n\n"

        return Response(stream_with_context(generate()), content_type='text/event-stream')
    except Exception as e:
        print(f"Server error: {str(e)}")
        return Response(json.dumps({'error': str(e)}), status=500, content_type='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)