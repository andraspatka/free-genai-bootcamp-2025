# Sentence constructor

Business goal: A chat agent that acts as a teaching assistant to guide students from translating a target English sentence into Japanese. The teaching assistant is not there to provide the direct answer, only guidance.

## Technical uncertainty

These questions were answered after getting experience with the prompt and how different sizes of the chosen LLM perform with it.

0. How well do the AI-Powered Assistants know the target language (Italian)?
-> Each model was evaluated separately. They all know Italian well.
1. How well can an AI-Powered Assistant perform a very broad task? 
-> The full model (available from the provider) performs very well on the full prompt and can handle complex topics. Much smaller models struggle with this and require smaller tasks.
2. Would a very broad task be better performed by dividing it into subtasks with specialized agents?
-> Yes, but depends on the LLM size, 1.5B models perform specific tasks okay and 14B models (max that I could test) perform more complex tasks also okay; but still can't handle the full prompt
3. Does using an AI-Powered Assistant make for a good place to rapidly prototype agents?
-> Yes, as there is no setup required and iterating is very fast. Deepseek R1 makes this even easier with the reasoning feature to provide effectively feedback on the prompt. It's less of a black box.
4. How could we take the agent we built in an AI-Powered Assistant and reimplement it into a stack that allows for direct integration into our platform?
-> Use Deepseek's API or host the model locally with Ollama and use Ollama's API to send prompts and receive answers from the app.
5. How much do we have to rework our prompt documents from one AI-Powered Assistant to another?
-> None at all. The full prompt worked very well with Mistral as well
6. What prompting techniques can we naturally discover working in the confines of an AI-Powered Assistant?
-> I discovered "Enforcing Guardrails with System Prompt" (https://www.promptingguide.ai/models/mistral-7b.en#enforcing-guardrails-with-system-prompt)
Also "Role Playing" (https://www.promptingguide.ai/models/gemma.en#role-playing)
The prompt was also Zero-shot as there were no examples provided
7. Are there any interesting innovations unique to specific AI-Powered Assistants for our business goal?
-> The free offer of reasoning with Deepseek is *very* nice
8. What were we able to achieve based on our AI-Powered Assistant choice and our hardware, or budget limitations?
-> Summary: AI-Powered assistant: full prompt works very well. Local hardware, max 14B model and prompt needs to be split up to multiple parts

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
- Mistral AI (https://chat.mistral.ai/)
    - Open model: YES
    - Knows Italian: YES (La veloce volpe marrone salta sopra il cane pigro. Lei vende conchiglie in riva al mare.)
    - Accessible from my country: YES
    - Reasoning: YES but not free
    - Will be evaluated in addition to Deepseek
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

Mistral will also be evaluated as it ticks almost all of the boxes as well. The only downside is that there is no reasoning available, but the prompt could be iterated over with Deepseek (used as a "debugger") and then tried out as-is with Mistral.
