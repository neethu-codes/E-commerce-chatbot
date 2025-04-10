import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
faqs_path = "resources/faq_data.csv"
chroma_client = chromadb.Client()
collection_name_faq = 'faqs'
groq_client = Groq()

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='sentence-transformers/all-MiniLM-L6-v2'
)

def ingest_faq_data(path):
    """
    Ingests FAQ data from a CSV file into ChromaDB.

    Args:
        path (str): The path to the CSV file containing 'question' and 'answer' columns.

    This function:
    - Checks if the collection already exists in ChromaDB.
    - If it doesn't, it reads the CSV, extracts the questions and answers,
      converts questions into embeddings, and stores them along with answers as metadata.
    """
    print("Ingesting FAQ data into Chromadb...")
    if collection_name_faq not in [col.name for col in chroma_client.list_collections()]:
        collection = chroma_client.get_or_create_collection(
            name=collection_name_faq,
            embedding_function=ef
        )

        df = pd.read_csv(path)
        docs = df['question'].to_list()
        metadata = [{'answer':ans} for ans in df['answer'].to_list()]
        ids = [f"id_{i}" for i in range(len(docs))]
        
        collection.add(
            documents=docs,
            metadatas=metadata,
            ids=ids
        )
        print(f"FAQ data successfully ingested into Chroma collection:{collection_name_faq}")
    else:
        print(f"Collection {collection_name_faq} already exists")


def get_relevant_qa(query):
    """
    Retrieves the most relevant FAQ entries from ChromaDB for a given query.

    Args:
        query (str): The user's input question.

    Returns:
        dict: A dictionary containing the top matching questions and metadata (answers).
    """
    collection = chroma_client.get_collection(name=collection_name_faq)
    result = collection.query(
        query_texts=[query],
        n_results=2
    )
    return result


def faq_chain(query):
    """
    Main function to get an answer to a query using the FAQ knowledge base and Groq for answer generation.

    Args:
        query (str): The user's question.

    Returns:
        str: The final answer generated based on retrieved context.
    """
    result = get_relevant_qa(query)
     
    context = ''.join([r.get('answer') for r in result['metadatas'][0]])
    
    answer = generate_answer(query,context)
    return answer

def generate_answer(query,context):
    """
    Uses Groq LLM to generate an answer from the context.

    Args:
        query (str): The user's question.
        context (str): The contextual information from ChromaDB.

    Returns:
        str: The generated answer.
    """

    prompt = f'''Given the question and context below, generate the answer based on the conetxt only. 
    If you don't find the answer inside the context then say "I don't know".
    Do not make things up.

    Question:{query}
    Context:{context}
    '''
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content" : prompt
            }
        ],
        model = os.environ['GROQ_MODEL']
    )

    return chat_completion.choices[0].message.content


if __name__ == "__main__":
    ingest_faq_data(faqs_path)

    query = 'What all payments types do you support?'
    answer = faq_chain(query)
    print(f"Question --> {query}")
    print(f"Answer --> {answer}")

    query = 'What are the return policies for the products?'
    answer = faq_chain(query)
    print(f"Question --> {query}")
    print(f"Answer --> {answer}")
