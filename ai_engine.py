import os
import numpy as np
import json

class AIInferenceEngine:
    def __init__(self, model_path="model/model.onnx", tokenizer_path="model/tokenizer.json"):
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.session = None
        self.tokenizer = None
        self.labels = ["focused", "distracted", "searching"]
        self.enabled = False
        
        self._load_model()

    def _load_model(self):
        try:
            import onnxruntime as ort
            from tokenizers import Tokenizer
            
            if not os.path.exists(self.model_path) or not os.path.exists(self.tokenizer_path):
                print(f"⚠️ AI Model not found at {self.model_path}. Attempting automatic download...")
                try:
                    import download_model
                    download_model.download_model()
                except Exception as e:
                    print(f"❌ Failed to auto-download model: {e}")
                    return

            self.session = ort.InferenceSession(self.model_path)
            self.tokenizer = Tokenizer.from_file(self.tokenizer_path)
            self.enabled = True
            print("✅ AI Inference Engine loaded successfully")
            
        except ImportError:
            print("⚠️ AI dependencies (onnxruntime, tokenizers) not installed. Running in Rule-Only mode.")
        except Exception as e:
            print(f"❌ Error loading AI model: {e}")

    def predict(self, text):
        """
        Predict focus state from text.
        Returns: (state, confidence)
        """
        if not self.enabled:
            return "unknown", 0.0

        try:
            # Tokenize
            encoded = self.tokenizer.encode(text)
            input_ids = np.array([encoded.ids], dtype=np.int64)
            attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
            
            # Run Inference
            inputs = {
                self.session.get_inputs()[0].name: input_ids,
                self.session.get_inputs()[1].name: attention_mask
            }
            logits = self.session.run(None, inputs)[0]
            
            # Softmax
            probs = self._softmax(logits[0])
            pred_idx = np.argmax(probs)
            confidence = float(probs[pred_idx])
            
            # Map index to label (assuming model was trained with these labels)
            # Note: You might need to adjust this mapping based on your specific model training
            # For a general zero-shot or similarity model, logic would be different.
            # Here we assume a custom trained classification head.
            # If using raw embeddings (MiniLM), we would calculate cosine similarity to reference vectors.
            
            # SIMPLIFIED LOGIC for "Zero-Shot" using Embeddings (MiniLM style)
            # Since we are using a raw transformer, we likely get embeddings, not logits.
            # Let's assume we are using a sequence classification model for simplicity.
            # If using raw MiniLM, we would need to compare embeddings.
            
            # For this implementation, let's assume the model outputs 3 logits: [focused, distracted, searching]
            label = self.labels[pred_idx] if pred_idx < len(self.labels) else "unknown"
            
            return label, confidence

        except Exception as e:
            print(f"AI Prediction Error: {e}")
            return "unknown", 0.0

    def _softmax(self, x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()
