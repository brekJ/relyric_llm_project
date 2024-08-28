from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import bitsandbytes as bnb

device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)

# Tokenizer and model loading
tokenizer = AutoTokenizer.from_pretrained("beomi/KoAlpaca-Polyglot-12.8B")
model = AutoModelForCausalLM.from_pretrained("beomi/KoAlpaca-Polyglot-12.8B", load_in_8bit=True)

model.to(device)
