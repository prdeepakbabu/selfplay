import os
import logging
import json
<<<<<<< HEAD
from openai import AzureOpenAI
import markdown2

class Chatbot:
    def __init__(self, name, sys_msg):
        self.name = name
        self.sys_msg = sys_msg
        self.memory = []
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")        
        self.client = AzureOpenAI(api_version=api_version, azure_endpoint=azure_endpoint, api_key=api_key)
=======
import markdown2
from .provider_interface import get_provider, AzureOpenAIProvider

class Chatbot:
    def __init__(self, name, sys_msg, provider="azure", model=None, time_delay=0, **provider_kwargs):
        """
        Initialize a chatbot with a name, system message, and LLM provider.
        
        Args:
            name: The name of the chatbot.
            sys_msg: The system message that defines the chatbot's behavior.
            provider: The LLM provider to use. Default is "azure".
                Options: "azure", "openai", "anthropic", "google", "meta", "aws"
            model: The model to use. If None, the provider's default model will be used.
            time_delay: Time to wait in seconds between API calls to avoid throttling. Default is 0.
            **provider_kwargs: Additional keyword arguments to pass to the provider.
        """
        self.name = name
        self.sys_msg = sys_msg
        self.memory = []
        
        # Set up logging
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        # Suppress INFO logs from httpx
        httpx_logger = logging.getLogger("httpx")
        httpx_logger.setLevel(logging.WARNING)
<<<<<<< HEAD

    def chat(self, user_msg, use_memory=True):
=======
        
        # Initialize the provider
        try:
            if model:
                provider_kwargs["model"] = model
            # Pass time_delay to the provider
            provider_kwargs["time_delay"] = time_delay
            self.provider = get_provider(provider, **provider_kwargs)
            self.logger.info(f"Using {self.provider.provider_name} provider with model {self.provider.model}")
            if time_delay > 0:
                self.logger.info(f"API call delay set to {time_delay} seconds to avoid throttling")
        except Exception as e:
            self.logger.error(f"Failed to initialize provider: {str(e)}")
            # Fall back to Azure OpenAI for backward compatibility
            self.logger.info("Falling back to Azure OpenAI provider")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            azure_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION")
            self.provider = AzureOpenAIProvider(
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=api_version
            )

    def chat(self, user_msg, use_memory=True, **kwargs):
        """
        Send a message to the chatbot and get a response.
        
        Args:
            user_msg: The user message to send.
            use_memory: Whether to use the conversation memory. Default is True.
            **kwargs: Additional parameters to pass to the provider's generate_response method.
                
        Returns:
            The chatbot's response.
        """
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)
        try:
            self._add_to_memory("user", user_msg)
            messages = self._construct_messages(user_msg, use_memory)

<<<<<<< HEAD
            response = self.client.chat.completions.create(
                model="gpt-4",  # model = "deployment_name"
                messages=messages
            )

            response_msg = response.choices[0].message.content
=======
            response_msg = self.provider.generate_response(messages, **kwargs)
            
            # Ensure we're only storing the text content in memory
            # If the response is a JSON string, try to extract just the text content
            if isinstance(response_msg, str) and (response_msg.startswith('{') or response_msg.startswith('{')):
                try:
                    import json
                    response_json = json.loads(response_msg)
                    if isinstance(response_json, dict) and 'content' in response_json:
                        if isinstance(response_json['content'], list) and len(response_json['content']) > 0:
                            if 'text' in response_json['content'][0]:
                                response_msg = response_json['content'][0]['text']
                except:
                    # If we can't parse the JSON, just use the original response
                    pass
            
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)
            self._add_to_memory("assistant", response_msg)
            return response_msg

        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")
            return f"An error occurred: {str(e)}"
    
    def _add_to_memory(self, role, content):
        self.memory.append({"role": role, "content": content})

    def _construct_messages(self, user_msg, use_memory):
        messages = [{"role": "system", "content": self.sys_msg}]
        if use_memory:
            messages.extend(self.memory)
        else:
            messages.append({"role": "user", "content": user_msg})
        return messages

    def __repr__(self):
        if not self.memory:
            return "NOTHING TO REMEMBER"
<<<<<<< HEAD
        return "\n".join([f"{self.name if m['role'] == 'assistant' else 'USER'}: {m['content']}" for m in self.memory])
