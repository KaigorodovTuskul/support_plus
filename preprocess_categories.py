"""
Script to preprocess sfr_invalidam_data.csv and categorize documents using Mistral API
"""
import csv
import os
import time
from dotenv import load_dotenv
from mistralai import Mistral

# Load environment variables
load_dotenv()

# Get API key and initialize Mistral client
mistral_api_key = os.getenv('MISTRAL_API_KEY')
mistral_client = Mistral(api_key=mistral_api_key)

# Define possible categories
CATEGORIES = [
    "Пенсионное обеспечение",
    "Технические средства реабилитации",
    "Медицинская помощь",
    "Социальные выплаты",
    "Образование",
    "Жилищные льготы",
    "Транспортные льготы",
    "Налоговые льготы",
    "Трудоустройство",
    "Юридическая помощь",
    "Другое"
]

def categorize_document(header: str, text: str) -> str:
    """
    Use Mistral API to categorize a document based on header and text
    """
    prompt = f"""Определи категорию для следующего документа о льготах для инвалидов.

Заголовок: {header}
Текст: {text[:500]}...

Выбери ОДНУ наиболее подходящую категорию из списка:
{', '.join(CATEGORIES)}

Ответь ТОЛЬКО названием категории, без дополнительных объяснений."""

    try:
        # Call Mistral API (using small model for categorization to save on rate limits)
        response = mistral_client.chat.complete(
            model="mistral-small-latest",  # Cheaper and faster for simple categorization
            messages=[
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )

        category = response.choices[0].message.content.strip()

        # Validate that the category is in our list
        if category in CATEGORIES:
            return category
        else:
            # Try to find closest match
            for cat in CATEGORIES:
                if cat.lower() in category.lower() or category.lower() in cat.lower():
                    return cat
            return "Другое"

    except Exception as e:
        print(f"Error categorizing: {e}")
        return "Другое"


def preprocess_csv(input_file: str, output_file: str):
    """
    Read CSV, categorize each document, and save to new CSV with category column
    """
    print(f"Reading {input_file}...")

    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    print(f"Found {len(rows)} documents to categorize")

    # Process each row
    categorized_rows = []
    for i, row in enumerate(rows, 1):
        print(f"\nProcessing document {i}/{len(rows)}: {row['header'][:50]}...")

        category = categorize_document(row['header'], row['text'])
        print(f"  Category: {category}")

        # Add category to row
        row['category'] = category
        categorized_rows.append(row)

        # Add delay to avoid rate limits (Mistral free tier has limits)
        if i < len(rows):
            print("  Waiting 2 seconds to avoid rate limit...")
            time.sleep(2)

    # Write to output CSV
    print(f"\nSaving categorized data to {output_file}...")
    fieldnames = ['id', 'url', 'header', 'text', 'category']

    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(categorized_rows)

    print(f"\n✓ Successfully preprocessed {len(categorized_rows)} documents")

    # Show category distribution
    category_counts = {}
    for row in categorized_rows:
        cat = row['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print("\nCategory distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")


if __name__ == '__main__':
    import sys

    input_file = 'sfr_invalidam_data.csv'
    output_file = 'sfr_invalidam_data_categorized.csv'

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        exit(1)

    # Check if user wants to test with limited documents
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("TEST MODE: Processing only first 5 documents")
        print("Run without --test flag to process all documents\n")
        # Modify the function to process only 5 documents in test mode
        import csv
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)[:5]  # Only first 5

        categorized_rows = []
        for i, row in enumerate(rows, 1):
            print(f"\nProcessing document {i}/5: {row['header'][:50]}...")
            category = categorize_document(row['header'], row['text'])
            print(f"  Category: {category}")
            row['category'] = category
            categorized_rows.append(row)
            if i < len(rows):
                print("  Waiting 2 seconds...")
                time.sleep(2)

        output_file = 'sfr_invalidam_data_categorized_test.csv'
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'url', 'header', 'text', 'category'])
            writer.writeheader()
            writer.writerows(categorized_rows)
        print(f"\nTest complete! Saved to {output_file}")
    else:
        preprocess_csv(input_file, output_file)
