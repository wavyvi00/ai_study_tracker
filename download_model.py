import os
import sys

def download_model():
    print("🚀 Setting up AI Model for FocusWin...")
    
    # Create model directory
    if not os.path.exists("model"):
        os.makedirs("model")
        
    print("📦 Installing dependencies...")
    try:
        import onnxruntime
        from tokenizers import Tokenizer
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
    except ImportError:
        print("⚠️  Missing dependencies. Installing...")
        os.system(f"{sys.executable} -m pip install onnxruntime tokenizers transformers torch")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch

    print("⬇️  Downloading MiniLM model (this may take a minute)...")
    
    # We'll use a pre-trained model fine-tuned for productivity/distraction if available,
    # or a generic NLI model and use zero-shot logic.
    # For this demo, let's download a generic small model and export to ONNX.
    
    model_id = "cross-encoder/nli-distilroberta-base" # Good for zero-shot classification
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)
    
    # Save Tokenizer
    tokenizer.save_pretrained("model")
    print("✅ Tokenizer saved.")
    
    # Export to ONNX
    print("🔄 Converting to ONNX...")
    dummy_input = tokenizer("This is a test", return_tensors="pt")
    
    torch.onnx.export(
        model, 
        (dummy_input["input_ids"], dummy_input["attention_mask"]), 
        "model/model.onnx",
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"}
        },
        opset_version=11
    )
    print("✅ Model converted to ONNX: model/model.onnx")
    print("\n🎉 Setup Complete! You can now run the app with AI detection.")

if __name__ == "__main__":
    download_model()
