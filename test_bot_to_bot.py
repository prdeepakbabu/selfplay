#!/usr/bin/env python3
"""
Test script for Bot-to-Bot Chat mode using AWS Bedrock.
"""

from selfplay.chatbot import Chatbot

def main():
    # Create two chatbots using AWS Bedrock
    bot1 = Chatbot(
        name="Science Expert",
        sys_msg="You are a science expert who specializes in explaining complex scientific concepts in simple terms. You're enthusiastic about science and technology.",
        provider="aws",
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    )

    bot2 = Chatbot(
        name="Curious Student",
        sys_msg="You are a curious student who asks thoughtful questions about science and technology. You're eager to learn and understand complex concepts.",
        provider="aws",
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    )
    
    # Initial message to start the conversation
    initial_message = "Can you explain quantum computing in simple terms?"
    initial_message = "I'm a 3rd grader, can you explain mixed fractions"
    
    # Number of turns for the conversation
    num_turns = 3
    
    print(f"\n{'='*80}\nBOT-TO-BOT CHAT MODE TEST\n{'='*80}\n")
    print(f"Bot 1: {bot1.name} - {bot1.sys_msg}")
    print(f"Bot 2: {bot2.name} - {bot2.sys_msg}")
    print(f"Initial Message: {initial_message}")
    print(f"Number of Turns: {num_turns}")
    print(f"\n{'-'*80}\nCONVERSATION\n{'-'*80}\n")
    
    # Run the interaction
    conversation_history = bot1.interact(
        bot2,
        start=initial_message,
        #num_turns=num_turns,
        auto_end=True,
        max_turns=4,
        filename="/Users/badeepak/Downloads/ts.html"
    )
    
    print(f"{'='*80}\nBOT-TO-BOT CHAT COMPLETED\n{'='*80}")

if __name__ == "__main__":
    main()
