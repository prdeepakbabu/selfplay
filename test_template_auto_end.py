#!/usr/bin/env python3
"""
Test script for the auto-end feature in template-based conversations.
"""

from selfplay.RolePlay import RolePlay

def main():
    # Create a role play simulation using the "Doctor | Patient" template
    template_name = "Doctor | Patient"
    description = "A patient consults with a doctor about persistent headaches and dizziness."
    num_turns = 10
    
    print(f"\n{'='*80}\nTEMPLATE-BASED CHAT WITH AUTO-END FEATURE\n{'='*80}\n")
    print(f"Template: {template_name}")
    print(f"Description: {description}")
    print(f"Maximum Turns: {num_turns}")
    print(f"\n{'-'*80}\nCONVERSATION\n{'-'*80}\n")
    
    # Create a role play simulation
    role_play = RolePlay(
        template_name=template_name,
        description=description,
        num_turns=num_turns,
        provider="aws",
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    )
    
    # Run the simulation with auto_end enabled
    conversation_history = role_play.simulate_interaction(
        auto_end=True,
        max_turns=num_turns * 2  # Set a higher max_turns to allow for longer conversations if needed
    )
    
    print(f"{'='*80}\nTEMPLATE-BASED CHAT COMPLETED\n{'='*80}")
    print(f"Total turns: {len(conversation_history) // 2}")

if __name__ == "__main__":
    main()
