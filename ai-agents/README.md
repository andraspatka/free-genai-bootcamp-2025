# Atomic Agents Examples

The goal is to reimplement the Song vocabulary agent from: https://gist.github.com/kajogo777/df1dba7f346d3997c38ec0261422cd81

Using either a framework or implementing everything from scratch.

## Framework

Atomic agents has gotten a lot of love lately, as it aims to be simple and developer friendly.
There have been a lot of criticism surrounding langchain as their implementation seem to be convoluted and hard to understand.

Atomic agents seems to have been created as an answer for difficult to understand frameworks.

https://github.com/BrainBlend-AI/atomic-agents

## Implementation and issues

### Stopping criteria

The biggest question in the beginning for me was how to implement a stopping criteria.
I added an infinite loop with a counter fallback (to avoid a truly infinite loop) to handle the case where the model doesn't stop generating.
The framework didn't seem to provide something like this, I was halfway expecting the `agent.run` method to do multiple iterations until it determines that the task is done.
It instead does just 1 iteration, but that also makes sense as in this case the control is fully in the developer's hands to determine when the task is done.

I settled on just asking the model to give a specific input when it is done. I added this initially to the system prompt only, but that wasn't reliable enough.
I ended up adding it to multiple places, and also constrainting the number of words that it should generate out, as sometimes it just kept on going.


I tried also to tell the model to give either as prefix to the output "STEP" "VOCABULARY" or "EXIT". It didn't always give the "EXIT" part and it was hard to convince the model to do so. I realised though, that "EXIT" is redundant, and if "VOCABULARY" is in the output, then that means the task is already done.

### Output formatting

I used initially a custom output format, but the model sometimes randomly spat out JSON, so I ended up requesting JSON to make this also more reliable.
I learned after, that the atomic_agents framework adds a couple of output_instructions by default and this was causing issues. There's no straight forward way to remove them, but I have added an additional output_instruction which defines that follow up instructions should be ignored. 

I also added some error handling in case the model doesn't output the result in the appropriate format. In that case the prompt is adjusted to provide feedback and provide the log format again.

### Temperature

Tweaking the temperature parameter helped a lot, as this made the agent much more determenistic. A value close to 0 should be good in this case, as the model should follow specific instructions well, but still it should be a little bit creative with the words to choose and the example sentences.

### Tool implementations and tool use

The tool use worked VERY well, I implemented the tools once and didn't bother with them again. The agent was able to select the appropriate tool and use it perfectly.
I was very impressed by this.

The only complaint I had about tool use, was that the code was very verbose. A lot of things had to be defined, and this turned a simple function with 4 lines into ~100 lines of code.
But this can also be because of my inexperience with the framework.

### Model

I used initially `gpt-4o-mini` but this requires a bit of hand holding.
The full model `gpt-4o` performed much better and was much more reliable.

After further testing and tweaking `gpt-4o-mini` was also fine, it just required additional retry logic and explanations to get it right in case it got stuck our didn't provide the output in the appropriate format.

### Text degeneration

Using low values of temperature could cause the model to get stuck and start repeating the same things over and over again.
To combat this, a retry logic was implemented to retry twice in case the amount of steps were exceeded.
The step count was also reduced, as realistically the task should be completed in a few steps at most.

### Conclusion

I was very impressed by the framework. It's still very new and some more documentation would be nice, but it's very simple to use and after a bit of searching it becomes very intuitive and obvious where things should be implemented.
