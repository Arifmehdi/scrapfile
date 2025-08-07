import json

def main():
    try:
        # Read the extracted JSON data
        with open(r"C:\laragon\www\scrapfile\laboratory\bikroy.com\extracted_json.txt", "r", encoding="utf-8") as f:
            json_data = f.read()

        # Parse the JSON data
        data = json.loads(json_data)

        # Save the formatted JSON data to a new file
        with open(r"C:\laragon\www\scrapfile\laboratory\bikroy.com\pretty_json.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print("Successfully created pretty_json.json")

    except json.JSONDecodeError as e:
        print(f"Error: The file 'extracted_json.txt' does not contain valid JSON.\nDetails: {e}")

if __name__ == "__main__":
    main()
