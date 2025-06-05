# System Patterns: SelfPlay

## System Architecture

SelfPlay follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Chatbot      │◄────┤    RolePlay     │◄────┤    Templates    │
│    Module       │     │    Module       │     │    Module       │
│                 │     │                 │     │                 │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│                 │
│  Azure OpenAI   │
│     Client      │
│                 │
└─────────────────┘
```

1. **Chatbot Module**: Core component that handles individual bot instances, conversation memory, and API interactions.
2. **RolePlay Module**: Manages interactions between multiple bots using predefined templates.
3. **Templates Module**: Stores predefined conversation scenarios and role definitions.
4. **Azure OpenAI Client**: External dependency for generating AI responses.

## Key Technical Decisions

1. **Azure OpenAI Integration**: The system is designed to work with Azure OpenAI's API, leveraging its capabilities for generating contextually relevant responses.

2. **Memory Management**: Each bot instance maintains its own conversation memory, allowing for context-aware responses across multiple turns.

3. **Template-Based Design**: Predefined templates enable quick setup of common conversation scenarios without requiring extensive configuration.

4. **HTML Export**: Conversations can be exported as formatted HTML for easy reading and analysis.

5. **Modular Structure**: The codebase is organized into distinct modules with clear responsibilities, facilitating maintenance and extension.

## Design Patterns

1. **Factory Pattern**: The RolePlay class acts as a factory for creating and configuring Chatbot instances based on templates.

2. **Observer Pattern**: The interaction between bots follows an observer-like pattern, where each bot responds to the messages of the other.

3. **Strategy Pattern**: Different conversation strategies can be implemented by configuring the system messages and roles.

4. **Facade Pattern**: The high-level API provides a simplified interface to the complex underlying functionality.

## Component Relationships

### Chatbot Class
- **Primary Responsibilities**:
  - Maintaining conversation memory
  - Constructing messages for the API
  - Handling API interactions
  - Formatting and exporting conversations

- **Key Methods**:
  - `chat()`: Process a user message and generate a response
  - `interact()`: Facilitate conversation between two bots
  - `_add_to_memory()`: Store conversation history
  - `_construct_messages()`: Format messages for the API
  - `_save_conversation_to_markdown()`: Export conversations as HTML

### RolePlay Class
- **Primary Responsibilities**:
  - Setting up predefined conversation scenarios
  - Creating and configuring bot instances
  - Initiating and managing interactions

- **Key Methods**:
  - `simulate_interaction()`: Run the conversation simulation

### Templates Module
- **Primary Responsibilities**:
  - Defining conversation scenarios
  - Storing role definitions and system messages
  - Providing starting prompts for conversations

## Critical Implementation Paths

1. **Bot Initialization Flow**:
   ```
   Initialize Chatbot → Set system message → Configure API client → Prepare memory storage
   ```

2. **Conversation Flow**:
   ```
   Receive message → Add to memory → Construct API request → Process response → Store response → Return formatted result
   ```

3. **Interaction Flow**:
   ```
   Bot A initiates → Bot B responds → Alternate responses for N turns → Export conversation (optional)
   ```

4. **RolePlay Initialization Flow**:
   ```
   Select template → Create bot instances with roles → Set starting message → Simulate interaction
   ```

## Error Handling Strategy

1. **API Errors**: Exceptions from the OpenAI API are caught and logged, with error messages returned to the user.

2. **Memory Operations**: File operations for saving/loading memory include exception handling to prevent crashes.

3. **Logging**: The system uses Python's logging module to record important events and errors.
