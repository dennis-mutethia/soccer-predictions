import uuid
from datetime import datetime
from flask import Flask, redirect, render_template, url_for
from src.utils.postgres_crud import PostgresCRUD

app = Flask(__name__)

class Match:
    def __init__(self):
        self.kickoff = None
        self.home_team = None
        self.away_team = None
        self.prediction = None
        self.overall_prob = 0
        self.over_0_5_home_perc = 0
        self.over_0_5_away_perc = 0
        self.over_1_5_home_perc = 0
        self.over_1_5_away_perc = 0
        self.over_2_5_home_perc = 0
        self.over_2_5_away_perc = 0
        self.over_3_5_home_perc = 0
        self.over_3_5_away_perc = 0
        self.home_results = None
        self.status = None
        self.away_results = None
        self.analysis = None

def get_background_color(perc):
    color_map = [
        (100, 'green'),
        (90, 'limegreen'),
        (80, 'lime'),
        (70, 'lawngreen'),
        (60, 'yellow'),
        (50, 'orange'),
        (40, 'darkorange'),
        (30, 'tomato'),
        (20, 'orangered')
    ]

    for threshold, color in color_map:
        if perc >= threshold:
            return color
    return 'red'

def highlight_analysis(analysis):
    analysis = analysis.replace("a Very Low Chance", 'a <span style="background-color: red border-radius: 5px">Very Low Chance</span>')
    analysis = analysis.replace("a Low Chance", 'a <span style="background-color: tomato border-radius: 5px">Low Chance</span>')
    analysis = analysis.replace("Uncertainty", '<span style="background-color: yellow border-radius: 5px">Uncertainty</span>')
    analysis = analysis.replace("Medium Chance", '<span style="background-color: lawngreen border-radius: 5px">Medium Chance</span>')
    analysis = analysis.replace("a High Chance", 'a <span style="background-color: lime border-radius: 5px">High Chance</span>')  
    analysis = analysis.replace("a Very High Chance", 'a <span style="background-color: green border-radius: 5px">Very High Chance</span>')
    return analysis

def fetch_matches(day, comparator='=', status="AND status IS NOT NULL"):
    matches = []
    played = 0
    won = 0
    for open_match in PostgresCRUD().fetch_matches(day, comparator, status):
        match = Match()
        match.kickoff = open_match[1]
        match.home_team = open_match[2]
        match.away_team = open_match[3]
        match.prediction = open_match[4]    
        match.over_0_5_home_perc = int(open_match[9])
        match.over_0_5_away_perc = int(open_match[10]) 
        match.over_1_5_home_perc = int(open_match[11])
        match.over_1_5_away_perc = int(open_match[12])
        match.over_2_5_home_perc = int(open_match[13]) 
        match.over_2_5_away_perc = int(open_match[14])
        match.over_3_5_home_perc = int(open_match[15]) 
        match.over_3_5_away_perc = int(open_match[16])
        match.home_results = open_match[17] 
        match.status = open_match[18] 
        match.away_results = open_match[19] 
        match.overall_prob = int(open_match[21])    
        match.analysis = open_match[22]
        matches.append(match)
        if match.status is not None:
            played += 1
            won += 0 if match.status == 'LOST' else 1
            
    return matches, played, won

today_code = str(uuid.uuid5(uuid.NAMESPACE_DNS, datetime.now().strftime('%Y%m%d'))).replace('-', '')[:8]

@app.errorhandler(404)
def page_not_found(e):
    # Redirect to a specific endpoint, like 'today', or a custom 404 page
    return redirect(url_for('today', code='guest')), 302
  
@app.route('/<code>')
def today(code): 
    matches, played, won = fetch_matches('', '=', '')
    return render_template('index.html', today_code=today_code, code=code, header="Today Games Predictions", matches=matches, played=played, won=won, get_background_color=get_background_color, highlight_analysis=highlight_analysis)

@app.route('/tomorrow/<code>')
def tomorrow(code):    
    matches, played, won = fetch_matches('+1', '=', '')
    return render_template('index.html', today_code=today_code, code=code, header="Tomorrow Games Predictions", matches = matches, played = played, won = won, get_background_color=get_background_color, highlight_analysis=highlight_analysis )

@app.route('/yesterday/<code>')
def yesterday(code):    
    matches, played, won = fetch_matches('-1', '=')
    return render_template('index.html', today_code=today_code, code=code, header="Yesterday's Predictions Results", matches = matches, played = played, won = won, get_background_color=get_background_color, highlight_analysis=highlight_analysis )

@app.route('/history/<code>')
def history(code):    
    matches, played, won = fetch_matches('-7', '>=')
    return render_template('index.html', today_code=today_code, code=code, header="Last 7-Days Predictions Results", matches = matches, played = played, won = won, get_background_color=get_background_color, highlight_analysis=highlight_analysis )

@app.route('/download/<code>')
def download(code):    
    return render_template('download.html', today_code=today_code, code=code)

if __name__ == '__main__':
    app.run(debug=True)
