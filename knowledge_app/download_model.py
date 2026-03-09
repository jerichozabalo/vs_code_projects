"""
Download Llama-2-7B-Chat model when you have WiFi connection.
This script downloads the model (~14GB) to your local machine for offline use.

Instructions:
1. When you have WiFi, run: python download_model.py
2. Wait for the model to download (Hugging Face Hub will handle it)
3. Once complete, update config.py:
   - Set USE_LOCAL_LLAMA = True
   - Adjust LOCAL_LLAMA_PATH if needed
4. Restart the app and it will use Llama instead of DistilGPT2

The download happens ONCE. After that, the app uses it locally without internet.
"""

import os
from transformers import AutoTokenizer, AutoModelForCausalLM

# The model to download
MODEL_NAME = 'meta-llama/Llama-2-7b-chat-hf'
SAVE_PATH = './models/llama-model'

def download_model():
    print(f"Downloading {MODEL_NAME}...")
    print(f"This will download ~14GB. Ensure you have WiFi and sufficient disk space.")
    print()
    
    os.makedirs(SAVE_PATH, exist_ok=True)
    
    try:
        print("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        tokenizer.save_pretrained(SAVE_PATH)
        print("✓ Tokenizer saved")
        
        print("Downloading model (this may take 10-30 minutes)...")
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="auto", torch_dtype="auto")
        model.save_pretrained(SAVE_PATH)
        print("✓ Model saved")
        
        print()
        print("=" * 60)
        print("SUCCESS! Model downloaded and saved to:", SAVE_PATH)
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Open config.py")
        print("2. Change: USE_LOCAL_LLAMA = True")
        print("3. Restart the app")
        print()
        print("The app will now use Llama-2 instead of DistilGPT2")
        print("(Better quality, but slower. No internet needed after this.)")
        
    except Exception as e:
        print(f"✗ Error downloading model: {e}")
        print("Make sure your Hugging Face token is set up for Llama access:")
        print("1. Get access to Llama at: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf")
        print("2. Run: huggingface-cli login")
        print("3. Try again")

if __name__ == '__main__':
    download_model()
