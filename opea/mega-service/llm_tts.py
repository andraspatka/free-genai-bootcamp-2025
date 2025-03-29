import os

from comps import MegaServiceEndpoint, MicroService, ServiceOrchestrator, ServiceRoleType, ServiceType
from comps.cores.proto.api_protocol import ChatCompletionRequest
from comps.cores.proto.docarray import LLMParams
from fastapi import Request, Response
from fastapi.responses import StreamingResponse

MEGA_SERVICE_PORT = int(os.getenv("MEGA_SERVICE_PORT", 8888))

SPEECHT5_SERVER_HOST_IP = os.getenv("SPEECHT5_SERVER_HOST_IP", "0.0.0.0")
SPEECHT5_SERVER_PORT = int(os.getenv("SPEECHT5_SERVER_PORT", 7055))

TTS_SPEECHT5_SERVER_HOST_IP = os.getenv("TTS_SPEECHT5_SERVER_HOST_IP", "0.0.0.0")
TTS_SPEECHT5_SERVER_PORT = int(os.getenv("TTS_SPEECHT5_SERVER_PORT", 9088))

LLM_SERVER_HOST_IP = os.getenv("LLM_SERVER_HOST_IP", "0.0.0.0")
LLM_SERVER_PORT = int(os.getenv("LLM_SERVER_PORT", 80))
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "meta-llama/Llama-3.2-1B")

def align_inputs(self, inputs, cur_node, runtime_graph, llm_parameters_dict, **kwargs):
    print(f"align_inputs for node {cur_node}, service type: {self.services[cur_node].service_type}")
    print(f"inputs: {inputs}")
    print(f"kwargs: {kwargs}")
    
    if self.services[cur_node].service_type == ServiceType.LLM:
        # convert TGI/vLLM to unified OpenAI /v1/chat/completions format
        next_inputs = {}
        next_inputs["model"] = LLM_MODEL_ID
        next_inputs["messages"] = inputs["messages"] if "messages" in inputs else [{"role": "user", "content": inputs.get("prompt", "")}]
        next_inputs["max_tokens"] = llm_parameters_dict["max_tokens"]
        next_inputs["top_p"] = llm_parameters_dict["top_p"]
        next_inputs["stream"] = inputs.get("stream", False)  # False as default
        next_inputs["frequency_penalty"] = inputs.get("frequency_penalty", 0.0)
        # next_inputs["presence_penalty"] = inputs["presence_penalty"]
        # next_inputs["repetition_penalty"] = inputs["repetition_penalty"]
        next_inputs["temperature"] = inputs.get("temperature", 0.01)
        inputs = next_inputs
        print(f"LLM next_inputs: {next_inputs}")
    elif self.services[cur_node].service_type == ServiceType.TTS:
        next_inputs = {}
        # Check if we have choices from LLM output
        if "choices" in inputs and len(inputs["choices"]) > 0:
            if "message" in inputs["choices"][0] and "content" in inputs["choices"][0]["message"]:
                next_inputs["text"] = inputs["choices"][0]["message"]["content"]
            else:
                # Fallback if the structure is different
                next_inputs["text"] = str(inputs["choices"][0])
        # If we have content directly
        elif "content" in inputs:
            next_inputs["text"] = inputs["content"]
        # If we have a text field directly
        elif "text" in inputs:
            next_inputs["text"] = inputs["text"]
        # Fallback to the entire input as string
        else:
            print(f"WARNING: Could not find text content in TTS inputs: {inputs}")
            next_inputs["text"] = str(inputs)
            
        next_inputs["voice"] = kwargs.get("voice", "default")
        inputs = next_inputs
        print(f"TTS next_inputs: {next_inputs}")
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
        print("Received request to /v1/audioqna")
        data = await request.json()
        print(f"Request data: {data}")

        chat_request = ChatCompletionRequest.parse_obj(data)
        print(f"Parsed chat_request: {chat_request}")
        
        # Extract the prompt from the messages
        prompt = ""
        if isinstance(chat_request.messages, list) and len(chat_request.messages) > 0:
            if isinstance(chat_request.messages[0], dict) and "content" in chat_request.messages[0]:
                prompt = chat_request.messages[0]["content"]
            elif isinstance(chat_request.messages[0], str):
                prompt = chat_request.messages[0]
        elif isinstance(chat_request.messages, str):
            prompt = chat_request.messages
            
        print(f"Extracted prompt: {prompt}")
            
        parameters = LLMParams(
            # relatively lower max_tokens for audio conversation
            max_tokens=chat_request.max_tokens if chat_request.max_tokens else 128,
            top_k=chat_request.top_k if hasattr(chat_request, "top_k") else 10,
            top_p=chat_request.top_p if chat_request.top_p else 0.95,
            temperature=chat_request.temperature if hasattr(chat_request, "temperature") else 0.01,
            frequency_penalty=chat_request.frequency_penalty if chat_request.frequency_penalty else 0.0,
            presence_penalty=chat_request.presence_penalty if chat_request.presence_penalty else 0.0,
            repetition_penalty=chat_request.repetition_penalty if hasattr(chat_request, "repetition_penalty") else 1.03,
            stream=False,  # TODO add stream LLM output as input to TTS
        )
        
        print(f"LLM parameters: {parameters}")
        
        voice = "default"
        if hasattr(data, "voice"):
            voice = data.voice
        elif isinstance(data, dict) and "voice" in data:
            voice = data["voice"]
            
        print(f"Using voice: {voice}")
            
        result_dict, runtime_graph = await self.megaservice.schedule(
            initial_inputs={"messages": chat_request.messages, "prompt": prompt},
            llm_parameters=parameters,
            voice=voice,
        )

        print(f"Runtime graph nodes: {list(runtime_graph.nodes)}")
        print(f"Result dict keys: {result_dict.keys()}")
        
        # Get the last node in the runtime graph
        last_node = list(runtime_graph.nodes)[-1]
        print(f"Last node: {last_node}")
        
        if last_node in result_dict:
            print(f"Result for last node: {result_dict[last_node].keys()}")
        
        # Check if we have a tts_result in the result_dict
        if last_node in result_dict and "tts_result" in result_dict[last_node]:
            print("Found tts_result, returning audio")
            audio_data = result_dict[last_node]["tts_result"]
            return StreamingResponse(
                iter([audio_data]),
                media_type="audio/wav"
            )
        else:
            # Fallback to returning whatever we have
            print("No tts_result found, returning text response")
            return Response(
                content=str(result_dict),
                media_type="text/plain"
            )

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