=======
        
        # Define ANSI color codes for better visualization
        USER_COLOR = "\033[94m"  # Blue
        ASSISTANT_COLOR = "\033[92m"  # Green
        RESET_COLOR = "\033[0m"  # Reset to default
        
        return "\n".join([
            f"{ASSISTANT_COLOR}{self.name}{RESET_COLOR}: {m['content']}" 
            if m['role'] == 'assistant' 
            else f"{USER_COLOR}USER{RESET_COLOR}: {m['content']}" 
            for m in self.memory
        ])
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)
    
    def show_memory(self):
        if not self.memory:
            return "MEMORY EMPTY ERROR"
<<<<<<< HEAD
        for msg in self.memory:
            role = self.name if msg["role"] == "assistant" else "USER"
            print(f"{role}: {msg['content']}")
=======
        
        # Define ANSI color codes for better visualization
        USER_COLOR = "\033[94m"  # Blue
        ASSISTANT_COLOR = "\033[92m"  # Green
        RESET_COLOR = "\033[0m"  # Reset to default
        
        for msg in self.memory:
            if msg["role"] == "assistant":
                print(f"{ASSISTANT_COLOR}{self.name}{RESET_COLOR}: {msg['content']}")
            else:
                print(f"{USER_COLOR}USER{RESET_COLOR}: {msg['content']}")
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)

    def reset_memory(self):
        self.memory = []
        self.logger.info("Memory has been reset.")
        return "Memory has been reset."

    def save_memory(self, file_path):
        try:
            with open(file_path, 'w') as file:
                json.dump(self.memory, file)
            self.logger.info(f"Memory saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save memory: {str(e)}")

    def load_memory(self, file_path):
        try:
            with open(file_path, 'r') as file:
                self.memory = json.load(file)
            self.logger.info(f"Memory loaded from {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to load memory: {str(e)}")
    
    def get_num_turns(self):
        return len(self.memory) // 2
<<<<<<< HEAD
    
    def _save_conversation_to_markdown(self, conversation_history, filename):
        with open(filename, 'w') as file:
            file.write("# Conversation History\n\n")
            file.write(f'<div style="margin-bottom: 10px;">')
            file.write(f'<span style="color: blue; font-weight: bold;">{conversation_history[1][0]}</span>: ')
            file.write(f'<span style="background-color: #f1f1f1; padding: 10px; border-radius: 5px; display: inline-block; max-width: 80%; font-size: 14px; ">{conversation_history[0][1]}</span>')
            file.write('</div>\n\n')
            i=0
            for turn in conversation_history:
                bot_name, user_msg, response = turn
                if i%2 == 0:
                    file.write(f'<div style="margin-bottom: 10px;">')
                    file.write(f'<span style="color: green; font-weight: bold;">{bot_name}</span>: ')
                    file.write(f'<span style="background-color: #e0ffe0;  padding: 10px; border-radius: 5px; display: inline-block; max-width: 80%; font-size: 14px; ">{response}</span>')
                    file.write('</div>\n\n')
                else:
                    file.write(f'<div style="margin-bottom: 10px;">')
                    file.write(f'<span style="color: blue; font-weight: bold;">{bot_name}</span>: ')
                    file.write(f'<span style="background-color: #f1f1f1;  padding: 10px; border-radius: 5px; display: inline-block; max-width: 80%; font-size: 14px; ">{response}</span>')
                    file.write('</div>\n\n')  
                i   = i + 1                 
    
    def interact(self, other_bot, num_turns=10, start="Hello! How can I assist you today?",filename=None):
        conversation_history = []
