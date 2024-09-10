from jamo import h2j, j2hcj
from g2pk import G2p
import numpy as np
g2p = G2p()

from unicode import join_jamos

JA_EMBEDDING = {
    'ㅂ' : [0.0, 0.0, 1.0],
    'ㅃ' : [0.0, 0.0, 0.0],
    'ㅍ' : [0.0, 0.0, 0.1],
    'ㅁ' : [0.0, 0.75, 1.0],
    'ㄷ' : [0.25, 0.0, 1.0],
    'ㄸ' : [0.25, 0.0, 0.0],
    'ㅌ' : [0.25, 0.0, 0.1],
    'ㄴ' : [0.25, 0.75, 1.0],
    'ㄹ' : [0.25, 1.0, 1.0],
    'ㅅ' : [0.25, 0.5, 1.0],
    'ㅆ' : [0.25, 0.5, 0.0],
    'ㅈ' : [0.5, 0.25, 1.0],
    'ㅉ' : [0.5, 0.25, 0.0],
    'ㅊ' : [0.5, 0.25, 0.1],
    'ㄱ' : [0.75, 0.0, 1.0],
    'ㄲ' : [0.75, 0.0, 0.0],
    'ㅋ' : [0.75, 0.0, 0.1],
    'ㅇ' : [0.75, 0.75, 1.0],
    'ㅎ' : [1.0, 0.5, 0.1],
    'E' : [-1.0, -1.0, -1.0]
}
MO_EMBEDDING = {
    'ㅏ' : [1.0, 0.5, 0.0, 0.0, 0.0],
    'ㅐ' : [1.0, 0.0, 0.0, 0.0, 0.0],
    'ㅑ' : [1.0, 0.5, 0.0, 0.0, 1.0],
    'ㅒ' : [1.0, 0.0, 0.0, 0.0, 1.0],
    'ㅓ' : [0.5, 1.0, 0.0, 0.0, 0.0],
    'ㅔ' : [0.5, 0.0, 0.0, 0.0, 0.0],
    'ㅕ' : [0.5, 1.0, 0.0, 0.0, 1.0],
    'ㅖ' : [0.5, 0.0, 0.0, 0.0, 1.0],
    'ㅗ' : [0.5, 1.0, 1.0, 0.0, 0.0],
    'ㅛ' : [0.5, 1.0, 1.0, 0.0, 1.0],
    'ㅜ' : [0.0, 1.0, 1.0, 0.0, 0.0],
    'ㅠ' : [0.0, 1.0, 1.0, 0.0, 1.0],
    'ㅡ' : [0.0, 1.0, 0.0, 0.0, 0.0],
    'ㅣ' : [0.0, 0.0, 0.0, 0.0, 0.0],
    'ㅚ' : [0.5, 0.0, 1.0, 0.0, 0.5],
    'ㅟ' : [0.0, 0.0, 1.0, 0.0, 0.5]
}

# word1 = "뽀삐야"
# word2 = "포기다"
# word3 = "고지난"
# word4 = "칠전팔기"

ex1_word = "가겠습니다"
ex2_word = "가고십지만"
de_len_word = "가개문"



def split_jamo(text):
    """한글 단어를 들리는 발음으로 바꾸는 함수"""
    return j2hcj(h2j(text))

def process_word(word):
    """한글 단어를 들리는 발음으로 바꾸고 자모 단위로 쪼개고 글자 단위로 합쳐서 리스트로 리턴하는 함수
    종성이 없는 경우에는 'E'를 추가한다.
    return example : ['ㄱㅏE', 'ㄱㅔㄷ', 'ㅆㅡㅁ', 'ㄴㅣE', 'ㄷㅏE']"""
    jamo_list= []
    sound_word = g2p(word)
    for idx, t in enumerate(sound_word):
        split_word = split_jamo(t)
        if len(split_word) != 3:
            split_word+=("E")
            split_word+=("L")
        else:
            split_word+=("L")
        jamo_list.extend(split_word)
    str_jamo = "".join(jamo_list[:-1])
    sound_letter_jamo = str_jamo.split("L")
    return sound_letter_jamo

def embed_word(word):
    """한글 단어를 자모 단위로 쪼개고 자모별로 임베딩된 리스트를 만들어 리턴하는 함수
    return example : 
    [
        [[0.75, 0.0, 1.0], [0.5, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.1]], 
        [[0.75, 0.75, 1.0], [0.5, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
    ]"""
    sound_letter_jamo = process_word(word)
    embed_letter_list = []
    for jamo_letter in sound_letter_jamo:
        embed_jamo_list = []
        for embed_jamo in jamo_letter:
            if embed_jamo in JA_EMBEDDING.keys():
                embed_jamo_list.append(JA_EMBEDDING[embed_jamo])
            else:
                embed_jamo_list.append(MO_EMBEDDING[embed_jamo])
        embed_letter_list.append(embed_jamo_list)
    return embed_letter_list

def jamo_euclidean_distance(word1, word2):
    """같은 길이의 각각 단어를 자모 단위로 쪼개고 자모별로 임베딩한 리스트를 구해서 두 단어의 유클리디안 거리를 계산하는 함수
    두개의 인풋이 모두 한글로만 이루어져야 하고, 길이가 같아야 한다."""
    assert len(word1) == len(word2), "두 단어의 길이가 같아야 합니다."
    
    euclidian_distance = 0
    word_length = len(word1)
    embed_word1 = embed_word(word1)
    embed_word2 = embed_word(word2)
    for i in range(word_length):
        for j in range(3):
            embed_array1 = np.array(embed_word1[i][j])
            embed_array2 = np.array(embed_word2[i][j])
            if j == 1:
                distance = np.linalg.norm(embed_array1 - embed_array2) * 2
            else:
                distance = np.linalg.norm(embed_array1 - embed_array2)
            euclidian_distance += distance
    return euclidian_distance
    
    # print(embed_word1 - embed_word2)
    #     embed_list.append(JA_EMBEDDING[jamo])
    # return embed_list

if __name__ == "__main__":
    print(jamo_euclidean_distance("거지", "어이"))