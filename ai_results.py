
import json

from utils.gemini import Gemini
from utils.postgres_crud import PostgresCRUD


# def compose_question(events):     
#     request_json = {
#         "instructions": "Fetch Results for below football matches using available web data. Also give me the status either WIN/LOST depending on my earlier prediction and the actual outcome." ,
#         "matches": events,  # Use the 'events' list here
#         "format": {
#             "type": "json",
#             "structure": [
#                 {
#                     "parent_match_id": "string",
#                     "home_team": "string",
#                     "away_team": "string",
#                     "structure": {
#                         "match_id": "string",
#                         "home_results": "integer",
#                         "away_results": "integer",
#                         "status": "string"
#                     }
#                 }
#             ] 
#         },
#         "data_sources": [
#             "Recent match results, weighted by recency",
#             "Team news from official team websites and reputable sports news sources"
#         ]
#     }

#     question = json.dumps(request_json)  # Convert the JSON to a string

#     return question

def compose_question(events):     
    request_json = {
        "instructions": "Fetch Results for below football matches using available web data." ,
        "matches": events, 
        "data_sources": [
            "Recent match results, weighted by recency",
            "Team news from official team websites and reputable sports news sources"
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
        events = PostgresCRUD().get_events(limit, page)
        
        if len(events) == limit:
            page +=1
        else:
            total -= limit
         
        question = compose_question(events)      
        print(question)      
        #questions.append(question)
        
    return questions
                    
if __name__ == '__main__':
    try:
        for question in generate_questions():
            response = Gemini().get_response(question)
            cleaned_response = response.replace('```json', '').replace('```', '').strip()
            for datum in json.loads(cleaned_response):
                print(datum)
                #PostgresCRUD().update_match_results(datum.get('match_id'), datum.get('home_results'), datum.get('away_results'), datum.get('status'))
                
        print(f"Done Fetching Results...")    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except FileNotFoundError as e:
        print(f"Error accessing file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")