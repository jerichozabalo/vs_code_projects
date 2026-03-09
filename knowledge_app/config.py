DATABASE = 'data/knowledge.db'
SECRET_KEY = 'your-unique-secret-key-change-this'  # Use a strong key
DEBUG = True

# Model config: Start with a small model for data connections
# Switch to 'meta-llama/Llama-2-7b-chat-hf' after downloading locally (see download_model.py)
MODEL_NAME = 'distilgpt2'  # ~500MB, fast on CPU. Works on data connection.
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # For vector search (~100MB)

# Set to True after Llama download to use local Llama instead
USE_LOCAL_LLAMA = False
LOCAL_LLAMA_PATH = './models/llama-model'  # Path where you'll store Llama when WiFi available