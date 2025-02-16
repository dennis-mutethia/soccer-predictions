
import json
from pathlib import Path
from utils.betika import Betika
from utils.gemini import Gemini

import json
from pathlib import Path


def compose_question(events):     
    request_json = {
        "instructions": "Predict the outcome of the following football matches using available web data, including team form and Twitter feeds. Provide predictions for the following markets: 1 (Home Win), X (Draw), 2 (Away Win), Over 1.5 goals, Over 2.5 goals, and Both Teams To Score (BTTS). For each market, provide a probability percentage. Return the results as a JSON array of objects, where each object represents a match." ,
        "matches": events,  # Use the 'events' list here
        "format": {
            "type": "json",
            "structure": [
                {
                    "parent_match_id": "string",
                    "home_team": "string",
                    "away_team": "string",
                    "predictions": {
                        "BTTS": "probability",
                        "OVER 2.5": "probability",
                        "1": "probability",
                        "X": "probability",
                        "2": "probability",
                        "OVER 1.5": "probability"
                    }
                }
            ] 
        },
        "data_sources": [
            "Recent match results for the last 7 games, weighted by recency",
            "League standings",
            "Head-to-head records for the last 5 meetings",
            "Player statistics: goals and assists for key players this season, current injuries/suspensions",
            "Team news from official team websites and reputable sports news sources",
            "Expert predictions from ESPN and Sky Sports",
            "Weather forecast for the match location",
            "Home form for Team A, away form for Team B",
            "Tweets from official team accounts and reputable sports journalists covering the league",
            "Aggregate fan sentiment from Twitter (treat with caution)",
            "Team information from Wikipedia",
            "Player transfer data from Transfermarkt"
        ]
    }

    question = json.dumps(request_json)  # Convert the JSON to a string

    return question

def generate_questions():
    questions = []        
    total = 16
    limit = 15
    page = 1
    while limit*page < total:
        total, page, events = Betika().get_events(limit, page)
         
        question = compose_question(events)            
        questions.append(question)
        
    return questions
                    



if __name__ == '__main__':
    try:
        # Delete the file if it exists
        file_path = Path('predictions.json')
        if file_path.exists():
            file_path.unlink()

        # Initialize an empty list to store all responses
        all_data = []

        for question in generate_questions():
            response = Gemini().get_response(question)
            # Clean and parse the JSON response
            cleaned_response = response.replace('```json', '').replace('```', '').strip()
            data = json.loads(cleaned_response)
            print(f"Added {len(data)} matches...")
            
            # Append the current data to all_data list
            all_data.extend(data)  # Use extend because data is already a list
            
            # Write updated data to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=4, ensure_ascii=False)
        print(f"Done Predicting. Total = {len(all_data)} matches...")    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except FileNotFoundError as e:
        print(f"Error accessing file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")