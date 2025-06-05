"""
Gradio app for SelfPlay.
This module provides a user-friendly interface for the SelfPlay package.
"""

import os
import gradio as gr
import tempfile
from pathlib import Path
import time
import json
import markdown2
from .chatbot import Chatbot
from .RolePlay import RolePlay
from .templates import templates
from .provider_interface import get_provider

# Define provider options
PROVIDERS = {
    "Azure OpenAI": "azure",
    "OpenAI": "openai",
    "Anthropic": "anthropic",
    "Google (Gemini)": "google",
    "Meta (Llama)": "meta",
    "AWS Bedrock": "aws"
}

# Define model options for each provider
PROVIDER_MODELS = {
    "azure": ["gpt-4", "gpt-3.5-turbo"],
    "openai": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
    "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
    "google": ["gemini-pro", "gemini-ultra"],
    "meta": ["llama-3-70b", "llama-3-8b", "llama-2-70b"],
    "aws": [
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Claude 3.7 Sonnet model
        "amazon.titan-text-express-v1",
        "meta.llama-2-70b-chat-v1"
    ]
}

# Define credential fields for each provider
PROVIDER_CREDENTIALS = {
    "azure": ["API Key", "Endpoint", "API Version"],
    "openai": ["API Key"],
    "anthropic": ["API Key"],
    "google": ["API Key"],
    "meta": ["API Key"],
    "aws": ["Access Key ID", "Secret Access Key", "Region"]
}

# Define chat modes
CHAT_MODES = ["Self-Chat", "Bot-to-Bot Chat", "Template-Based Chat"]

def get_template_names():
    """Get a list of available template names."""
    return list(templates.keys())

def create_temp_html(conversation_history):
    """Create a temporary HTML file for displaying the conversation."""
    temp_dir = tempfile.gettempdir()
    temp_file = Path(temp_dir) / f"selfplay_conversation_{int(time.time())}.html"
    
    with open(temp_file, 'w') as file:
        file.write("<html><head>")
        file.write("<style>")
        file.write("""
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
            background-color: #f9f9f9;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .message {
            display: flex;
            flex-direction: column;
            max-width: 80%;
            padding: 0;
        }
        .user-message {
            align-self: flex-end;
        }
        .assistant-message {
            align-self: flex-start;
        }
        .message-bubble {
            padding: 12px 16px;
            border-radius: 18px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            word-wrap: break-word;
        }
        .user-message .message-bubble {
            background-color: #e3f2fd;
            border-bottom-right-radius: 4px;
        }
        .assistant-message .message-bubble {
            background-color: #e8f5e9;
            border-bottom-left-radius: 4px;
        }
        .name {
            font-weight: 500;
            margin-bottom: 4px;
            font-size: 14px;
        }
        .user-message .name {
            color: #2962FF;
            align-self: flex-end;
            margin-right: 8px;
        }
        .assistant-message .name {
            color: #00897B;
            margin-left: 8px;
        }
        .content {
            font-size: 15px;
            line-height: 1.4;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 24px;
            font-weight: 500;
        }
        </style>
        """)
        file.write("</head><body>")
        file.write("<h1>Conversation History</h1>")
        file.write('<div class="chat-container">')
        
        # Process each turn in the conversation
        for i, (bot_name, message, response) in enumerate(conversation_history):
            # Convert markdown to HTML
            html_response = markdown2.markdown(response, extras=["tables", "code-friendly", "fenced-code-blocks"])
            
            # For even indices (0, 2, 4...), this is the first bot (assistant)
            if i % 2 == 0:
                file.write(f'<div class="message assistant-message">')
                file.write(f'<div class="name">{bot_name}</div>')
                file.write(f'<div class="message-bubble">{html_response}</div>')
                file.write('</div>')
            # For odd indices (1, 3, 5...), this is the second bot (user)
            else:
                file.write(f'<div class="message user-message">')
                file.write(f'<div class="name">{bot_name}</div>')
                file.write(f'<div class="message-bubble">{html_response}</div>')
                file.write('</div>')
        
        file.write('</div>')
        
        file.write("</body></html>")
    
    return str(temp_file)

