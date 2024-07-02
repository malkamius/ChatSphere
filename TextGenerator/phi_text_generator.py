import torch
from transformers import AutoModelForCausalLM, AutoConfig, AutoTokenizer, pipeline
from shared.ansi_logger import getLogger
from TextGenerator import TextGenerator
class PhiTextGenerator (TextGenerator):
    def __init__(self, config):
        self.logger = getLogger(config, __name__)
        self.initialize_model()
        
    def initialize_model(self):
        model_name = "leliuga/Phi-3-mini-128k-instruct-bnb-4bit"
        model_config = AutoConfig.from_pretrained(
            model_name,
            device_map="cuda",
            torch_dtype=torch.float16,
            trust_remote_code=True,
            attn_implementation="eager"
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="cuda",
            torch_dtype="auto",
            trust_remote_code=True,
            attn_implementation="eager",
            config=model_config
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def generate_batch(self, messages_batch, max_new_token_count=10):
        prompts = [
            self.pipe.tokenizer.apply_chat_template(messages['messages'], tokenize=False, add_generation_prompt=True) + messages['lasttext']
            for messages in messages_batch
        ]
        outputs = self.pipe(prompts, max_new_tokens=max_new_token_count, return_tensors="pt")
        generated_texts = []
        for output, messages in zip(outputs, messages_batch):
            prompt_tokens = self.tokenizer.encode(
                self.pipe.tokenizer.apply_chat_template(messages['messages'], tokenize=False, add_generation_prompt=True) + messages['lasttext'],
                return_tensors="pt"
            )
            prompt_length = prompt_tokens.shape[1] - 1
            output_tokens = output["generated_token_ids"]
            old_tokens = output_tokens[:prompt_length]
            total_text = self.tokenizer.decode(output_tokens, skip_special_tokens=True)
            skip_text = self.tokenizer.decode(old_tokens, skip_special_tokens=True)
            start_index = len(skip_text)
            generated_text = total_text[start_index:]
            generated_texts.append(generated_text)
        return generated_texts