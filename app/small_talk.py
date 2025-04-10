from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
groq_client = Groq()

def talk(query):
    """
    Generates a conversational response for small talk queries using a Groq LLM.

    Args:
        query (str): The user's small talk input, e.g., "What is your name?", "What's the weather like?"

    Returns:
        str: The AI-generated conversational response.

    Description:
    This function formats the user's input into a friendly prompt,
    sends it to the Groq language model, and returns the model's response.
    It's meant to simulate natural, engaging conversation.
    """

    prompt = f'''You are a helpful and friendly chatbot designed for small talk. You can answer questions about the weather, your name, your purpose, and more.
    
    QUESTION: {query}
    '''

    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model = os.environ['GROQ_MODEL'],
        temperature = 0.5
        
    )
    response = chat_completion.choices[0].message.content
    return response



if __name__=='__main__':
    question="What are you?"
    answer = talk(question)
    print(f"Question -- > {question} \nAnswer --> {answer}")
    question="Tell me a joke"
    answer = talk(question)
    print(f"Question -- > {question} \nAnswer --> {answer}")
