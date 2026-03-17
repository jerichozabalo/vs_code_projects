from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from config import MODEL_NAME

print('MODEL_NAME', MODEL_NAME)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map='auto')
pipe = pipeline('text-generation', model=model, tokenizer=tokenizer)
llm = HuggingFacePipeline(pipeline=pipe)
print('llm type', type(llm))
print('callable?', callable(llm))
print('dir llm', [m for m in dir(llm) if not m.startswith('_')])