=======
        
    def conversation_to_json(self, conversation_history, other_bot=None):
        """
        Convert conversation history to a structured JSON object.
        
        Args:
            conversation_history: List of conversation turns as tuples (bot_name, message, response)
            other_bot: The other bot in the conversation (optional)
            
        Returns:
            dict: A structured JSON-serializable dictionary of the conversation
        """
        import datetime
        
        # Create metadata section
        metadata = {
            "timestamp": datetime.datetime.now().isoformat(),
            "participants": [
                {
                    "name": self.name,
                    "system_message": self.sys_msg,
                    "provider": self.provider.provider_name,
                    "model": self.provider.model
                }
            ],
            "turns": len(conversation_history),
            "initial_prompt": conversation_history[0][1] if conversation_history else ""
        }
        
        # Add second participant if available
        if other_bot:
            metadata["participants"].append({
                "name": other_bot.name,
                "system_message": other_bot.sys_msg,
                "provider": other_bot.provider.provider_name,
                "model": other_bot.provider.model
            })
        
        # Create conversation turns
        conversation = []
        for i, (bot_name, message, response) in enumerate(conversation_history):
            conversation.append({
                "turn": i + 1,
                "speaker": bot_name,
                "message": response,
                "previous_message": message
            })
        
        # Combine into final structure
        data = {
            "metadata": metadata,
            "conversation": conversation
        }
        
        return data
    
    def print_conversation_json(self, conversation_history, other_bot=None, indent=2):
        """
        Print the conversation history as formatted JSON to stdout.
        
        Args:
            conversation_history: List of conversation turns
            other_bot: The other bot in the conversation (optional)
            indent: Number of spaces for JSON indentation (default: 2)
            
        Returns:
            str: The JSON string representation of the conversation
        """
        import json
        
        data = self.conversation_to_json(conversation_history, other_bot)
        json_str = json.dumps(data, indent=indent)
        print(json_str)
        return json_str
    
    def _save_conversation_to_markdown(self, conversation_history, filename):
        with open(filename, 'w') as file:
            file.write("<!DOCTYPE html>\n<html>\n<head>\n")
            file.write("<title>Conversation History</title>\n")
            
            # Write CSS for better styling
            file.write("""<style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 1px solid #ddd;
                padding-bottom: 10px;
            }
            .chat-container {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            .message {
                margin-bottom: 15px;
                display: flex;
                flex-direction: column;
            }
            .user-message .message-content {
                background-color: #e3f2fd;
                border-radius: 10px;
                padding: 15px;
                margin-left: auto;
                max-width: 80%;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .assistant-message .message-content {
                background-color: #e8f5e9;
                border-radius: 10px;
                padding: 15px;
                margin-right: auto;
                max-width: 80%;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .user-name {
                color: #2962FF;
                font-weight: bold;
                margin-bottom: 4px;
                text-align: right;
            }
            .assistant-name {
                color: #00897B;
                font-weight: bold;
                margin-bottom: 4px;
            }
            /* Markdown styling */
            .message-content h1 { font-size: 1.8em; margin-top: 0.5em; margin-bottom: 0.5em; }
            .message-content h2 { font-size: 1.5em; margin-top: 0.5em; margin-bottom: 0.5em; }
            .message-content h3 { font-size: 1.3em; margin-top: 0.5em; margin-bottom: 0.5em; }
            .message-content h4 { font-size: 1.2em; margin-top: 0.5em; margin-bottom: 0.5em; }
            .message-content h5 { font-size: 1.1em; margin-top: 0.5em; margin-bottom: 0.5em; }
            .message-content h6 { font-size: 1em; margin-top: 0.5em; margin-bottom: 0.5em; }
            .message-content ul, .message-content ol { padding-left: 20px; }
            .message-content li { margin-bottom: 5px; }
            .message-content pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .message-content code { background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
            .message-content blockquote { border-left: 4px solid #ddd; padding-left: 10px; margin-left: 0; color: #666; }
            .message-content table { border-collapse: collapse; width: 100%; }
            .message-content th, .message-content td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .message-content th { background-color: #f2f2f2; }
            .message-content a { color: #0066cc; text-decoration: none; }
            .message-content a:hover { text-decoration: underline; }
            .message-content img { max-width: 100%; height: auto; }
            </style>\n""")
            
            file.write("</head>\n<body>\n")
            file.write("<h1>Conversation History</h1>\n")
            file.write('<div class="chat-container">\n')
            
            # Process each turn in the conversation
            for i, turn in enumerate(conversation_history):
                bot_name, message, response = turn
                
                # Convert markdown to HTML
                html_response = markdown2.markdown(response, extras=["tables", "code-friendly", "fenced-code-blocks"])
                
                # Determine if this is a user or assistant message based on the conversation flow
                if i % 2 == 0:  # First bot (assistant) messages
                    file.write(f'<div class="message assistant-message">\n')
                    file.write(f'  <div class="assistant-name">{bot_name}</div>\n')
                    file.write(f'  <div class="message-content">{html_response}</div>\n')
                    file.write('</div>\n\n')
                else:  # Second bot (user) messages
                    file.write(f'<div class="message user-message">\n')
                    file.write(f'  <div class="user-name">{bot_name}</div>\n')
                    file.write(f'  <div class="message-content">{html_response}</div>\n')
                    file.write('</div>\n\n')
            
            file.write('</div>\n')
            file.write('</body>\n</html>')
    
    def interact(self, other_bot, num_turns=10, start="Hello! How can I assist you today?", 
                 filename=None, output_json=False, json_filename=None,
                 auto_end=False, max_turns=None):
        """
        Interact with another chatbot for a specified number of turns or until the conversation naturally ends.
        
        Args:
            other_bot: The other chatbot to interact with.
            num_turns: Number of turns for the conversation. Default is 10.
            start: Initial message to start the conversation. Default is "Hello! How can I assist you today?".
            filename: Path to save the conversation as HTML. Default is None.
            output_json: Whether to print the conversation as JSON to stdout. Default is False.
            json_filename: Path to save the conversation as JSON. Default is None.
            auto_end: Whether to automatically detect the end of the conversation. Default is False.
            max_turns: Maximum number of turns if auto_end is True. If None, uses num_turns value.
            
        Returns:
            List of conversation turns as tuples (bot_name, message, response).
        """
        conversation_history = []
        
        # Initialize conversation analyzer if auto_end is enabled
        analyzer = None
        if auto_end:
            from .conversation_analyzer import ConversationAnalyzer
            analyzer = ConversationAnalyzer()
            # If max_turns is not specified, use num_turns as the default
            actual_max_turns = max_turns if max_turns is not None else num_turns
        else:
            actual_max_turns = num_turns
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)

        # Ensure the first bot starts the conversation
        first_bot = self
        second_bot = other_bot

        # Initial message to start the conversation
        user_msg = start

