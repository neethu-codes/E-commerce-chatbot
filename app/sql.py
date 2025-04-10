import sqlite3
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import os
import re


load_dotenv()


db_path = "db.sqlite"
groq_client_sql = Groq()

sql_prompt = """You are an expert in understanding the database schema and generating SQL queries for a natural language question asked
pertaining to the data you have. The schema is provided in the schema tags. 
<schema> 
table: product 

fields: 
product_link - string (hyperlink to product)	
title - string (name of the product)	
brand - string (brand of the product)	
price - integer (price of the product in Indian Rupees)	
discount - float (discount on the product. 10 percent discount is represented as 0.1, 20 percent as 0.2, and such.)	
avg_rating - float (average rating of the product. Range 0-5, 5 is the highest.)	
total_ratings - integer (total number of ratings for the product)

</schema>
Make sure whenever you try to search for the brand name, the name can be in any case. 
So, make sure to use %LIKE% to find the brand in condition. Never use "ILIKE". 
Create a single SQL query for the question provided. 
The query should have all the fields in SELECT clause (i.e. SELECT *)

Just the SQL query is needed, nothing more. Always provide the SQL in between the <SQL></SQL> tags."""


def generate_sql_query(question):
    """
    Uses Groq to generate an SQL query for the given natural language question.

    Args:
        question (str): The natural language question about the product data.

    Returns:
        str: Raw model output containing SQL between <SQL></SQL> tags.
    """

    chat_completion = groq_client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content" : sql_prompt
            },
            {
                "role": "user",
                "content" : question
            }
        ],
        model = os.environ['GROQ_MODEL'],
        temperature=0.2,
        max_tokens=1024
    )
    sql_query = chat_completion.choices[0].message.content
    print(f"Question - {question} -> SQL Query - {sql_query}")
    return sql_query



def run_query(query):
    """
    Executes a SQL SELECT query against the SQLite3 database and returns the result as a DataFrame.

    Args:
        query (str): A valid SQL SELECT query.

    Returns:
        pd.DataFrame or str: Query result as a DataFrame, or error message if invalid.
    """
    if query.strip().upper().startswith('SELECT'):
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query,conn)
            return df
    else:
        return f"Invalid SQL query generated - {query}"
    

    
def sql_chain(question):
    """
    End-to-end flow: Converts a user question to SQL, executes the query, and returns a human-friendly answer.

    Args:
        question (str): Natural language query.

    Returns:
        str: AI-generated response based on queried data.
    """
    sql_query = generate_sql_query(question)
    pattern = "<SQL>(.*?)</SQL>"
    matches = re.findall(pattern,sql_query, re.DOTALL)

    if len(matches) == 0:
        return "Sorry, LLM is not able to generate a query for your question"
    
    response = run_query(matches[0].strip())

    if response is None:
        return "Sorry, there was a problem executing SQL query"
    
    context = response.to_dict(orient='records')
    answer = data_comprehension(question,context)

    return answer


def data_comprehension(question,df):

    """
    Uses Groq to convert a DataFrame or dict into a human-readable natural language answer.

    Args:
        question (str): The original user question.
        df : Data extracted from SQL query result.

    Returns:
        str: A natural language response describing the data.
    """



    comprehension_prompt = """You are an expert in understanding the context of the question and replying based on the data pertaining to the question provided. You will be provided with QUESTION: and DATA:. The data will be in the form of an array or a dataframe or dict. Reply based on only the data provided as Data for answering the question asked as Question. Do not write anything like 'Based on the data' or any other technical words. Just a plain simple natural language response.
    The Data would always be in context to the question asked. For example is the question is “What is the average rating?” and data is “4.3”, then answer should be “The average rating for the product is 4.3”. So make sure the response is curated with the question and data. Make sure to note the column names to have some context, if needed, for your response.
    There can also be cases where you are given an entire dataframe in the Data: field. Always remember that the data field contains the answer of the question asked. All you need to do is to always reply in the following format when asked about a product: 
    Product title, price in indian rupees, discount, and rating, and then product link. Take care that all the products are listed in list format, one line after the other. Not as a paragraph.
    For example:
    1. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
    2. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
    3. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
    """
        
    chat_completion = groq_client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content" : comprehension_prompt
            },
            {
                "role": "user",
                "content" : f"QUESTION:{question} DATA: {df}"
            }
        ],
        model = os.environ['GROQ_MODEL'],
        temperature=0.2,
        max_tokens=1024
    )

    return chat_completion.choices[0].message.content

if __name__ == "__main__":

    question = "Give me PUMA shoes with rating higher than 4.5 and more than 30% discount"
    answer = sql_chain(question)
    print(f"Question -> {question}\n Answer -> {answer}")

    question = "Give me All NIKE shoes in price range 5000 to 10000"
    answer = sql_chain(question)
    print(f"Question -> {question}\n Answer -> {answer}")

    question = "Give me All Nike shoes with rating higher than 4.8"
    answer = sql_chain(question)
    print(f"Question -> {question}\n Answer -> {answer}")

    