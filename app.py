import os
from selfplay.chatbot import Chatbot


def main():
    """
    Main function to run the chatbot interaction example.
    """
    # Set OpenAI credentials
    os.environ["AZURE_OPENAI_API_KEY"] = "8jsd899fs000sdf7632"
    os.environ["AZURE_OPENAI_API_ENDPOINT"] = "https://server.openai.azure.com"
    os.environ["AZURE_OPENAI_API_VERSION"] = "2023-12-01-preview"

    #self-chat multi-turn conversation
    bot = Chatbot(name="default", sys_msg="you are a helpful assistant and honest in repsones. you give short and concise response.")
    bot.chat("what is the capital of California")    
    bot.chat("how about Oregon?")
    bot.chat("How many live here?")
    print(bot)

    # Initialize chatbots with specific roles and system messages
    teacher = Chatbot(
        name="Teacher",
        sys_msg="You are a helpful teacher with extensive knowledge of science and math. "
                "You ask thoughtful questions to motivate and invoke students' curiosity and depth. "
                "Provide concise, crisp, and clear replies."
    )
    student = Chatbot(
        name="Student",
        sys_msg="You are a student trying to learn from a teacher. "
                "Ask clarifying questions until the topic is clear to you."
    )

    # Interact between the teacher and student chatbots
    response = teacher.interact(
        student,  #who to interact with
        start="I'm a 4th grader and I don't seem to quite understand what complex numbers are.",
        num_turns=2,  #max_turns in conversation
        filename="/Users/dpiskala/Downloads/teacher-student.html"  #export the chat results in a well-formatted html file.
    )
    #print(response)


if __name__ == "__main__":
    main()