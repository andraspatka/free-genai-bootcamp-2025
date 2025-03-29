# Try out a couple of OPEA components

Source: https://github.com/opea-project/GenAIComps

## Setup

``` 
make start # launch the services in docker-compose; this also pulls the image
make test # execute an example query
```

## Infrastructure

The infrastructure is provisioned through Terraform.
`tf-infra` contains the IaC parts.
ASGs are used so that EC2 instances can easily be scaled down and up on demand.
Spot nodes are also used to keep costs minimal.

[See the terraform code](tf-infra/README.md)

## Run TGI on AWS with Xeon processors

I gave OPEA another try by using AWS to have access to an Xeon processor instead of the M1.

The infrastructure is provisioned using terraform `tf-infra` contains the IaC parts.

The technical uncertainty in this case is:
- Will I get text2sql working on AWS with an instance that has a Xeon processor?
-> Yes and it's working well! It's slow but not sure if that's a limitation of the instance or the code.
- Will I get vLLM working with AWS inf instances?
-> Yes and it's working well!
- Is the performance going to be good? What are the limits that I can go to with a given instance type?
-> Attempted only 1 request at a time but the turnaround time for that was a couple of minutes already.

Working demo video available at: https://youtu.be/96vAJkGMI_4

## OPEA Mega-service

A new OPEA mega-service was implemented in order to gain more domain knowledge on OPEA.
The mega-service is very similar to existing examples but it's a bit simpler.

The mega service uses TGI for LLM and SPEECHT5 for speech synthesis. The user sends a prompt and gets the result in an audio file.

See the demo here: https://www.loom.com/share/b3764ee22fc94ff1a3d94e376ca9df0b?sid=f0dcc959-647f-4679-8c7c-4d7454dcc0a9

Results:
- The mega service works, it routes the requests successfully to TGI and then its response to SpeechT5
- For some reason the result seem repetitive and it looks like the LLM doesn't know when to stop. Or there's an issue with the mega service where it's looping the requests. This will need to be investigated further.

[See the code and more information](mega-service/README.md)


## Past attempts: OPEA comps that were tried out (M1)

Technical uncertainty:
- Will text2sql work on a mac with m1?
    - Yes it will! But it a couple of tweaks are needed in the dockerfile and it needs to be built on M1 for it to work
- Will text2sql work with an ollama-server? The documentation mentions TGI as the LLM endpoint.
    - No it won't work. They are not interoperable.
- Will text2sql work with a tiny model?
    - I was not able to test this out as it needs TGI to work which doesn't run on M1

I tried out `text2sql` and using the ollama-server endpoint as the `TGI_LLM_ENDPOINT`, but this didn't work on an M1 Mac:
```
RuntimeError: This version of jaxlib was built using AVX instructions, which your CPU and/or operating system do not support. You may be able work around this issue by building jaxlib from source.
```

-> Compiling the docker image myself makes it work. The dockerfile needs some updates so that it works. I forked the opea repo and made some changes to it and then added it here as a submodule.

The text2sql service is starting up correctly now!

