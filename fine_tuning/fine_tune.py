from unsloth import FastLanguageModel
import torch

max_seq_length = 4096
dtype = torch.float16
load_in_4bit = True

model, tokenizer = FastLanguageModel.from_pretrained(
   model_name = "yanolja/EEVE-Korean-10.8B-v1.0",
   max_seq_length = max_seq_length,
   dtype = dtype,
   load_in_4bit = load_in_4bit,
   device_map="auto"
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,  
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=7468,
    use_rslora=False,
    loftq_config=None,
)

from datasets import load_dataset

EOS_TOKEN = tokenizer.eos_token

alpaca_prompt = """### Instruction:
{}

### Response:
{}"""


def formatting_prompts_func(examples):
    instructions = examples["inputs"]
    outputs = examples["response"]
    texts = []
    for instruction, output in zip(instructions, outputs):
        text = alpaca_prompt.format(instruction, output) + EOS_TOKEN
        texts.append(text)
    return {
        "text": texts,
    }

dataset = load_dataset("csv", data_files="augmented_dataset.csv", split="train")
dataset = dataset.map(
    formatting_prompts_func,
    batched=True,
)

train_test_split = dataset.train_test_split(test_size=0.2, shuffle=True, seed=7468)

train_dataset = train_test_split['train']
test_dataset = train_test_split['test']

from trl import SFTTrainer
from transformers import TrainingArguments, EarlyStoppingCallback

tokenizer.padding_side = "right"

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

early_stopping_callback = EarlyStoppingCallback(
    early_stopping_patience=5,
    early_stopping_threshold=0.005
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_ratio=0.1,
        num_train_epochs=5,
        # max_steps=3000,
        do_eval=True,
        evaluation_strategy="steps",
        eval_steps=100,
        logging_steps=10,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=7468,
        output_dir="outputs",
        save_strategy="steps",
        save_steps=100,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
    ),
    callbacks=[early_stopping_callback]
)

trainer.train()

model.save_pretrained("model")


