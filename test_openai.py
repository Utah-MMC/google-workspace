from openai import OpenAI
import os

def main():
    # Check that the env var is visible inside Python
    print("Has OPENAI_API_KEY?", "OPENAI_API_KEY" in os.environ)

    # Create client (reads key from env by default if not passed)
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    print("Calling OpenAI...")
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input="Say a one-sentence hello to Dave."
    )

    text = resp.output[0].content[0].text
    print("OpenAI replied:")
    print(text)

if __name__ == "__main__":
    main()
