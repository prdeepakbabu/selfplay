#!/usr/bin/env python3
"""
Test script for Self-Chat mode using AWS Bedrock.
"""

from selfplay.chatbot import Chatbot

def main():
    # Create a chatbot using AWS Bedrock
    bot = Chatbot(
        name="Claude",
        sys_msg="You are Claude, a helpful AI assistant created by Anthropic.",
        provider="aws",
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    )
    
    # Initial message
    initial_message = "What are the top 5 emerging technologies in 2025?"
    
    # Number of turns for self-chat
    num_turns = 3
    
    print(f"\n{'='*80}\nSELF-CHAT MODE TEST\n{'='*80}\n")
    print(f"Bot: {bot.name}")
    print(f"System Message: {bot.sys_msg}")
    print(f"Initial Message: {initial_message}")
    print(f"Number of Turns: {num_turns}")
    print(f"\n{'-'*80}\nCONVERSATION\n{'-'*80}\n")
    
    # Initial response
    response = bot.chat(initial_message)
    print(f"USER: {initial_message}")
    print(f"{bot.name}: {response}\n")
    
    # Continue the conversation for the remaining turns
    for i in range(num_turns - 1):
        user_msg = response
        response = bot.chat(user_msg)
        print(f"USER: {user_msg}")
        print(f"{bot.name}: {response}\n")
    
    print(f"{'='*80}\nSELF-CHAT COMPLETED\n{'='*80}")

if __name__ == "__main__":
    main()
