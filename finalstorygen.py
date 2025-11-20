import os
from dotenv import load_dotenv

# Use the shared helpers in ai_utils which already initialize and handle clients
from ai_utils import generate_story, generate_ghibli_image

load_dotenv()

def main():
    description = input("Enter a short description for the story: ").strip()
    if not description:
        print("No description provided. Exiting.")
        return

    try:
        story_text = generate_story(description)
        print("\n--- Generated Story ---\n")
        print(story_text)
    except Exception as e:
        print("Story generation failed:", e)

    try:
        image_path = generate_ghibli_image(description)
        print(f"\nImage saved as {image_path}")
    except Exception as e:
        print("Image generation failed:", e)

if __name__ == "__main__":
    main()
