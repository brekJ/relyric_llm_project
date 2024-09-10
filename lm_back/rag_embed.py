'''
임베딩에 사용할 model 불러오고 형식에 맞추어서 custom class 작성
'''

import numpy as np

import torch
from transformers import AutoTokenizer, AutoModel

class HuggingFaceEmbedding:
    def __init__(self, model_name="xlm-roberta-large", cache_dir=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        self.model = AutoModel.from_pretrained(model_name, cache_dir=cache_dir).to(self.device)

    def embed_documents(self, texts, batch_size=32):
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            inputs = self.tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                embeddings = embeddings / embeddings.norm(dim=1, keepdim=True)
            all_embeddings.append(embeddings.cpu().numpy())
        return np.vstack(all_embeddings)

    def embed_query(self, text):
        return self.embed_documents([text])[0]

    def __call__(self, texts):
        if isinstance(texts, list):
            return self.embed_documents(texts)
        else:
            return self.embed_query(texts)