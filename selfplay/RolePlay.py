# Import the templates from templates.py
from .templates import templates
from .chatbot import Chatbot

# Define the RolePlay class
class RolePlay:
    def __init__(self, template_name, description, num_turns=3, provider="azure", model=None, time_delay=0, **provider_kwargs):
        """
        Initialize a role play simulation with two chatbots based on a template.
        
        Args:
            template_name: The name of the template to use.
            description: The starting message for the conversation.
            num_turns: The number of turns for the conversation. Default is 3.
            provider: The LLM provider to use. Default is "azure".
                Options: "azure", "openai", "anthropic", "google", "meta", "aws"
            model: The model to use. If None, the provider's default model will be used.
            time_delay: Time to wait in seconds between API calls to avoid throttling. Default is 0.
            **provider_kwargs: Additional keyword arguments to pass to the provider.
        """
        # Initialize based on the imported template
        template = templates[template_name]  # Access templates from the separate file
        self.role1 = Chatbot(
            template["roles"][0], 
            template["sys_msgs"][template["roles"][0]],
            provider=provider,
            model=model,
            time_delay=time_delay,
            **provider_kwargs
        )
        self.role2 = Chatbot(
            template["roles"][1], 
            template["sys_msgs"][template["roles"][1]],
            provider=provider,
            model=model,
            time_delay=time_delay,
            **provider_kwargs
        )
        self.start_message = description
        self.num_turns = num_turns

        # Automatically run the simulation during initialization
        self.simulate_interaction()

    def simulate_interaction(self, filename=None, output_json=False, json_filename=None, auto_end=False, max_turns=None):
        """
        Run the role play simulation.
        
        Args:
            filename: Optional filename to save the conversation as HTML.
            output_json: Whether to print the conversation as JSON to stdout. Default is False.
            json_filename: Optional filename to save the conversation as JSON.
            auto_end: Whether to automatically detect the end of the conversation. Default is False.
            max_turns: Maximum number of turns if auto_end is True. If None, uses self.num_turns.
            
        Returns:
            The conversation history.
        """
        # Use the interact function from ChatBot class
        response = self.role1.interact(
            self.role2, 
            start=self.start_message, 
            num_turns=self.num_turns,
            filename=filename,
            output_json=output_json,
            json_filename=json_filename,
            auto_end=auto_end,
            max_turns=max_turns
        )
        return response