Next issue is that the ollama-server is not compatible with the TGI interface as it seems. Logs of text2sql-server:
```
2025-02-20 19:52:08 [2025-02-20 17:52:08,006] [    INFO] - comps-text2sql - Starting Agent
2025-02-20 19:52:08 /home/user/comps/text2sql/src/integrations/sql_agent.py:149: LangChainDeprecationWarning: The class `LLMChain` was deprecated in LangChain 0.1.17 and will be removed in 1.0. Use RunnableSequence, e.g., `prompt | llm` instead.
2025-02-20 19:52:08   values["llm_chain"] = LLMChain(
2025-02-20 19:52:08 /usr/local/lib/python3.11/site-packages/huggingface_hub/inference/_generated/_async_client.py:2308: FutureWarning: `stop_sequences` is a deprecated argument for `text_generation` task and will be removed in version '0.28.0'. Use `stop` instead.
2025-02-20 19:52:08   warnings.warn(
2025-02-20 19:50:15 INFO:     172.21.0.1:59158 - "POST /v1/postgres/health HTTP/1.1" 404 Not Found
2025-02-20 19:52:08 
2025-02-20 19:52:08 
2025-02-20 19:52:08 > Entering new SQL Agent Executor chain...
2025-02-20 19:52:08 INFO:     172.21.0.1:55142 - "POST /v1/text2sql HTTP/1.1" 500 Internal Server Error
2025-02-20 19:52:08 ERROR:    Exception in ASGI application
2025-02-20 19:52:08 Traceback (most recent call last):
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/uvicorn/protocols/http/h11_impl.py", line 403, in run_asgi
2025-02-20 19:52:08     result = await app(  # type: ignore[func-returns-value]
2025-02-20 19:52:08              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
2025-02-20 19:52:08     return await self.app(scope, receive, send)
2025-02-20 19:52:08            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/fastapi/applications.py", line 1054, in __call__
2025-02-20 19:52:08     await super().__call__(scope, receive, send)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/applications.py", line 112, in __call__
2025-02-20 19:52:08     await self.middleware_stack(scope, receive, send)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 187, in __call__
2025-02-20 19:52:08     raise exc
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
2025-02-20 19:52:08     await self.app(scope, receive, _send)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/prometheus_fastapi_instrumentator/middleware.py", line 174, in __call__
2025-02-20 19:52:08     raise exc
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/prometheus_fastapi_instrumentator/middleware.py", line 172, in __call__
2025-02-20 19:52:08     await self.app(scope, receive, send_wrapper)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
2025-02-20 19:52:08     await self.app(scope, receive, send)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
2025-02-20 19:52:08     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
2025-02-20 19:52:08     raise exc
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
2025-02-20 19:52:08     await app(scope, receive, sender)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 715, in __call__
2025-02-20 19:52:08     await self.middleware_stack(scope, receive, send)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 735, in app
2025-02-20 19:52:08     await route.handle(scope, receive, send)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
2025-02-20 19:52:08     await self.app(scope, receive, send)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
2025-02-20 19:52:08     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
2025-02-20 19:52:08     raise exc
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
2025-02-20 19:52:08     await app(scope, receive, sender)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
2025-02-20 19:52:08     response = await f(request)
2025-02-20 19:52:08                ^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
2025-02-20 19:52:08     raw_response = await run_endpoint_function(
2025-02-20 19:52:08                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
2025-02-20 19:52:08     return await dependant.call(**values)
2025-02-20 19:52:08            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/home/user/comps/text2sql/src/opea_text2sql_microservice.py", line 47, in execute_agent
2025-02-20 19:52:08     response = await loader.invoke(input)
2025-02-20 19:52:08                ^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/home/user/comps/cores/common/component.py", line 163, in invoke
2025-02-20 19:52:08     return await self.component.invoke(*args, **kwargs)
2025-02-20 19:52:08            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/home/user/comps/text2sql/src/integrations/opea.py", line 119, in invoke
2025-02-20 19:52:08     result = await agent_executor.ainvoke(input)
2025-02-20 19:52:08              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain/chains/base.py", line 217, in ainvoke
2025-02-20 19:52:08     raise e
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain/chains/base.py", line 208, in ainvoke
2025-02-20 19:52:08     await self._acall(inputs, run_manager=run_manager)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain/agents/agent.py", line 1685, in _acall
2025-02-20 19:52:08     next_step_output = await self._atake_next_step(
2025-02-20 19:52:08                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain/agents/agent.py", line 1479, in _atake_next_step
2025-02-20 19:52:08     [
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain/agents/agent.py", line 1479, in <listcomp>
2025-02-20 19:52:08     [
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain/agents/agent.py", line 1507, in _aiter_next_step
2025-02-20 19:52:08     output = await self.agent.aplan(
2025-02-20 19:52:08              ^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain/agents/agent.py", line 502, in aplan
2025-02-20 19:52:08     async for chunk in self.runnable.astream(
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain_core/runnables/base.py", line 3287, in astream
2025-02-20 19:52:08     async for chunk in self.atransform(input_aiter(), config, **kwargs):
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain_core/runnables/base.py", line 3270, in atransform
2025-02-20 19:52:08     async for chunk in self._atransform_stream_with_config(
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain_core/runnables/base.py", line 2163, in _atransform_stream_with_config
2025-02-20 19:52:08     chunk: Output = await asyncio.create_task(  # type: ignore[call-arg]
2025-02-20 19:52:08                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain_core/runnables/base.py", line 3240, in _atransform
2025-02-20 19:52:08     async for output in final_pipeline:
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain_core/runnables/base.py", line 1314, in atransform
2025-02-20 19:52:08     async for ichunk in input:
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain_core/runnables/base.py", line 5312, in atransform
2025-02-20 19:52:08     async for item in self.bound.atransform(
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain_core/runnables/base.py", line 1332, in atransform
2025-02-20 19:52:08     async for output in self.astream(final, config, **kwargs):
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain_core/language_models/llms.py", line 637, in astream
2025-02-20 19:52:08     raise e
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain_core/language_models/llms.py", line 620, in astream
2025-02-20 19:52:08     async for chunk in self._astream(
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/langchain_huggingface/llms/huggingface_endpoint.py", line 348, in _astream
2025-02-20 19:52:08     async for response in await self.async_client.text_generation(
2025-02-20 19:52:08                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/huggingface_hub/inference/_generated/_async_client.py", line 2412, in text_generation
2025-02-20 19:52:08     raise_text_generation_error(e)
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/huggingface_hub/inference/_common.py", line 410, in raise_text_generation_error
2025-02-20 19:52:08     raise http_error
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/huggingface_hub/inference/_generated/_async_client.py", line 2382, in text_generation
2025-02-20 19:52:08     bytes_output = await self._inner_post(request_parameters, stream=stream)
2025-02-20 19:52:08                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/huggingface_hub/inference/_generated/_async_client.py", line 331, in _inner_post
2025-02-20 19:52:08     raise error
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/huggingface_hub/inference/_generated/_async_client.py", line 317, in _inner_post
2025-02-20 19:52:08     response.raise_for_status()
2025-02-20 19:52:08   File "/usr/local/lib/python3.11/site-packages/aiohttp/client_reqrep.py", line 1161, in raise_for_status
2025-02-20 19:52:08     raise ClientResponseError(
2025-02-20 19:52:08 aiohttp.client_exceptions.ClientResponseError: 401, message='Unauthorized', url='https://router.huggingface.co/hf-inference/models/ollama-server:8008'
```

It's complaining about the Huggingface API not being set (401), but the issue actually seems to be that it's expecting a TGI server and it's getting an Ollama one instead.
It should be theoretically possible to rewrite the microservice to be compatible with Ollama API and to not use langchain, but that's too much work for not much gain.

TGI not supported on M1: https://github.com/huggingface/text-generation-inference/issues/690