<<<<<<< HEAD
        # First bot initiates the conversation
        response = first_bot.chat(user_msg)
        conversation_history.append((first_bot.name, user_msg, response))
        print(f"{second_bot.name}: {user_msg}")
        print(f"{first_bot.name}: {response}\n")

        # Continue the conversation for the remaining turns
        for _ in range(num_turns - 1):
=======
        # Define ANSI color codes for better terminal visualization
        USER_COLOR = "\033[94m"  # Blue
        ASSISTANT_COLOR = "\033[92m"  # Green
        RESET_COLOR = "\033[0m"  # Reset to default

        # First bot initiates the conversation
        response = first_bot.chat(user_msg)
        conversation_history.append((first_bot.name, user_msg, response))
        print(f"{USER_COLOR}{second_bot.name}{RESET_COLOR}: {user_msg}")
        print(f"{ASSISTANT_COLOR}{first_bot.name}{RESET_COLOR}: {response}\n")

        # Continue the conversation for the remaining turns or until auto-detection signals end
        for turn in range(1, actual_max_turns):
            # Check if we should end the conversation based on content analysis
            if auto_end and turn > 1:
                should_end, score, reason = analyzer.detect_end_signals(conversation_history, turn)
                if should_end:
                    print(f"Conversation ended automatically after {turn} turns. Reason: {reason} (confidence: {score:.2f})")
                    break
                    
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)
            user_msg = response

            # Second bot responds
            response = second_bot.chat(user_msg)
            conversation_history.append((second_bot.name, user_msg, response))
<<<<<<< HEAD
            print(f"{second_bot.name}: {response}\n")
=======
            print(f"{USER_COLOR}{second_bot.name}{RESET_COLOR}: {response}\n")

            # Check again after second bot's response
            if auto_end:
                should_end, score, reason = analyzer.detect_end_signals(conversation_history, turn)
                if should_end:
                    print(f"Conversation ended automatically after {turn} turns. Reason: {reason} (confidence: {score:.2f})")
                    break
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)

            user_msg = response

            # First bot responds
            response = first_bot.chat(user_msg)
            conversation_history.append((first_bot.name, user_msg, response))
<<<<<<< HEAD
            print(f"{first_bot.name}: {response}\n")
=======
            print(f"{ASSISTANT_COLOR}{first_bot.name}{RESET_COLOR}: {response}\n")
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)
        
        # Save conversation to a markdown file if filename is provided
        if filename:
            self._save_conversation_to_markdown(conversation_history, filename)
            print(f"Conversation saved to {filename}")
<<<<<<< HEAD

        return conversation_history
=======
        
        # Output JSON if requested
        if output_json:
            self.print_conversation_json(conversation_history, other_bot)
        
        # Save conversation to a JSON file if json_filename is provided
        if json_filename:
            import json
            with open(json_filename, 'w') as file:
                json.dump(self.conversation_to_json(conversation_history, other_bot), file, indent=2)
            print(f"Conversation saved to JSON: {json_filename}")

        return conversation_history
>>>>>>> 85e1a4d (enhanced with an app and also add features like timeout)
