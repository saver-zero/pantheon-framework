# Pantheon Framework

## Overview
Pantheon Framework makes AI workflows that are truly custom and work - reliable, auditable, iterable, and portable. Instead of fighting with the AI, Pantheon's structured approach hands the control back to you for consistent output with a repeatable process.

Pantheon Framework aims to solve the following problems:
* **"You're absolutely right!" problem:** AI agreeing with you, but continuing to not follow instructions and make the same mistake, resulting in hours of wasted work and late night rework.
* **Agent overload:** Having too many agents to choose from, with pre-built generic agents not customized for the project at hand.
* **Rigid workflow:** A workflow that doesn't quite fit your needs and is difficult to customize. Pantheon Framework recognizes that there is no one-size-fits-all solution.
* **Non-portable customization:** Your custom prompts, context, and commands stuck in a single platform. With rapid advancement of AI, being able to freely explore other providers and models is non-negotiable.

Pantheon Framework is a reference implementation of the [Glass Box Process](PHILOSOPHY.md), turning process into a tangible artifact. We believe that **the output of AI is not where the creative value is - the process of how the output was created is where the most value is.** The custom workflow that you've worked hard to create and optimize should be owned by you, portable to any providers and shareable with anyone you wish.

**Pantheon Framework itself was built with Pantheon,** showcasing its capabilities through self-bootstrapping: the initial `Pantheon Dev` team was created using `Pantheon Team Builder`, and the rest of Pantheon Framework was then built using that `Pantheon Dev` team. This recursive development served as the ultimate test bed for the framework - building the entire capability of the framework with the framework itself.

## Core Use Cases
Pantheon Framework has 2 core use cases - software development and custom team creation - and ships with 2 teams supporting these two core use cases.

### Use Case 1: Software Development
For software development, Pantheon Framework comes with `Pantheon Dev` team. `Pantheon Dev` team comes with [Glass Box Processes](PHILOSOPHY.md) tailored for software development and a set of core AI agents. In addition, `Pantheon Dev` team is configured to create additional set of custom AI agents specific to the project at hand.

`Pantheon Dev` team has:
* **Custom specialized agents:** With truly custom agents that match your project needs, there is no need to choose from pre-made agents or manually create agents yourself.
* **Configurable process:** Configure the process at any time - whether to draft commit message, auto-commit, enable progress logs, read documentation, update documentation, create diagrams, run TDD, etc... It ships with a set of pre-configured profiles to choose from, and supports customization of common aspects of the software development cycle, with changes reflecting immediately.
* **Iterable workflow:** No more fighting with the AI. Provide feedback and run a retro analysis for actionable insights to make immediate changes to the workflow.
* **Core agents:** Pantheon ships with a minimal set of core agents to kick-off and support your project - create the architecture guide, perform code reviews, run retro, and make concrete improvements to your process.

Working with `Pantheon Dev` team is simple - just use natural language. The framework handles the complexity of the system, while still providing transparent AI workflows.

Here's what typical interactions look like:
```
@pantheon-dev, kick off my travel planner project based on @travel-planner-notes.txt
> frontend-engineer is created and kick-off ticket for arch guide and backlog tickets created

@tech-lead, work on the kick-off ticket KOT01
> initial architecture guide is created, and a set of initial backlog tickets created and assigned

@frontend-engineer, create a plan for ticket T012
> Modular multi-phase plan is created, reflecting custom profile configs for testing, documentation, diagrams, committing, etc...

@frontend-engineer, implement ticket T012. Work on only 2 phases at a time
> Ticket is implemented per plan, with clear progress notes on decisions outlined

@tech-lead, create a ticket to save travel plan histories into local storage
> Ticket is created, along with documentation and file references relevant to the work
```

And when you run into issues, you can make concrete improvements to the process:
```
You did not clean-up the temporary files and committed them. You should always clean-up temporary files. Log this feedback.
> The user's feedback along with the context (what happened before, the agent behavior, etc...) is captured.

@retro create a retro report based on the feedbacks so far
> retro agent reviews all submitted feedbacks and creates actionable retro report with suggestions to update the ticket plan template

@pantheon-dev, update the ticket plan template to ensure temporary files are always cleaned up before committing per @RR1-retro-report.md
> pantheon-dev agent adds a step to clean-up temporary files to the ticket plan template, as suggested by @RR1-retro-report.md.
```

