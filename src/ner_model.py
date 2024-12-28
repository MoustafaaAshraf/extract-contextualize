from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from joblib import Parallel, delayed
import math

# TODO: Document better

class NERModel:
    def __init__(self, model_name_or_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name_or_path)
        self.model.eval()

    def get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """
        Returns a substring of `text` that includes the specified [start, end) range,
        plus 'window' characters before and after for context.
        """
        prefix_start = max(0, start - window)
        suffix_end = min(len(text), end + window)
        return text[prefix_start:suffix_end]
    
    def extract_entities(self, text: str):
        # 1) Split text into chunks that fit within BERT's 512 token limit
        # Using 450 tokens per chunk to leave room for special tokens
        encoded = self.tokenizer.encode(text, add_special_tokens=False)
        chunk_size = 450
        chunks = [
            encoded[i:i + chunk_size] 
            for i in range(0, len(encoded), chunk_size)
        ]
        
        # 2) Process chunks in parallel
        def process_chunk(chunk):
            # Decode chunk back to text
            chunk_text = self.tokenizer.decode(chunk)
            
            # Process single chunk
            inputs = self.tokenizer(chunk_text, 
                            return_tensors="pt", 
                            truncation=True, 
                            padding=True)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.argmax(outputs.logits, dim=-1)
                
                # Convert predictions to entities (implement your entity extraction logic here)
                # This is a placeholder - replace with your actual entity extraction code
                entities = []
                # ... your entity extraction logic ...
                return entities
        
        # Process all chunks in parallel using all available cores
        results = Parallel(n_jobs=-1)(
            delayed(process_chunk)(chunk) for chunk in chunks
        )
        
        # 3) Combine results from all chunks
        all_entities = []
        offset = 0
        for chunk_entities in results:
            for entity in chunk_entities:
                # Adjust entity positions based on chunk offset
                entity["start"] += offset
                entity["end"] += offset
                entity["context"] = self.get_context(text, 
                                            entity["start"], 
                                            entity["end"])
                all_entities.append(entity)
            
            # Update offset for next chunk
            offset += len(chunk_entities)
        
        return all_entities
