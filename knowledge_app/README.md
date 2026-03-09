# Knowledge Consolidation & Content Generation App

A Flask app that consolidates your influential writings and personal narratives, then generates social media content (Facebook & YouTube) using local AI models. **No token limits, completely private.**

## Features

- **Knowledge Storage**: Add influential writings and narratives to a local database
- **Social Media Generation**: Generate Facebook posts and YouTube video scripts based on your knowledge
- **Local AI Models**: Uses lightweight models by default, with option to upgrade to Llama-2 for better quality
- **Zero Internet Dependency**: After initial setup, runs fully offline (except model download)

## Setup

### 1. Create Virtual Environment

```bash
cd knowledge_app
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
python app.py
```

Then open: `http://127.0.0.1:5000/`

## Usage

### Add Knowledge

1. Go to `/add`
2. Enter:
   - **Title**: Name of the knowledge item
   - **Content**: Full text (e.g., principles, story excerpt)
   - **Source**: Where it came from (e.g., "Book: Atomic Habits")
   - **Category**: "Influential Writing" or "Narratives"
3. Click "Add"

### Generate Content

1. Go to `/generate`
2. Enter:
   - **Query**: What you want (e.g., "How to build daily habits")
   - **Platform**: Facebook (short post) or YouTube (video script)
   - **Category**: Filter by knowledge type (optional)
3. Click "Generate"

The AI will retrieve relevant knowledge and create tailored content.

## Model Information

### Current: DistilGPT2 (~500MB)

- **Pros**: Fast, works on CPU, minimal data usage, downloads quickly
- **Cons**: Lower quality output, less sophisticated
- **Best For**: Now (testing, on data connection)

### Upgrade to Llama-2 (~14GB) - Later with WiFi

- **Pros**: Much better quality, more sophisticated writing, better context understanding
- **Cons**: Slower (10-60 sec per generation), requires more disk space, needs WiFi to download
- **Best For**: Production use, when you have WiFi

## Upgrade to Llama-2 (When You Have WiFi)

1. Connect to WiFi
2. Run: `python download_model.py`
3. Wait for the download (~10-30 minutes, ~14GB)
4. Once complete, edit `config.py`:
   ```python
   USE_LOCAL_LLAMA = True
   ```
5. Restart the app

The app will now use Llama-2 for significantly better content quality, with **no internet required after download**.

## Folder Structure

```
knowledge_app/
├── app.py              # Main Flask app
├── config.py           # Configuration
├── download_model.py   # Download Llama-2 when WiFi available
├── requirements.txt    # Python dependencies
├── static/
│   └── style.css       # Styling
├── templates/
│   ├── index.html      # Knowledge list
│   ├── add.html        # Add knowledge form
│   └── generate.html   # Generate content form
├── data/               # Database storage (auto-created)
└── models/             # Llama-2 storage (optional, after download)
```

## Troubleshooting

### "Model download too slow"
- If DistilGPT2 is still too slow, try smaller models in `config.py`:
  - `microsoft/DialoGPT-small` (~250MB)
  - `gpt2` (~500MB)

### "CUDA out of memory" error
- Edit `config.py` and change `MODEL_NAME` to a smaller model
- Or ensure GPU drivers are up to date

### "Knowledge base is empty"
- Add at least one knowledge item before generating
- The AI needs context to work from

## Future Enhancements

- Auto-posting to Facebook and YouTube (requires OAuth setup)
- File uploads (PDF, Word docs)
- Advanced search and filtering
- Multiple language support
- Analytics on generated content performance

## License

Personal use. Respect copyrights of sources you add.

## Notes

- **Privacy**: Your knowledge stays local on your machine. No uploads to servers.
- **Customization**: Edit templates for different layouts or styles
- **Backups**: The database is in `data/knowledge.db` - back it up regularly