Over time, `Pantheon Dev` team will evolve to become your own custom tailored team to fit your exact style and needs.

More details about `Pantheon Dev` team is available in the [Pantheon Dev Team README](pantheon/_templates/pantheon-teams/pantheon-dev/README.md).

### Use Case 2: Custom Team Building
`Pantheon Team Builder` enables the creation of new teams and workflows with no code involved. Simply describe what you want in natural language, review the generated markdown text files, and make adjustments as needed. You can create any team you need - software development, content creation, research, analysis, or any custom workflow. The framework will handle the complexity of the system and `Pantheon Team Builder` will create your own custom team of specialized agents with transparent processes that are reliable, auditable, iterable, and portable.

Use `Pantheon Team Builder` when:
* You have a specific workflow in mind you want to use
* You want to build a new team that will generate content like idea docs, plan, blog post, etc..

Creating a new team will go through the following core phases, all of which are achieved through **natural language** and **markdown text** files:
1. Initial Team Blueprint creation with high level context and structure
2. Artifact designing - defines the output (i.e. plan, document, content) and the process around it
3. Agent designing - defines the agents creating the artifacts and the workflow it follows
4. Profile designing - evaluation and designing of any custom profiles or configs needed
5. Profile/Agent/Artifact building - Building of the final profile/agents/artifacts based on the design.

At each phase, you'll have a chance to review the design, and you can either update the design directly or provide feedback to the agents to update it.

Below are some examples of what typical interactions with `Pantheon Team Builder` would look like.

**With a specific workflow in mind:**
```
My current development workflow involves having a list of features I want, asking the agents to come up with a list of clarifying questions that I'll answer, and continue refining the plan until there's no more clarifying questions. Then I break this up into manageable chunks, and have the agent implement it one by one, reminding it of the initial plan and context. @pantheon-team-builder create a Team Blueprint for this.
> Initial team blueprint with context is created by pantheon-team-builder. The team blueprint contains instructions for next steps. Make any adjustments as needed directly on the doc and move on to the next step.

@artifact-designer, design the artifacts described in team blueprint TB01. I want to make sure the list of clarifying questions is not overwhelming, with clear priorities and limited to 10 questions max.
> artifact-designer outlines the artifacts that the team will support and updates the team blueprint. Make any adjustments needed or ask the artifact-designer to update it with feedback.

@agent-designer, design the agents for TB01.
> agent-designer outlines the minimal set of agents the team will have to support the process.

@profile-designer, design the profile for TB01.
> profile-designer suggests the profile and configs needed, if any.

(after reviewing the blueprint)
@profile-designer, create the team profile from @TB01-clarifying-team.md
> profile-designer creates the team-profile.yaml file

@agent-designer, create the agents from @TB01-clarifying-team.md
> agent-designer creates the agents

@artifact-designer build the artifacts from @TB01-clarifying-team.md
> artifact-designer builds the artifacts and the processes around it.

Result: A custom team package with specialized agents based on your workflow - iterable and shareable.
```

**Building a new team:**
```
(start discussing the rough idea first with the main LLM)
I want to start a food blog/vlog. I like trying new food, so I want to explore restaurants around the area - and create a blog and a short video (i.e. shorts, tiktok, reels) about it. I'll probably need to research which restaurants to try first, and come up with a unique theme and style as that topic is saturated.

(after idea is fleshed out more)
Ok, let's go with that idea. Have @pantheon-team-builder create a team blueprint for this.
> pantheon-team-builder creates the team blueprint with high level context and structure

(rest is same as above, follow the suggested next steps in the team blueprint to design, review, and create the team)

Result: A food influencer team package with specialized agents and platform-specific content creation. Your content stays organized on your device, with workflows that are iterable, portable, and auditable - giving you freedom to explore various LLM providers.
```

For software development, we recommend trying the `Pantheon Dev` team first to see if the existing configurations with minor customization will suit your needs.

More details about `Pantheon Team Builder` is available in the [Pantheon Team Builder README](pantheon/_templates/pantheon-teams/pantheon-team-builder/README.md).

## Demo Projects
Below are some demo projects with Pantheon Framework in action. The trip planning example was selected based on OpenAI's recent [demo of Agent Builder](https://www.youtube.com/watch?v=44eFf-tRiSg), which uses travel itinerary planning as a reference example.