def get_credential_values(credentials_dict, provider_code):
    """Extract credential values for the selected provider."""
    if provider_code == "azure":
        return {
            "api_key": credentials_dict.get("API Key", ""),
            "azure_endpoint": credentials_dict.get("Endpoint", ""),
            "api_version": credentials_dict.get("API Version", "")
        }
    elif provider_code in ["openai", "anthropic", "google", "meta"]:
        return {"api_key": credentials_dict.get("API Key", "")}
    elif provider_code == "aws":
        # For AWS, credentials are optional as they can be read from ~/.aws/credentials
        credentials = {}
        if credentials_dict.get("Access Key ID"):
            credentials["aws_access_key"] = credentials_dict.get("Access Key ID")
        if credentials_dict.get("Secret Access Key"):
            credentials["aws_secret_key"] = credentials_dict.get("Secret Access Key")
        if credentials_dict.get("Region"):
            credentials["region"] = credentials_dict.get("Region")
        return credentials
    return {}

def update_credential_fields(provider_display_name):
    """Update credential fields based on the selected provider."""
    provider_code = PROVIDERS.get(provider_display_name)
    if not provider_code:
        return [], gr.Textbox(visible=False), gr.Textbox(visible=False), gr.Textbox(visible=False)
    
    credential_fields = PROVIDER_CREDENTIALS.get(provider_code, [])
    models = PROVIDER_MODELS.get(provider_code, [])
    
    # Create textboxes for credentials
    textboxes = [gr.Textbox(label=field, type="password", visible=True) for field in credential_fields]
    
    # Ensure we always have exactly 3 textboxes (visible or invisible)
    while len(textboxes) < 3:
        textboxes.append(gr.Textbox(visible=False))
    
    # Return the model dropdown and exactly 3 textboxes
    return gr.Dropdown(choices=models, label="Model"), textboxes[0], textboxes[1], textboxes[2]

def update_chat_mode_ui(chat_mode):
    """Update UI components based on the selected chat mode."""
    if chat_mode == "Self-Chat":
        return [
            gr.Textbox(visible=True, label="Bot Name"),
            gr.Textbox(visible=True, label="System Message"),
            gr.Textbox(visible=True, label="Initial Message"),
            gr.Slider(visible=True, label="Number of Turns"),
            gr.Dropdown(visible=False, label="Template"),
            gr.Textbox(visible=False, label="Bot 1 Name"),
            gr.Textbox(visible=False, label="Bot 1 System Message"),
            gr.Textbox(visible=False, label="Bot 2 Name"),
            gr.Textbox(visible=False, label="Bot 2 System Message")
        ]
    elif chat_mode == "Bot-to-Bot Chat":
        return [
            gr.Textbox(visible=False, label="Bot Name"),
            gr.Textbox(visible=False, label="System Message"),
            gr.Textbox(visible=True, label="Initial Message"),
            gr.Slider(visible=True, label="Number of Turns"),
            gr.Dropdown(visible=False, label="Template"),
            gr.Textbox(visible=True, label="Bot 1 Name"),
            gr.Textbox(visible=True, label="Bot 1 System Message"),
            gr.Textbox(visible=True, label="Bot 2 Name"),
            gr.Textbox(visible=True, label="Bot 2 System Message")
        ]
    else:  # Template-Based Chat
        return [
            gr.Textbox(visible=False, label="Bot Name"),
            gr.Textbox(visible=False, label="System Message"),
            gr.Textbox(visible=True, label="Initial Message"),
            gr.Slider(visible=True, label="Number of Turns"),
            gr.Dropdown(visible=True, label="Template", choices=get_template_names()),
            gr.Textbox(visible=False, label="Bot 1 Name"),
            gr.Textbox(visible=False, label="Bot 1 System Message"),
            gr.Textbox(visible=False, label="Bot 2 Name"),
            gr.Textbox(visible=False, label="Bot 2 System Message")
        ]

