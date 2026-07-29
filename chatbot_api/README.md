# Chatbot API Notes

## Connection Pattern for LLM and Embeddings
As of the final stack decision, we are using the following setup for the LLM and Embeddings:

- **LLM**: We use `openai/gpt-oss-20b:free` accessed via OpenRouter's API. This is called using LangChain's `ChatOpenAI` class configured with `base_url="https://openrouter.ai/api/v1"`, the OpenRouter API key, and the aforementioned model name. This leverages OpenRouter's OpenAI-compatible API without needing additional LangChain packages beyond `langchain-openai`.

- **Embeddings**: We use `sentence-transformers/all-MiniLM-L6-v2` accessed via the HuggingFace Inference API's feature-extraction endpoint. This is a hosted call authenticated with the HF token, meaning we do not install torch or load model weights locally. This can be wrapped as a custom LangChain `Embeddings` class in a later phase.
