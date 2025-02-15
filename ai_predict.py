
import json
from pathlib import Path
from utils.betika import Betika
from utils.gemini import Gemini

import json
from pathlib import Path

if __name__ == '__main__':
    try:
        # Delete the file if it exists
        file_path = Path('predictions.json')
        if file_path.exists():
            file_path.unlink()

        # Initialize an empty list to store all responses
        all_data = []

        for question in Betika().generate_questions():
            response = Gemini().get_response(question)
            # Clean and parse the JSON response
            cleaned_response = response.replace('```json', '').replace('```', '').strip()
            data = json.loads(cleaned_response)
            #print(data)
            
            # Append the current data to all_data list
            all_data.extend(data)  # Use extend because data is already a list
            
            # Write updated data to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=4, ensure_ascii=False)
                
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except FileNotFoundError as e:
        print(f"Error accessing file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")