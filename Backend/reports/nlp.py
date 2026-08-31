import sys

# 1. FORCE PYTORCH TO LOAD
try:
    import torch
    print(f"--> PyTorch loaded successfully! Version: {torch.__version__}")
except Exception as e:
    print(f"CRITICAL: PyTorch failed to load! {str(e)}", file=sys.stderr)

# 2. LOAD RAW COMPONENTS (BYPASSING PIPELINE WRAPPER)
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
except Exception as e:
    print(f"CRITICAL: Failed to import transformers classes: {e}", file=sys.stderr)
    AutoTokenizer, AutoModelForSeq2SeqLM = None, None

_TOKENIZER = None
_MODEL = None

def _load_ai_components():
    global _TOKENIZER, _MODEL

    # If already loaded, skip
    if _TOKENIZER is not None and _MODEL is not None:
        return True

    if AutoTokenizer is None:
        return False

    try:
        print("--> Explicitly loading DistilBART Tokenizer and Model...")
        model_name = "sshleifer/distilbart-cnn-12-6"
        
        # Load exactly what we need, no registry checks
        _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
        _MODEL = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        print("--> Bare-metal AI Model loaded successfully!")
        return True
    except Exception as e:
        print(f"CRITICAL MODEL EXPLICIT LOAD ERROR: {str(e)}", file=sys.stderr)
        return False

# Attempt to load right when Django starts
_load_ai_components()

def generate_report_summary(text):
    if not text:
        return ""

    cleaned_text = text.strip()
    if len(cleaned_text.split()) < 50:
        return cleaned_text

    if not _load_ai_components():
        print("WARNING: AI Components missing. Falling back to 250-character slice.", file=sys.stderr)
        return cleaned_text[:250]

    try:
        print("--> AI is analyzing the text directly via PyTorch...")
        
        # 1. Tokenize the text (convert words to numbers)
        inputs = _TOKENIZER(cleaned_text, return_tensors="pt", max_length=1024, truncation=True)
        
        # 2. Generate the summary (run the neural network)
        summary_ids = _MODEL.generate(
            inputs["input_ids"], 
            max_length=60, 
            min_length=20, 
            length_penalty=2.0, 
            num_beams=4, 
            early_stopping=True
        )
        
        # 3. Decode the result (convert numbers back to words)
        summary_text = _TOKENIZER.decode(summary_ids[0], skip_special_tokens=True).strip()
        
        if summary_text:
            return summary_text
    except Exception as e:
        print(f"NLP Raw Generation Error: {str(e)}", file=sys.stderr)

    return cleaned_text[:250]