# MultiBot Simulation for Self-Play 🗣️🔄🗣️

SelfPlay is a Python package that allows you to simulate conversations between multiple chatbots. The package includes an orchestrator bot to determine the order of responses based on a given goal.Introducing SelfPlay Project – a versatile and intelligent chatbot package designed to enhance your conversational AI capabilities. With features enabling multi-turn self-chat and seamless interaction between two chatbots, this package leverages the power of LLMs to deliver insightful and dynamic conversations. Perfect for developers, educators, and businesses looking to integrate advanced chatbot functionalities, Self-play offers robust logging, error handling, and easy customization to meet your unique needs.
![Image](images/demo.png)

Here's the illustration of two chatbots engaging in self-play, designed to highlight their interaction in a modern tech environment.
## Features

- Simulate conversations among multiple bots
- Orchestrator bot to manage conversation flow
- Provides Memory for LLM conversations
- Multi-turn Conversations with control for maximum turns
- Ability to export conversation as a neatly formatted html
- Easy-to-use API

## Installation

You can install the package via pip:

```sh
pip install selfplay
```

## Usage
### Example 1: Multi-turn Self Chat

In this example, the chatbot will perform a self-chat to simulate a conversation with itself. This can be useful for improving response accuracy and testing conversational flows.
```python
import os
from selfplay.chatbot import Chatbot

# Set OpenAI credentials
os.environ["AZURE_OPENAI_API_KEY"] = "8jsd899fs000sdf7632"
os.environ["AZURE_OPENAI_API_ENDPOINT"] = "https://server.openai.azure.com"
os.environ["AZURE_OPENAI_API_VERSION"] = "2023-12-01-preview"

#self-chat multi-turn conversation
bot = Chatbot(name="default", sys_msg="you are a helpful assistant and honest in repsones. you give short and concise response.")
bot.chat("what is the capital of California")    
bot.chat("how about Oregon?")
bot.chat("How many live here?")
print(bot)
```
### Example 2: Chat with Another Bot

In this example, two chatbots, one acting as a teacher and the other as a student, interact with each other. This showcases how you can simulate educational or customer service interactions.

```python
import os
from selfplay.chatbot import Chatbot

# Set OpenAI credentials
os.environ["AZURE_OPENAI_API_KEY"] = "8jsd899fs000sdf7632"
os.environ["AZURE_OPENAI_API_ENDPOINT"] = "https://server.openai.azure.com"
os.environ["AZURE_OPENAI_API_VERSION"] = "2023-12-01-preview"

# Initialize chatbots with specific roles and system messages
teacher = Chatbot(
    name="Teacher",
    sys_msg="You are a helpful teacher with extensive knowledge of science and math. "
            "You ask thoughtful questions to motivate and invoke students' curiosity and depth. "
            "Provide concise, crisp, and clear replies."
)
student = Chatbot(
    name="Student",
    sys_msg="You are a student trying to learn from a teacher. "
            "Ask clarifying questions until the topic is clear to you."
)

#Interact between the teacher and student chatbots
response = teacher.interact(
    student,  #who to interact with
    start="I'm a 4th grader and I don't seem to quite understand what complex numbers are.",
    num_turns=2,  #max_turns in conversation
    filename="/Users/dpiskala/Downloads/teacher-student.html"  #export the chat results in a well-formatted html file.
)
print(response)
```
## Contributing

We welcome contributions to the Selfplay framework! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute, including submitting pull requests and reporting issues.

To contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit them (`git commit -am 'Add new feature'`)
4. Push the branch (`git push origin feature-branch`)
5. Submit a pull request

## Issues & Feedback

Found a bug or have a suggestion? Open an issue [here](https://github.com/prdeepakbabu/selfplay/issues) to collaborate on improvements. We actively review and address community feedback.

## Collaboration & Partnerships

We’re open to collaborating with researchers and developers interested in extending Selfplay or integrating it into larger projects. Feel free to reach out via [prdeepak.babu@gmail.com] for discussions regarding joint development or research partnerships.
