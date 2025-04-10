from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder(name="sentence-transformers/all-MiniLM-L6-v2")

faq = Route(
    name='faq',
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        "Are there any ongoing sales or promotions?",
        "Can I cancel or modify my order after placing it?", 
        "Do you offer international shipping?", 
        "What should I do if I receive a damaged product?", 
        "How do I use a promo code during checkout?"
    ],
    score_threshold = 0.2
)

sql = Route(
    name='sql',
    utterances=[
        "I want to buy nike shoes that have 50 percent discount.",
        "Are there any shoes under Rs. 3000?",
        "Do you have formal shoes in size 9?",
        "Are there any Puma shoes on sale?",
        "What is the price of puma running shoes?",
    ],
    score_threshold = 0.2
)

small_talk = Route(
    name='small_talk',
    utterances=[
        "How are you?",
        "What is your name?",
        "Are you a robot?",
        "What are you?",
        "What do you do?",
        "Tell me a joke",
        "What's the weather like?",
        "What time is it?",
        "Where are you from?",
        "Can you speak any other languages?",
        "Do you like music?",
        "What's your favorite movie?",
        "Do you have any hobbies?",
        "Are you alive?",
        "What's your favorite color?",
        "What can you do?",
        "How do you work?",
        "What is your purpose?",
        "Do you understand emotions?",
        "What's your opinion on artificial intelligence?"
    ],
    score_threshold = 0.2
)

router = SemanticRouter(routes = [faq,sql,small_talk], encoder = encoder, auto_sync="local")

if __name__ == "__main__":
    print("======================================================")
    print(router("Is there any discounts going on now?").name)
    print(router("Pink Puma shoes in price range 5000 to 1000?").name)
    print(router("Nike shoes with rating more than 4.5?").name)
    print(router("What is your policy on defective product?").name)
    print(router("When is the refund processed?").name)
    print(router("How to cancel my order?").name)
    print(router("Is there international shipping?").name)
    print(router("Is there a discount going on for debit cards?").name)
    print(router("how are you?").name)
    print(router("Are you a robot?").name)
    print(router("what is your age?").name)
    print("======================================================")