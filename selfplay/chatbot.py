import os
import logging
import json
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
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        # Suppress INFO logs from httpx
        httpx_logger = logging.getLogger("httpx")
        httpx_logger.setLevel(logging.WARNING)

    def chat(self, user_msg, use_memory=True):
        try:
            self._add_to_memory("user", user_msg)
            messages = self._construct_messages(user_msg, use_memory)

            response = self.client.chat.completions.create(
                model="gpt-4",  # model = "deployment_name"
                messages=messages
            )

            response_msg = response.choices[0].message.content
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
        return "\n".join([f"{self.name if m['role'] == 'assistant' else 'USER'}: {m['content']}" for m in self.memory])
    
    def show_memory(self):
        if not self.memory:
            return "MEMORY EMPTY ERROR"
        for msg in self.memory:
            role = self.name if msg["role"] == "assistant" else "USER"
            print(f"{role}: {msg['content']}")

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

        # Ensure the first bot starts the conversation
        first_bot = self
        second_bot = other_bot

        # Initial message to start the conversation
        user_msg = start

        # First bot initiates the conversation
        response = first_bot.chat(user_msg)
        conversation_history.append((first_bot.name, user_msg, response))
        print(f"{second_bot.name}: {user_msg}")
        print(f"{first_bot.name}: {response}\n")

        # Continue the conversation for the remaining turns
        for _ in range(num_turns - 1):
            user_msg = response

            # Second bot responds
            response = second_bot.chat(user_msg)
            conversation_history.append((second_bot.name, user_msg, response))
            print(f"{second_bot.name}: {response}\n")

            user_msg = response

            # First bot responds
            response = first_bot.chat(user_msg)
            conversation_history.append((first_bot.name, user_msg, response))
            print(f"{first_bot.name}: {response}\n")
        
        # Save conversation to a markdown file if filename is provided
        if filename:
            self._save_conversation_to_markdown(conversation_history, filename)
            print(f"Conversation saved to {filename}")

        return conversation_history