def run_chat(
    provider_display_name, model, chat_mode, 
    bot_name, system_message, initial_message, num_turns,
    template_name, bot1_name, bot1_system_message, bot2_name, bot2_system_message,
    compact_mode, auto_end, *credential_values,
    progress=gr.Progress()
):
    """Run the chat based on the selected parameters."""
    # Reset any previous state
    progress(0, desc="Starting chat...")
    # Get provider code
    provider_code = PROVIDERS.get(provider_display_name)
    if not provider_code:
        return "Error: Invalid provider selected."
    
    # Get credential fields for the selected provider
    credential_fields = PROVIDER_CREDENTIALS.get(provider_code, [])
    
    # Create credentials dictionary
    credentials_dict = {field: value for field, value in zip(credential_fields, credential_values)}
    
    # Get provider kwargs
    provider_kwargs = get_credential_values(credentials_dict, provider_code)
    if model:
        provider_kwargs["model"] = model
    
    # Get time delay from UI
    time_delay = credential_values[-1] if len(credential_values) > len(credential_fields) else 0
    provider_kwargs["time_delay"] = time_delay
    
    try:
        conversation_history = []
        
        if chat_mode == "Self-Chat":
            # Create a single bot for self-chat
            bot = Chatbot(
                name=bot_name or "Bot",
                sys_msg=system_message or "You are a helpful assistant.",
                provider=provider_code,
                **provider_kwargs
            )
            
            # Initial message
            progress(0.1, desc="Starting conversation...")
            user_msg = initial_message or "Hello! How can I assist you today?"
            response = bot.chat(user_msg)
            conversation_history.append((bot.name, user_msg, response))
            
            # Continue the conversation for the remaining turns
            total_turns = int(num_turns) - 1
            for i in range(total_turns):
                progress((i + 1) / (total_turns + 1), desc=f"Turn {i+1}/{total_turns}...")
                user_msg = response
                response = bot.chat(user_msg)
                conversation_history.append((bot.name, user_msg, response))
                
        elif chat_mode == "Bot-to-Bot Chat":
            progress(0.1, desc="Creating bots...")
            # Create two bots for bot-to-bot chat
            bot1 = Chatbot(
                name=bot1_name or "Bot 1",
                sys_msg=bot1_system_message or "You are a helpful assistant.",
                provider=provider_code,
                **provider_kwargs
            )
            
            bot2 = Chatbot(
                name=bot2_name or "Bot 2",
                sys_msg=bot2_system_message or "You are a helpful assistant.",
                provider=provider_code,
                **provider_kwargs
            )
            
            progress(0.2, desc="Starting bot interaction...")
            # Run the interaction
            conversation_history = bot1.interact(
                bot2,
                start=initial_message or "Hello! How can I assist you today?",
                num_turns=int(num_turns),
                auto_end=auto_end,
                max_turns=int(num_turns) * 2 if auto_end else None
            )
            
        else:  # Template-Based Chat
            progress(0.1, desc="Setting up template...")
            # Create a role play simulation
            role_play = RolePlay(
                template_name=template_name,
                description=initial_message or "Hello! How can I assist you today?",
                num_turns=int(num_turns),
                provider=provider_code,
                **provider_kwargs
            )
            
            progress(0.2, desc="Starting role play simulation...")
            # Get the conversation history
            conversation_history = role_play.simulate_interaction(
                auto_end=auto_end,
                max_turns=int(num_turns) * 2 if auto_end else None
            )
        
        progress(0.8, desc="Creating HTML output...")
        # Create a temporary HTML file for displaying the conversation
        html_file = create_temp_html(conversation_history)
        
        # Convert conversation to JSON for better formatting
        conversation_json = []
        for i, (bot_name, user_msg, response) in enumerate(conversation_history):
            # If compact mode is enabled, truncate long messages
            if compact_mode:
                display_response = response[:100] + "..." if len(response) > 100 else response
            else:
                display_response = response
                
            conversation_json.append({
                "role": "assistant" if i % 2 == 0 else "user",
                "name": bot_name,
                "content": display_response,
                "full_content": response,
                "truncated": compact_mode and len(response) > 100
            })
        
        progress(0.9, desc="Formatting conversation...")
        # Format the conversation with HTML/CSS for better visual appeal
        formatted_conversation = """
        <style>
        .chat-container {
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 100%;
            margin: 0 auto;
        }
        .message {
            display: flex;
            flex-direction: column;
            margin-bottom: 16px;
            max-width: 85%;
        }
        .user-message, .assistant-message {
            align-self: flex-start;
        }
        .message-name {
            font-weight: 600;
            margin-bottom: 4px;
            font-size: 14px;
        }
        .user-message .message-name {
            color: #2962FF;
        }
        .assistant-message .message-name {
            color: #00897B;
        }
        .message-content {
            padding: 12px 16px;
            border-radius: 12px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            line-height: 1.5;
        }
        .user-message .message-content {
            background-color: #e3f2fd;
            border-bottom-left-radius: 4px;
        }
        .assistant-message .message-content {
            background-color: #e8f5e9;
            border-bottom-left-radius: 4px;
        }
        .expand-button {
            margin-top: 5px;
            background-color: #f0f0f0;
            border: none;
            padding: 3px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            color: #555;
        }
        .expand-button:hover {
            background-color: #e0e0e0;
        }
        </style>
        <script>
        function expandMessage(msgId) {
            const shortContent = document.getElementById('short-' + msgId);
            const fullContent = document.getElementById('full-' + msgId);
            const expandBtn = document.getElementById('expand-' + msgId);
            
            if (shortContent.style.display !== 'none') {
                shortContent.style.display = 'none';
                fullContent.style.display = 'block';
                expandBtn.innerText = 'Show Less';
            } else {
                shortContent.style.display = 'block';
                fullContent.style.display = 'none';
                expandBtn.innerText = 'Show More';
            }
        }
        </script>
        <div class="chat-container">
        """
        
        for i, msg in enumerate(conversation_json):
            # Convert markdown to HTML for both short and full content
            html_content = markdown2.markdown(msg["content"], extras=["tables", "code-friendly", "fenced-code-blocks"])
            
            role_class = "user-message" if msg["role"] == "user" else "assistant-message"
            
            if msg.get("truncated", False):
                # For truncated messages, include both short and full versions with a toggle button
                full_html_content = markdown2.markdown(msg["full_content"], extras=["tables", "code-friendly", "fenced-code-blocks"])
                
                formatted_conversation += f"""
                <div class="message {role_class}">
                    <div class="message-name">{msg["name"]}</div>
                    <div id="short-msg-{i}" class="message-content">{html_content}</div>
                    <div id="full-msg-{i}" class="message-content" style="display: none;">{full_html_content}</div>
                    <button id="expand-msg-{i}" class="expand-button" onclick="expandMessage('msg-{i}')">Show More</button>
                </div>
                """
            else:
                # For non-truncated messages, just show the content
                formatted_conversation += f"""
                <div class="message {role_class}">
                    <div class="message-name">{msg["name"]}</div>
                    <div class="message-content">{html_content}</div>
                </div>
                """
        
        formatted_conversation += "</div>"
        
        progress(1.0, desc="Done!")
        return formatted_conversation, html_file
        
    except Exception as e:
        return f"Error: {str(e)}", None