### Demo 1 - Pantheon Dev Team
What it looks like to create an LLM backed trip planner using different `Pantheon Dev` team profiles.
* [Vibe Coding Profile](https://github.com/saver-zero/pantheon-framework-demo/tree/main/pantheon-vibe-coding) - The minimal profile to support the Glass Box Process with auto-commit and progress logs.
* [Check-Everything Profile](https://github.com/saver-zero/pantheon-framework-demo/tree/main/pantheon-check-everything) - The most comprehensive profile with Test-Driven-Development, code review, up-to-date documentation and diagrams. For this specific demo, [OpenCode](https://github.com/sst/opencode) was used mid-project with `Qwen3 Coder 480B A35B` model from NVIDIA, demonstrating the ability to switch providers mid-project.

### Demo 2 - Custom Software Development Workflow

What it looks like to:
1. Create a custom development team with a specific workflow in mind
2. Use the created custom team to build an LLM backed trip planner.

The demo teams were built using reference workflows shared in real Reddit posts, where posters shared their own workflow for development to contribute to the community.

Here's what creating the teams looked like:
```
@pantheon-team-builder Create a team based on @ascii-planning-workflow.md

@pantheon-team-builder Create a team based on @dead-simple-workflow.md

@pantheon-team-builder Create a team based on @production-ready-workflow.md
```

* [ASCII Planning](https://github.com/saver-zero/pantheon-framework-demo/tree/main/ascii-planning) - Uses ASCII wireframes for planning.
* [Dead Simple Workflow](https://github.com/saver-zero/pantheon-framework-demo/tree/main/dead-simple-workflow) - Keeps the project context updated with bite-size implementation TODOs.
* [Production Ready Workflow](https://github.com/saver-zero/pantheon-framework-demo/tree/main/production-ready-workflow) - Creates a single source of truth PRD to work off of, with a review process to evaluate the implementation against the original PRD.

### Demo 3 - Creating New Teams

#### Travel Itinerary

This demo shows what it's like to create and use a non-development team - a simple trip planning team. It used the [transcript](travel-idea.txt) from OpenAI's recent [demo of Agent Builder](https://www.youtube.com/watch?v=44eFf-tRiSg) to create the `Travel Itinerary` team.

[Travel Itinerary](https://github.com/saver-zero/pantheon-framework-demo/tree/main/travel-itinerary) - What it looks like to create a non-development team that generates travel itinerary and flight options.
```
@travel-idea.txt is a transcript from a demo that sets up an agent for creating travel itinerary.
Let's build upon the idea. Let's create a team that does a bit more helpful things. Let's create a team that creates a
travel itinerary given a natural user input. We still want to keep it lightweight, so each itinerary should focus on one
destination or trip. what should this team focus on?

ok let's have @pantheon-team-builder create the team for this - let's keep the team and artifact simple so
that it's easy to use
```

#### Receipt Analysis

This demo shows what it's like to create and use a non-development team - a simple `Receipt Analysis` team. The team will take a look at the set of receipts given and do an analysis. The project is started with just a vague idea of having a receipt analyzer team, showing how to go from a rough idea -> team creation -> usage of the team, with some minor modifications in between.

[Receipt Analysis](https://github.com/saver-zero/pantheon-framework-demo/tree/main/receipt-analysis) - What it looks like to create a non-development team that analyzes receipts and provides spending insights.
```
> I am thinking of creating a receipt-analyzer team. I'll give it a set of receipt images and ask it to analyze it - grocery
receipts, amazon receipts, things of that nature where you don't really get visibility into your spending just from a credit
card statement. What kind of analysis would be useful and helpful?
 
<...>

The receipt-analysis team (TB01) is now fully implemented and ready to use! You can now start using the team to analyze receipt
images and generate spending insights reports. Would you like to test it out with some sample receipts?
```

## Getting Started

### Prerequisites

Pantheon requires Python 3.11 or higher. Using a virtual environment is recommended to isolate dependencies:

```bash
# Create and activate a virtual environment
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### Installation

Install Pantheon from the latest release

```bash
pip install pantheon_framework-0.1.1-py3-none-any.whl

# Verify installation
pantheon --help
```

### Initialization

Navigate to your project directory and run the initialization command:

```bash
cd your-project
pantheon init
```

The initialization script will guide you through:

1. **Team Selection**: Choose between `Pantheon Dev` (for software development) or `Pantheon Team Builder` (for creating custom teams)
2. **Profile Selection**: Select a team profile if available (e.g., "vibe-coding", "check-everything")
3. **Agent Installation**: Install team agents to `.claude/agents/` for direct invocation
4. **Protocol Integration**: Append team-specific instructions to `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`
5. **Directory Scaffolding**: Create `pantheon-teams/` and `pantheon-artifacts/` directories

After initialization, your project will have:
```
your-project/
├── .pantheon_project          # Active team configuration
├── .claude/agents/            # Installable team agents
├── pantheon-teams/            # Team definitions and processes
└── pantheon-artifacts/        # Generated artifacts and outputs
```

It is recommended to check-in pantheon-teams/ and pantheon-artifacts/ to ensure the team updates and artifacts are version-controlled. If you'd like to separate these from your main repo, you can change the default directories in .pantheon_project and have them separately version controlled, or .gitignore them.

You're now ready to start working with your Pantheon team! For next steps, see the installed team's team-specific README:
* [Pantheon Dev Team README](pantheon/_templates/pantheon-teams/pantheon-dev/README.md)
* [Pantheon Team Builder README](pantheon/_templates/pantheon-teams/pantheon-team-builder/README.md)

## How Pantheon Framework Works

While Pantheon Framework is easy to use with natural language and pure text files, there are key components to the system that enable the framework to abstract out the complexity. Below is a quick overview of the core components for those interested.

<details>
<summary><b>Core Framework Components</b> (click to expand)</summary>

Pantheon Framework is an implementation of [Retrieval-Augmented Execution](reference/retrieval-augmented-execution.md) (RAE), a new concept we developed to ensure **reliable** and **iterable** AI workflows. RAE builds upon insights from [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401) and [Routine: A Structural Planning Framework](https://arxiv.org/abs/2507.14447), extending these ideas into a practical and executable application. Pantheon's approach also aligns with concepts from [ReasoningBank](https://arxiv.org/abs/2509.25140), leveraging tangible team processes for **iterative** AI workflow improvements.

### Team Package
At its core, Pantheon Framework operates on the concept of a **team package**, consisting of **team agents** and **team processes**.

Team processes are further broken down into distinct routine (structured instruction), schema, and templates - converting an abstract concept of a `process` into tangible and modular elements. Team agents follow the routine to execute a team process and create an artifact. This process of following instructions, executing a process, and creating an artifact is defined as a single **workflow**. Each aspect of the workflow is a concrete item - the routine, process schema, and process template.

By creating and making improvements to these concrete elements, Pantheon Framework is able to create **portable** teams that can learn and **iterate**. The agent prompt, routine, schema, and template all become part of the `ReasoningBank` that make up a team. This is what enables the `Pantheon Team Builder` to act as the meta-team to create new teams and workflows, along with a customizable `Pantheon Dev` team that can evolve based on feedback. 

For example, the `tech-lead` agent of the `Pantheon Dev` team can `create-architecture-guide` based on project context and tech stack, following the process specific routine with clear data contract schema and structured template, resulting in a consistent and predictable architecture guide. The `tech-lead` can also `create-ticket` with the right context and references for other agents to work on.

Pantheon Framework's entire team package - agents, processes, and artifacts - are *customizable text files* - markdown, jsonnet schema, and Jinja2 template files. The core Pantheon framework code does not need to be changed to update a team. Each customizable component of the team package plays a distinct role in enabling reliable, iterable, and portable workflows.

To learn more about team packages, read the [team package overview](pantheon-artifacts/docs/team-packages/overview.md).

### Agent
Agent definitions (`agents/*.md`) define **WHO** the agent is and **WHAT** capabilities they possess. They establish persona, expertise, and working style without containing process-specific workflows or data contracts. Agent definitions are **process-agnostic**. They describe general capabilities that apply across multiple workflows, not step-by-step instructions for specific processes. It contains what workflows they have access to, but not the details of each workflow.

To learn more about agents, read the [agent documentation](pantheon-artifacts/docs/team-packages/agents.md).

### Process
The creation of artifact (i.e. plan, document, content) is driven by a process that agents can execute. A process contains:
* Routine - human readable markdown instructions for executing a process
* Schema - a jsonnet schema file enforcing the data contact
* Template - a Jinja2 template that gets rendered as the final artifact from the agent provided data

#### Routine
Routine is a structured list of instructions for the agent to execute a process.

By having structured instructions separate from the agent's core prompt, we can better [manage the agent's cognitive load](pantheon-artifacts/docs/routine-system/cognitive-load-management.md).

To learn more about routines, read the [routine philosophy](pantheon-artifacts/docs/routine-system/philosophy.md) and [authoring practices](pantheon-artifacts/docs/routine-system/authoring-practices.md).

#### Schema
Schema is the guardrail that enforces the data contract. Whereas a routine guides the agent's reasoning chain on **HOW** to execute a process, the schema defines **WHAT** data to provide to execute a process, and enforces it.

To learn more about schema, read the [schema guide](pantheon-artifacts/docs/team-packages/schemas-guide.md)

#### Template
Template plays a key role in Pantheon Framework. It separates out the formatting and presentation from the agent, enabling it to focus only on the core content of the artifact. It also ensures consistent structured ouput. Pantheon Framework has 2 templating systems - jsonnet to power schemas, and Jinja2 to power the rest. Templates are heavily used in process, from the artifact itself to the routine that agents use to execute a process. As it plays a critical role in the system, there is extensive documentation available.

To learn more about template, read:
* [Template overview](pantheon-artifacts/docs/templating-system/overview.md)
* [Built-in variables](pantheon-artifacts/docs/templating-system/built-in-variables.md)
* [jsonnet schema guide](pantheon-artifacts/docs/templating-system/jsonnet-schemas-guide.md)
* [Jinja2 template guide](pantheon-artifacts/docs/templating-system/jinja2-templates-guide.md)
* [Routine template](pantheon-artifacts/docs/templating-system/routine-templates.md)
* [Template composition](pantheon-artifacts/docs/templating-system/template-composition-patterns.md)

#### Artifact
The end output of a process is an artifact - which can be a plan, document, or content. Once created, artifacts can be retrieved or updated. Artifacts can have sections - which allows the retrieval and updating of specific section, along with a prepend/append option for updating.

This is meaningful for 2 reasons:
1. **Context engineering:** It injects the right context at the right time, core to [Retrieval-Augmented Execution](reference/retrieval-augmented-execution.md). Instead of having a monolitic agent prompt or requiring the agent to read a huge documentation, you can simply instruct an agent to retrieve a specific section of an artifact. Contrary to what it looks like, an agent cannot "read" just a specific part of a doc without the help of a tooling (i.e. using `sed`). When given a path to the file, the agent either ends up reading the whole part of the doc, or attemps to read part of the doc with a best-faith effort reading piece by piece. However, with the ability to get just the exact section of the doc, the agent can have just-in-time context. An example of this is retrieving the documentation standards section of the architecture guide with `pantheon execute get-architecture-guide --sections documentation-standards`.
2. **Token management:** An agent cannot be guaranteed to simply prepend or append to a doc. The agent may end up reading the entire doc and rewriting the entire doc. By having native support for prepending/appending, Pantheon framework provides a guranteed tool to perform a true prepend/appent operations, saving on tokens.

To learn more about artifacts, read about [CLI commands](pantheon-artifacts/docs/cli-interface/commands.md) and [process model overview](pantheon-artifacts/docs/process-model/overview.md).

To learn more about the overall Pantheon Framework system, refer to the [framework README](pantheon-artifacts/docs/README.md).

</details>

## Common Questions
**Q: Does Pantheon Framework dictate a certain process?**

A: No, Pantheon Framework is opinionated about having a [Glass Box Process](PHILOSOPHY.md) that is **auditable, iterable, reliable, and portable**, but it's not opinionated about the type of process itself.

**Q: Is Pantheon Framework a task management system?**

A: No, Pantheon Framework doesn't position itself as a task management system, and `Pantheon Dev` team comes with only a basic level of task management (tickets and backlog/todo/done folders). You can integrate the artifacts of Pantheon Framework with any task management system of your choice.

**Q: Can I use Pantheon Framework for something non-technical?**

A: Yes, Pantheon Framework is not just for software development. You can create any team that creates a tangible artifact - to help you write and manage blog posts, create travel and party plans, write recipes, analyze receipts, index your files, just about anything you wish! The only limitation is the type of tools available to the agent. For example, if the agent does not have the ability to search online or find real time limitation, it won't be able to perform the task.

**Q: Is it better than other AI development workflows like BMAD or spec-kit?**

A: Pantheon Framework does not consider itself as 'better' than other AI development workflows. Rather, it's different. Other development workflows like BMAD and spec-kit can be powerful, and can be a perfect fit for variety of projects. While Pantheon Framework also ships with the default `Pantheon Dev` team with the `plan-and-review` profile, the key difference is that Pantheon Framework is less opinionated about the process itself. Pantheon gives full control to the user with varying levels of customization - from changing the team-profile, modifying the individual config fields, directly updating the routine/schema/template itself, to creating your own custom team from scratch. It also allows for an iterative evolution of your custom workflow that is portable and shareable.

**Q: How is Pantheon Framework different from more sophisticated frameworks like SuperClaude and Claude Flow ?**

A: Pantheon's goal is different - it doesn't try to own the entire aspects of the software development lifecycle. Instead, its goal is to stay simple and focused to create the [Glass Box Process](PHILOSOPHY.md) to support a powerful human-in-the-loop workflow. It does not try to fully automate all aspects of the development lifecycle as our core philosophy is that AI agent work should be **auditable**.

**Q: How is Pantheon Framework different from the recently announced [Claude Skills](https://www.anthropic.com/news/skills)?**

A: The announcement of Claude Skills was a very exciting one, addressing a critical gap in the current AI workflow. As Claude Skills is very new (announced after Pantheon Framework's development), direct comparison is limited. There are some aspects of Claude Skills that Pantheon Framework aligns well with - on being able to create a custom workflow with ease to create a reliable workflow. However, it's different in 2 key aspects - on being **auditable** and **portable** to create the [Glass Box Process](PHILOSOPHY.md). While Claude Skills can be made auditable, it is not the primary goal. In addition, Claude Skills is (currently) portable only within the Claude ecosystem, whereas Pantheon Framework's team are portable and shareable across all providers.

**Q: How is Pantheon Framework different from the recently announced [Agent Builder from OpenAI](https://platform.openai.com/docs/guides/agent-builder)?**

A: While Agent Builder has a great UI, it's still programmatic and logical in nature - you have to create nodes and conditionals and connect to the right tools. And due to this abstraction, it is less **auditable** in addition to not being **portable** to other providers. It also targets more complex automatic workflow, whereas Pantheon Framework targets simple and human-in-the-loop workflow.

**Q: What LLM providers does Pantheon support?**

A: Pantheon Framework is provider-agnostic. It works with any LLM that can follow instructions and access files. Tested providers include Claude Code (Anthropic), Codex (OpenAI), Gemini (Google), and Qwen3 Coder 480B A35B model through OpenCode. The teams are portable across all providers.

**Q: How do I use the agents of Pantheon Framework?**

A: Pantheon Framework works best with platforms that have built-in support for subagents, like Claude Code or OpenCode, as you can directly address the agents (i.e. @frontend-engineer). However, this is a mere convinience, not a blocker. With platforms that don't have built-in support for subagents, you can simply instruct the LLM to adopt a persona from the agent definition, and use dedicated terminal for each agent to prevent context bleeding (or clear the session context). An example interaction with other platforms would look like below
```
You are now @agents/tech-lead.md . As a tech-lead, create a ticket based on what we just discussed.
```

Depending on the subagent implementation, subagent doesn't always mean it's better. For example, with Claude Code's subagent, you cannot interact with it or intercept it, as it'll create a fresh new agent after that. This is different from OpenCode's implementation of subagent, which is similar to creating a dedicated terminal for each agent that you can interact with. 

**Q: Any tips and tricks?**

A: You can take advantage of Pantheon Framework's **portable** aspect to leverage subagents and multiple providers. On Claude, ask it to spawn multiple @frontend-engineer to create plans for multiple tickets at the same time. Open another terminal and have Codex implement the plan. Have Gemini do the code review. And try out OpenCode with NVIDIA's Qwen3 Coder 480B A35B model mid-project. In addition, you can copy-paste the agent files to create 'junior' versions of the agents for simple task to make model switching easier (i.e. @junior-frontend-engineer create a unit test based on the plan).

Pro tip: Copy agent files and configure them with lighter models (i.e Haiku, gpt-5-codex-low, gemini-2.5-flash) to create 'junior' versions for simple tasks. For example: `@junior-frontend-engineer write unit tests outlined in the plan`, making model switching much easier.

**Q: Any parting words?**

A: When you are using `Pantheon Dev` and you see the agent saying `You're absolutely right!`, that probably means something is **absolutely wrong.** Ask the agent to capture what just happened, have @retro create a retro report, and make concrete improvements based on the suggestion. **Stop fighting with AI, take control back!**


## License

[Apache 2.0](LICENSE)
