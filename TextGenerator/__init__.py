from random import Random
from shared.ansi_logger import getLogger

class TextGenerator:
    def __init__(self, config):
        self.logger = getLogger(config, __name__)
        self.initialize_model()
        
    def initialize_model(self):
        model_name = "leliuga/Phi-3-mini-128k-instruct-bnb-4bit"
        model_config = None
        self.model = None
        self.tokenizer = None
        self.pipe = None
        self.random : Random = Random()
    
    def generate_batch(self, messages_batch, max_new_token_count=10):
        # Fake text appending logic for demonstration
        generated_texts = []
        for messages in messages_batch:
            generated_text = messages['lasttext'] + " [FAKE GENERATED TEXT]"
            if self.random.random() < .5:
                generated_text = generated_text + "--end of text--"
            generated_texts.append(generated_text)
        return generated_texts