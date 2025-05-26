from app.modules.scrapper.nlp import NLPLayer

def main():
    print("Enter sentences to analyze sentiment. Type 'exit' or 'quit' to stop.")
    while True:
        text = input("Sentence: ")
        if text.strip().lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        nlp = NLPLayer(text)
        sentiment = nlp.sentiment()
        print(f"Sentiment: {sentiment}")

if __name__ == "__main__":
    main()
