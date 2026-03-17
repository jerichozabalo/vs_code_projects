from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from config import MODEL_NAME

print('building llm...')
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map='auto')
pipe = pipeline('text-generation', model=model, tokenizer=tokenizer, max_new_tokens=10)
llm = HuggingFacePipeline(pipeline=pipe)

print('calling generate...')
res = llm.generate(["Hello world"])
print('result type', type(res))
print(res)
print('text extraction', res.generations[0][0].text)
