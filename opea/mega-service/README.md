# Technical spec

@llm_tts.py is an OPEA mega-service. Its purpose is to orchestrate multiple OPEA components.
One of them is serving an LLM using TGI. The other is running SPEECHT5 for speech synthesis.

The llm_tts service is expecting a prompt from the user and then forwards this to the LLM service which will generate a response. The response is then changed into voice with the SpeechT5 service. 

The requests flow in the following way:
- Request with the prompt goes into the llm-tts service
- The llm-tts service forwards the request to the LLM service (TGI)
- The LLM service generates a response
- The response forwarded to the SpeechT5 service which then converts the response into voice
- The result is returned to the user

The deployment is orchestrated using docker-compose.
