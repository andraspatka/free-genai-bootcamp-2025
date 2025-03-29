import os

from comps import MegaServiceEndpoint, MicroService, ServiceOrchestrator, ServiceRoleType, ServiceType
from comps.cores.proto.api_protocol import ChatCompletionRequest
from comps.cores.proto.docarray import LLMParams
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from comps.cores.mega.utils import handle_message

import sys

MEGA_SERVICE_PORT = int(os.getenv("MEGA_SERVICE_PORT", 8888))

SPEECHT5_SERVER_HOST_IP = os.getenv("SPEECHT5_SERVER_HOST_IP", "0.0.0.0")
SPEECHT5_SERVER_PORT = int(os.getenv("SPEECHT5_SERVER_PORT", 7055))

TTS_SPEECHT5_SERVER_HOST_IP = os.getenv("TTS_SPEECHT5_SERVER_HOST_IP", "0.0.0.0")
TTS_SPEECHT5_SERVER_PORT = int(os.getenv("TTS_SPEECHT5_SERVER_PORT", 9088))

LLM_SERVER_HOST_IP = os.getenv("LLM_SERVER_HOST_IP", "0.0.0.0")
LLM_SERVER_PORT = int(os.getenv("LLM_SERVER_PORT", 80))

LLM_MODEL_ID = os.getenv("LLM_MODEL_ID")
if not LLM_MODEL_ID:
    print("ERROR: LLM_MODEL_ID not defined!")
    sys.exit(1)


def align_inputs(self, inputs, cur_node, runtime_graph, llm_parameters_dict, **kwargs):
    print("align_inputs")
    print(f"inputs: {inputs}")
    print(f"node: {cur_node}")
    if self.services[cur_node].service_type == ServiceType.LLM:
        # convert TGI/vLLM to unified OpenAI /v1/chat/completions format
        next_inputs = {}
        next_inputs["model"] = LLM_MODEL_ID
        next_inputs["messages"] = [{"role": "user", "content": inputs["text"]}]
        next_inputs["max_tokens"] = llm_parameters_dict["max_tokens"]
        next_inputs["top_p"] = llm_parameters_dict["top_p"]
        next_inputs["stream"] = inputs["stream"]  # False as default
        next_inputs["frequency_penalty"] = inputs["frequency_penalty"]
        # next_inputs["presence_penalty"] = inputs["presence_penalty"]
        # next_inputs["repetition_penalty"] = inputs["repetition_penalty"]
        next_inputs["temperature"] = inputs["temperature"]
        inputs = next_inputs
    elif self.services[cur_node].service_type == ServiceType.TTS:
        next_inputs = {}
        next_inputs["text"] = inputs["choices"][0]["message"]["content"]
        next_inputs["voice"] = kwargs["voice"]
        inputs = next_inputs
    return inputs


class AudioQnAService:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        ServiceOrchestrator.align_inputs = align_inputs
        self.megaservice = ServiceOrchestrator()

        self.endpoint = str(MegaServiceEndpoint.AUDIO_QNA)

    def add_remote_service(self):
        tts = MicroService(
            name="tts",
            host=TTS_SPEECHT5_SERVER_HOST_IP,
            port=TTS_SPEECHT5_SERVER_PORT,
            endpoint="/v1/tts",
            use_remote_service=True,
            service_type=ServiceType.TTS,
        )
        llm = MicroService(
            name="llm",
            host=LLM_SERVER_HOST_IP,
            port=LLM_SERVER_PORT,
            endpoint="/v1/chat/completions",
            use_remote_service=True,
            service_type=ServiceType.LLM,
        )
        self.megaservice.add(llm).add(tts)
        self.megaservice.flow_to(llm, tts)


    async def handle_request(self, request: Request):
        print("handle_request")
        print(f"request: {request}")
        data = await request.json()

        chat_request = ChatCompletionRequest.parse_obj(data)
        prompt = handle_message(chat_request.messages)
        parameters = LLMParams(
            max_tokens=chat_request.max_tokens if chat_request.max_tokens else 1024,
            top_k=chat_request.top_k if chat_request.top_k else 10,
            top_p=chat_request.top_p if chat_request.top_p else 0.95,
            temperature=chat_request.temperature if chat_request.temperature else 0.01,
            frequency_penalty=chat_request.frequency_penalty if chat_request.frequency_penalty else 0.0,
            presence_penalty=chat_request.presence_penalty if chat_request.presence_penalty else 0.0,
            repetition_penalty=chat_request.repetition_penalty if chat_request.repetition_penalty else 1.03,
            stream=False,
            chat_template=chat_request.chat_template if chat_request.chat_template else None,
            model=chat_request.model if chat_request.model else None,
        )
        result_dict, runtime_graph = await self.megaservice.schedule(
            initial_inputs={"text": prompt},
            llm_parameters=parameters,
            voice="default",
        )
        last_node = runtime_graph.all_leaves()[-1]
        response = result_dict[last_node]["tts_result"]

        return response


    def start(self):
        self.service = MicroService(
            self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint=self.endpoint,
            input_datatype=ChatCompletionRequest,
            output_datatype=Response,
        )
        self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])
        self.service.start()


if __name__ == "__main__":
    audioqna = AudioQnAService(port=MEGA_SERVICE_PORT)
    audioqna.add_remote_service()
    audioqna.start()
