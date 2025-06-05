#!/usr/bin/env python3
"""
Test script to demonstrate JSON output functionality.
"""

from selfplay.chatbot import Chatbot

def main():
    # Create two chatbots
    bot1 = Chatbot(
        name="Math Teacher",
        sys_msg="You are a math teacher who explains complex mathematical concepts in simple terms with examples.",
        provider="aws",
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    )
    
    bot2 = Chatbot(
        name="Student",
        sys_msg="You are a curious student who asks thoughtful questions about mathematics.",
        provider="aws",
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    )
    
    print("\n=== Example 1: Print JSON to stdout ===\n")
    # Run the interaction with JSON output to stdout
    bot1.interact(
        bot2,
        start="Can you explain what complex numbers are?",
        num_turns=1,
        output_json=True
    )
    
    print("\n=== Example 2: Save JSON to file ===\n")
    # Run the interaction and save JSON to file
    conversation = bot1.interact(
        bot2,
        start="What is the Pythagorean theorem?",
        num_turns=1,
        json_filename="conversation.json"
    )
    
    print("\n=== Example 3: Get JSON programmatically ===\n")
    # Get JSON programmatically
    json_data = bot1.conversation_to_json(conversation, bot2)
    print("JSON data available as a Python dictionary:")
    print(f"- Timestamp: {json_data['metadata']['timestamp']}")
    print(f"- Number of turns: {json_data['metadata']['turns']}")
    print(f"- First speaker: {json_data['conversation'][0]['speaker']}")
    print(f"- First message: {json_data['conversation'][0]['message'][:50]}...")

if __name__ == "__main__":
    main()
