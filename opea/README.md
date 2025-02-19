# Try out a couple of OPEA components

Source: https://github.com/opea-project/GenAIComps

## Setup

```
make start
make pull llama3.2:1b
make test
```

## OPEA comps that were tried out

I tried out `text2sql` and using the ollama-server endpoint as the `TGI_LLM_ENDPOINT`, but this didn't work on an M1 Mac:
```
RuntimeError: This version of jaxlib was built using AVX instructions, which your CPU and/or operating system do not support. You may be able work around this issue by building jaxlib from source.
```