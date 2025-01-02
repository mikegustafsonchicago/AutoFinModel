import logging
import tiktoken
from config import OPENAI_MODEL

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Function to count tokens for a given text
def count_tokens(text, model=OPENAI_MODEL):
    if text:
        tokenizer = tiktoken.encoding_for_model(model)
        tokens = tokenizer.encode(text)
        return len(tokens)
    else:
        logging.debug("Warning: No Text sent to count_tokens")
        return 0