def create_gradio_app():
    """Create the Gradio app."""
    with gr.Blocks(title="SelfPlay - Multi-Provider Chatbot Simulation") as app:
        gr.Markdown("# SelfPlay - Multi-Provider Chatbot Simulation")
        gr.Markdown("Simulate conversations between chatbots using various LLM providers.")
        
        with gr.Tab("Chat"):
            # Top section with all inputs in a horizontal layout
            with gr.Row():
                # Provider and model selection
                with gr.Column(scale=1):
                    provider_dropdown = gr.Dropdown(
                        choices=list(PROVIDERS.keys()),
                        value=list(PROVIDERS.keys())[0],
                        label="LLM Provider"
                    )
                    model_dropdown = gr.Dropdown(
                        choices=PROVIDER_MODELS["azure"],
                        label="Model"
                    )
                
                # Credential fields
                with gr.Column(scale=1):
                    credential_components = [
                        gr.Textbox(label="API Key", type="password"),
                        gr.Textbox(label="Endpoint", type="password"),
                        gr.Textbox(label="API Version", type="password")
                    ]
                
                # Chat mode selection
                with gr.Column(scale=1):
                    chat_mode = gr.Radio(
                        choices=CHAT_MODES,
                        value=CHAT_MODES[0],
                        label="Chat Mode"
                    )
            
            # Second row for chat configuration
            with gr.Row():
                # Basic configuration
                with gr.Column(scale=1):
                    bot_name = gr.Textbox(label="Bot Name", value="Assistant")
                    system_message = gr.Textbox(
                        label="System Message",
                        value="You are a helpful assistant.",
                        lines=2
                    )
                
                # Additional configuration
                with gr.Column(scale=1):
                    initial_message = gr.Textbox(
                        label="Initial Message",
                        value="Hello! How can I assist you today?"
                    )
                    num_turns = gr.Slider(
                        minimum=1,
                        maximum=20,
                        value=5,
                        step=1,
                        label="Number of Turns"
                    )
                
                # Template and bot configuration
                with gr.Column(scale=1):
                    template_dropdown = gr.Dropdown(
                        choices=get_template_names(),
                        label="Template",
                        visible=False
                    )
                    bot1_name = gr.Textbox(label="Bot 1 Name", value="Bot 1", visible=False)
                    bot1_system_message = gr.Textbox(
                        label="Bot 1 System Message",
                        value="You are a helpful assistant.",
                        lines=2,
                        visible=False
                    )
                    bot2_name = gr.Textbox(label="Bot 2 Name", value="Bot 2", visible=False)
                    bot2_system_message = gr.Textbox(
                        label="Bot 2 System Message",
                        value="You are a helpful assistant.",
                        lines=2,
                        visible=False
                    )
            
            # Third row for display options and run button
            with gr.Row():
                with gr.Column(scale=1):
                    compact_mode = gr.Checkbox(
                        label="Compact Mode",
                        value=False,
                        info="Truncate long messages to 100 characters"
                    )
                    
                    auto_end = gr.Checkbox(
                        label="Auto-detect conversation end",
                        value=False,
                        info="Automatically end the conversation when it appears to be complete"
                    )
                    
                    # Function to update the label for the num_turns slider
                    def update_turns_label(auto_end_enabled):
                        if auto_end_enabled:
                            return gr.Slider(
                                minimum=1,
                                maximum=30,
                                value=10,
                                step=1,
                                label="Maximum Turns"
                            )
                        else:
                            return gr.Slider(
                                minimum=1,
                                maximum=20,
                                value=5,
                                step=1,
                                label="Number of Turns"
                            )
                    
                    # Connect the auto_end checkbox to the update function
                    auto_end.change(
                        fn=update_turns_label,
                        inputs=[auto_end],
                        outputs=[num_turns]
                    )
                    
                    time_delay = gr.Number(
                        label="API Call Delay (seconds)",
                        value=0,
                        minimum=0,
                        step=0.5,
                        info="Time to wait between API calls to avoid throttling"
                    )
                
                with gr.Column(scale=2):
                    run_button = gr.Button("Run Chat", variant="primary")
            
            # Output section below all inputs
            with gr.Row():
                # Conversation display
                conversation_output = gr.HTML(label="Conversation")
            
            with gr.Row():
                # External HTML file link
                html_output = gr.HTML(label="Conversation HTML (External)")
            
            # Update UI based on provider selection
            provider_dropdown.change(
                fn=update_credential_fields,
                inputs=[provider_dropdown],
                outputs=[model_dropdown, *credential_components]
            )
            
            # Update UI based on chat mode selection
            chat_mode.change(
                fn=update_chat_mode_ui,
                inputs=[chat_mode],
                outputs=[
                    bot_name, system_message, initial_message, num_turns,
                    template_dropdown, bot1_name, bot1_system_message,
                    bot2_name, bot2_system_message
                ]
            )
            
            # Clear output button
            clear_button = gr.Button("Clear Output")
            
            # Clear outputs when button is clicked
            def clear_outputs():
                return "", ""
            
            clear_button.click(
                fn=clear_outputs,
                inputs=[],
                outputs=[conversation_output, html_output]
            )
            
            # Run chat when button is clicked
            run_button.click(
                fn=run_chat,
                inputs=[
                    provider_dropdown, model_dropdown, chat_mode,
                    bot_name, system_message, initial_message, num_turns,
                    template_dropdown, bot1_name, bot1_system_message,
                    bot2_name, bot2_system_message,
                    compact_mode, auto_end, *credential_components, time_delay
                ],
                outputs=[conversation_output, html_output]
            )
        
        with gr.Tab("About"):
            gr.Markdown("""
            # About SelfPlay
            
            SelfPlay is a Python package that allows you to simulate conversations between multiple chatbots.
            The package includes an orchestrator bot to determine the order of responses based on a given goal.
            
            ## Features
            
            - Simulate conversations among multiple bots
            - Support for multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Google, Meta, AWS Bedrock)
            - Multi-turn conversations with control for maximum turns
            - Ability to export conversation as a neatly formatted HTML
            - Easy-to-use API and UI
            
            ## Usage
            
            1. Select an LLM provider and enter your API credentials
            2. Choose a chat mode (Self-Chat, Bot-to-Bot Chat, or Template-Based Chat)
            3. Configure the chat parameters
            4. Click "Run Chat" to start the conversation
            
            ## Credits
            
            SelfPlay was created by Deepak Babu Piskala.
            """)
    
    return app

def main():
    """Run the Gradio app."""
    app = create_gradio_app()
    app.launch()

if __name__ == "__main__":
    main()
