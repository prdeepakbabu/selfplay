# Technical Context: SelfPlay

## Technologies Used

### Core Technologies
1. **Python**: The primary programming language used for the entire project.
2. **Azure OpenAI API**: Used for generating AI responses in conversations.
3. **Markdown/HTML**: Used for formatting and exporting conversations.

### Python Libraries
1. **openai**: Client library for interacting with Azure OpenAI services.
2. **markdown2**: Used for converting markdown to HTML in conversation exports.
3. **json**: Used for serializing and deserializing conversation memory.
4. **logging**: Used for error handling and debugging information.
5. **os**: Used for environment variable management and file operations.

## Development Setup

### Environment Requirements
- Python 3.6 or higher
- Azure OpenAI API access (key, endpoint, and API version)

### Environment Variables
The following environment variables need to be set:
```
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_API_ENDPOINT=<your-endpoint>
AZURE_OPENAI_API_VERSION=<api-version>
```

### Installation
The package can be installed via pip:
```
pip install selfplay
```

### Development Installation
For development purposes, the package can be installed in editable mode:
```
git clone <repository-url>
cd selfplay
pip install -e .
```

## Technical Constraints

### API Limitations
1. **Rate Limits**: Azure OpenAI API has rate limits that may affect the speed of conversations, especially in multi-turn scenarios.
2. **Token Limits**: There are limits on the number of tokens that can be sent in a single API request, which may affect the length of conversation history that can be maintained.
3. **Cost Considerations**: API usage incurs costs based on the number of tokens processed.

### Memory Management
1. **In-Memory Storage**: Conversation history is stored in memory by default, which may limit the length of conversations in memory-constrained environments.
2. **Persistence**: While there are methods for saving and loading memory, there's no built-in database integration for long-term storage.

### Error Handling
1. **API Errors**: The system handles API errors but may not be able to recover from all types of failures.
2. **Network Dependency**: Requires stable internet connection for API calls.

## Dependencies

### External Dependencies
1. **Azure OpenAI Service**: Required for generating AI responses.
   - Version Compatibility: The package is designed to work with the API version specified in the environment variables.
   - Authentication: Requires API key and endpoint.

### Internal Dependencies
1. **templates.py**: Contains predefined conversation templates.
2. **chatbot.py**: Core module for bot functionality.
3. **RolePlay.py**: Module for managing interactions between bots.

## Tool Usage Patterns

### API Client Configuration
```python
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")        
client = AzureOpenAI(api_version=api_version, azure_endpoint=azure_endpoint, api_key=api_key)
```

### Conversation Memory Management
```python
# Adding to memory
self._add_to_memory("user", user_msg)
self._add_to_memory("assistant", response_msg)

# Constructing messages with memory
messages = [{"role": "system", "content": self.sys_msg}]
messages.extend(self.memory)
```

### API Request Pattern
```python
response = self.client.chat.completions.create(
    model="gpt-4",  # model = "deployment_name"
    messages=messages
)
response_msg = response.choices[0].message.content
```

### Error Handling Pattern
```python
try:
    # API call or file operation
except Exception as e:
    self.logger.error(f"An error occurred: {str(e)}")
    return f"An error occurred: {str(e)}"
```

## Deployment Considerations

### Package Distribution
- The package is distributed via PyPI, allowing for easy installation with pip.
- Version management follows semantic versioning principles.

### Integration Scenarios
1. **Web Applications**: Can be integrated into web applications as a backend service.
2. **Research Tools**: Can be used in research environments for studying conversational AI.
3. **Educational Platforms**: Can be integrated into educational software for simulating learning dialogues.
4. **Testing Frameworks**: Can be used as part of testing frameworks for conversational AI systems.

### Performance Considerations
1. **API Latency**: Response times are dependent on Azure OpenAI API latency.
2. **Memory Usage**: For long conversations, memory usage should be monitored.
3. **Concurrent Conversations**: The current implementation doesn't have specific optimizations for handling many concurrent conversations.
