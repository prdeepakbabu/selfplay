# Import the templates from templates.py
from .templates import templates
from .chatbot import Chatbot

# Define the RolePlay class
class RolePlay:
    def __init__(self, template_name, description, num_turns=3):
        # Initialize based on the imported template
        template = templates[template_name]  # Access templates from the separate file
        self.role1 = Chatbot(template["roles"][0], template["sys_msgs"][template["roles"][0]])
        self.role2 = Chatbot(template["roles"][1], template["sys_msgs"][template["roles"][1]])
        self.start_message = description
        self.num_turns = num_turns

        # Automatically run the simulation during initialization
        self.simulate_interaction()

    def simulate_interaction(self):
        # Use the interact function from ChatBot class
        response = self.role1.interact(self.role2, start=self.start_message, num_turns=self.num_turns)
        print(response)
