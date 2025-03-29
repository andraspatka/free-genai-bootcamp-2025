ARG BASE_TAG=latest
FROM opea/comps-base:$BASE_TAG

COPY ./llm_tts.py $HOME/llm_tts.py

ENTRYPOINT ["python", "llm_tts.py"]
