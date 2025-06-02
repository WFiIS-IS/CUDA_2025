from app.scrapper.nlp import NLPLayer


def main() -> None:
    """Interactive sentiment analysis CLI tool.

    This function provides a simple command-line interface for testing sentiment
    analysis functionality. Users can input text interactively and receive
    real-time sentiment analysis results using the NLP layer.

    Features:
        - Interactive text input for sentiment analysis
        - Real-time processing using HuggingFace Transformers
        - Graceful exit commands ('exit' or 'quit')
        - Continuous operation until user chooses to exit

    Usage:
        Run the script and enter sentences when prompted. The tool will analyze
        the sentiment and display results immediately. Type 'exit' or 'quit' to stop.

    Note:
        - Uses DistilBERT model for sentiment classification
        - Model is loaded on first use and cached for subsequent requests
        - Supports POSITIVE, NEGATIVE, and NEUTRAL sentiment classification
        - Each input is processed independently for immediate feedback

    Example Output:
        ```
        Sentence: This is a great product!
        Sentiment: {'label': 'POSITIVE', 'score': 0.9998}
        ```
    """
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
