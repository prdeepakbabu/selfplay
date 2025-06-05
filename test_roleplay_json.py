#!/usr/bin/env python3
"""
Test script to demonstrate JSON output functionality with RolePlay.
"""

from selfplay.RolePlay import RolePlay

def main():
    print("\n=== Example 1: Template-Based Chat with JSON Output ===\n")
    
    # Create a role play simulation with JSON output
    role_play = RolePlay(
        template_name="Doctor | Patient",
        description="I've been experiencing severe headaches and dizziness for the past week.",
        num_turns=1,
        provider="aws",
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    )
    
    # Get the conversation history
    conversation_history = role_play.simulate_interaction(
        output_json=True,
        json_filename="doctor_patient_conversation.json"
    )
    
    print("\nJSON file saved to doctor_patient_conversation.json")
    
    # You can also access the conversation history programmatically
    print(f"\nNumber of turns in conversation: {len(conversation_history)}")
    print(f"First speaker: {conversation_history[0][0]}")
    print(f"Initial message: {conversation_history[0][1]}")

if __name__ == "__main__":
    main()
