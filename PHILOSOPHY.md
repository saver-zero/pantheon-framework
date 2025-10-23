# The Glass Box Process: Beyond the Black Box

The current generation of AI tools are evolving rapidly, and they feel magically brilliant. There's a constant flux of model improvements and new papers being published to improve AI utilization. Even at an individual level, many people are developing and sharing their own way of utilizing AI. But after a while, it can often feel like a constant struggle wrestling with a flawed, amnesiac tool. It is evident that **how** we work with AI is becoming critical, yet it is the least tangible aspect.

With rapid development of AI agents, there's a fundamental shift in paradigm where the output is becoming a commodity - whether it's code, document, or media. We challenge the notion that AI is a magical brilliant blackbox. Instead, we believe that the role of human operator has evolved into creating a transparent Glass Box Process to direct AI. In the new era of AI, the process of directing AI is becoming the new artifact.

The Glass Box Process's philosophy is simple: **the output of AI is not where the creative value is - the process of how the output was created is where the most value is.** This is achieved by transforming the very **process of creation** into a tangible, **engineerable artifact**, which is just as important as the final output.

## Understanding AI

Our understanding of AI has not caught up to the rapid development of AI yet. The Black Box approach in working with AI creates significant risks when we rely on the output from AI without understanding how and why the output was created. Even though the industry is pursuing AI models that are inherently transparent - the Glass Box AI - AI is becoming even more sophisticated and complex. In addition to pursuing inherently transparent models, we must also build a Glass Box Process around it as an essential derisking layer.

At a base level, we must acknowledge that AI is a **goal-oriented probabilistic reasoning engine**. This is one of the first area where developers can run into frustration, with AI not following instruction. Developers are used to having deterministic behaviors - as the code we write is deterministic. However, AI is not deterministic, it's probabilistic.

### Probabilistic
What does it mean when AI is probabilistic, and how does it affect us? Simply put, it's a pattern matcher. It will try to match the most likely pattern, based on its training data. The most obvious example is the *full wine glass* problem. It is difficult to instruct AI to create an image or video of a full wine glass, upto the brim of the glass. This is because the vast majority of data it's been trained on show a full wine glass being, not actually full upto the brim. It does not understand physics nor the actual intent of the prompt, it is simply pattern matching the most likely pattern. When it comes to development, this can result in AI writing 'hacky' code - either because of the existing code base, or because of its training data from online snippets (as opposed to high quality closed-source production scale architecture code).

### Reasoning
The other aspect of AI is that it's a reasoning engine. It tries to reason and explain to itself why it must take or not take a certain action. If it deems something as not important, even when explicitly instructed, it will simply not perform the task. Frustrated developers may have experienced this, asking why AI did not do something given explicit instruction, and it will do a great job explaining the reason why.

### Goal Oriented
Lastly, AI is very goal oriented, making it very eager to do whatever it takes to achieve the goal - in the most efficient way possible. Coupled with the probabilistic and reasoning behavior, this can result in AI doing something completely different than what the human operator has intended. At best, it will result in frustration, but at worst, it can result in unintended output that goes undetected, creating significant risk because it had a different goal than what the human user has intended. Some examples of these include hallucination, generating fake data, creating hard coded passing tests with mock data, or saving and committing confidential informations like API keys.

## The Glass Box Process

The goal of the Glass Box Process is to transform abstract AI workflow into a tangible artifact that is **auditable, iterable, reliable, and portable**.

### Auditable
It is not enough for merely the output of AI to be auditable. A true Glass Box Process must provide a way to audit AI's chain of logic - the **reasoning** and **goal-oriented** part of the *goal-oriented probabilistic reasoning engine* - before the output is created. By intercepting the reasoning and the goal before the output is created, we can course-correct AI and ensure its goals align with our intention.

### Iterable
Unless the process is iterable, there will be no path forward. An abstract process, like improvements via adhoc prompts or a loose description of a process, is not iterable. The Glass Box Process must turn the process into a concrete artifact that can be systematically version-controlled, tested, and iterated to break the status-quo.

### Reliable
The Glass Box Process must be reliable. AI agents are non-determinstic by nature, which makes reliablity and consistency challenging. Unreliable and inconsistent process amplifies the non-deterministic nature of AI agents, significantly increasing the risk of AI output integrity. To counter balance this, the Glass Box Process must be inherently reliable, leveraging the latest understanding of AI to put guardrails on the unpredictable nature of AI.

### Portable
The Glass Box Process is a non-negotiable process around AI to ensure transparency. Locking such critical process into a single provider or platform puts the industry behind and increases the overall risks. The Glass Box Process must be portable across different providers, platforms, and models - to ensure rapid understanding of fast-evolving AI and foster wider adoption. A portable process is also shareable - allowing the contributions to benefit the wider industry.

## Benefits
Achieving the Glass Box Process delivers tangible benefits beyond philosophical idealogy.

### Control
The Glass Box Process gives control back to the human operator for an effective and pragmatic human-in-the-loop system. We no longer have to *fight* against AI to get the desired output. *To fight is an implicit acknowledgement of loss of control*. Rather, by making AI's reasoning chain auditable, we retain the control to direct AI, ensuring its output always aligns with our intention.

### Adaptability
The field of AI is advancing at an unprecedented rate. With constant model updates and new learnings about AI, *the half-life of the best workflow is short lived*. Having an adaptable process that can react quickly to the latest breakthrough is crucial to stay competitive. The Glass Box Process's iterable and portable nature comes with inherent adaptability.

### Repeatability
Unpredictable process significantly hinders velocity. The Glass Box Process's reliability allows for a repeatable process with consistent output, providing a competitive advantage with high velocity and quality.
