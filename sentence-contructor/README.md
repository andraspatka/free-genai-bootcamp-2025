# Sentence constructor

Business goal: A chat agent that acts as a teaching assistant to guide students from translating a target English sentence into Japanese. The teaching assistant is not there to provide the direct answer, only guidance.

## Technical uncertainty

0. How well do the AI-Powered Assistants know the target language (Italian)?
1. How well can an AI-Powered Assistant perform a very broad task?
2. Would a very broad task be better performed by dividing it into subtasks with specialized agents?
3. Does using an AI-Powered Assistant make for a good place to rapidly prototype agents?
4. How could we take the agent we built in an AI-Powered Assistant and reimplement it into a stack that allows for direct integration into our platform?	
5. How much do we have to rework our prompt documents from one AI-Powered Assistant to another?
6. What prompting techniques can we naturally discover working in the confines of an AI-Powered Assistant?
7. Are there any interesting innovations unique to specific AI-Powered Assistants for our business goal?
8. What were we able to achieve based on our AI-Powered Assistant choice and our hardware, or budget limitations?

## AI-Powered Assistant of choice

The chosen AI-Powered Assistant has to be one that is based on an open source or an open weight model (from now on referred to as just "open model"). It's not expected to do fine tuning on the model so open weight models are also fine. The initial approach to the project is to use an inference API and therefore to outsource the responsibility of hosting, securing and maintaining the infrastructure to a specialized provider. Later on the possibility of self hosting could also be evaluated, but it depends on the operating costs of the used API to determine whether a capital expense to hardware and operation expense going to additional engineers is worth the money and the effort.

Open models are also benefitial from the developer experience point of view, as with a small investment in a capable machine; tuned-down versions of these models are also runnable locally.

### AI-Powered Assistant evaluation - process

Language evaluation (does this LLM even know Italian?):
```
prompt mistral:
Give me a sample sentence that could be used as a benchmark for determining if English -> Italian translation is correct

output:
Here is a sample sentence that can be used as a benchmark for determining if an English to Italian translation is correct:

English: "The quick brown fox jumps over the lazy dog."
Italian: "La volpe marrone veloce salta sopra il cane pigro."
This sentence is often used for testing because it contains all the letters of the alphabet and a variety of grammatical structures.

-> Another sentence: She sells seashells by the seashore. -> Lei vende conchiglie sulla riva del mare.
```

Prompt to the LLMs to be evaluated:
```
Translate these 2 sentences into italian:
- The quick brown fox jumps over the lazy dog.
- She sells seashells by the seashore.
Respond in italian
```

The expectation is that the LLMs provide a correct translation for these 2 sentences. The correct translation was obtained by a reputable translation web app (deepl.com).

### AI-Powered Assistant evaluation - result

- ~~Meta AI (meta.ai)~~
    - Open model: YES
    - Accessible from my country: NO -> Won't be used
- ~~Mistral AI (https://chat.mistral.ai/)~~
    - Open model: YES
    - Knows Italian: YES (La veloce volpe marrone salta sopra il cane pigro. Lei vende conchiglie in riva al mare.)
    - Accessible from my country: YES
    - Reasoning: YES but not free
- **Deepseek (https://chat.deepseek.com/)**
    - Open model: YES
    - Knows Italian: YES (La veloce volpe marrone salta sopra il cane pigro. Lei vende conchiglie in riva al mare.)
    - Accessible from my country: YES
    - Reasoning: YES
- ~~Anthropic Claude:~~
    - Open model: NO
- ~~ChatGPT:~~
    - Open model: NO

The winner is "Deepseek" as it is an open model, it knows Italian, it's accessible from my country and it has reasoning capabilities which are included in the free plan. The reasoning capability is very useful in order to see what the model is doing behind the scenes, and I suspect it will also help with designing a proper prompt.
