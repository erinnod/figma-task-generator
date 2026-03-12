## Key Architecture Decisions and why

Decision 1: Fast API over Flask Fast API gives us automatic API documentation (Swagger UI at /docs), type validation via Pydantic, and async support out the box. For AI systems where LLM calls can take between 5-30 seconds, async is important.

Decision 2: Provider-agnostic LLM client. The src/llm/client.py will be written with an abstraction layer. Today we may use Claude or OpenAI. Tomorrow it may be self-hosted model. The pipeline can work with whatever, it just called llm.complete(pompt). This is the Strategy Pattern in practice.

Decision 3: Structured output parsing. I won't just dump LLM text to the user. I will define a schema (using Pydantic) and validate the LLM response against it.

Decision 4: Seperating the Parser from the LLM. I'll extract a clean intermediate representation from Figma JSON before sending anything to the LLM. This reduces token usage (cost), reduces noise, and makes prompts more deterministic.
