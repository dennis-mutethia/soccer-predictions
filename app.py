
import uuid
from datetime import datetime
from flask import Flask, Response, jsonify, redirect, render_template, request, url_for

from utils.helper import Helper
from utils.postgres_crud import PostgresCRUD

app = Flask(__name__)

today_codes = str(uuid.uuid5(uuid.NAMESPACE_DNS, datetime.now().strftime('%Y%m%d'))).split('-')

@app.errorhandler(404)
def page_not_found(e):
    # Redirect to a specific endpoint, like 'today', or a custom 404 page
    return redirect(url_for('today', code='guest')), 302
  
@app.route('/<code>')
def today(code): 
    matches, played, won = Helper().fetch_matches('', '=', '')
    return render_template('index.html', today_codes=today_codes, code=code, header="Today Games Predictions", matches=matches, played=played, won=won, get_background_color=Helper().get_background_color, highlight_analysis=Helper().highlight_analysis)

@app.route('/tomorrow/<code>')
def tomorrow(code):    
    matches, played, won = Helper().fetch_matches('+1', '=', '')
    return render_template('index.html', today_codes=today_codes, code=code, header="Tomorrow Games Predictions", matches = matches, played = played, won = won, get_background_color=Helper().get_background_color, highlight_analysis=Helper().highlight_analysis )

@app.route('/yesterday/<code>')
def yesterday(code):    
    matches, played, won = Helper().fetch_matches('-1', '=')
    return render_template('index.html', today_codes=today_codes, code=code, header="Yesterday's Predictions Results", matches = matches, played = played, won = won, get_background_color=Helper().get_background_color, highlight_analysis=Helper().highlight_analysis )

@app.route('/history/<code>')
def history(code):    
    matches, played, won = Helper().fetch_matches('-7', '>=')
    return render_template('index.html', today_codes=today_codes, code=code, header="Last 7-Days Predictions Results", matches = matches, played = played, won = won, get_background_color=Helper().get_background_color, highlight_analysis=Helper().highlight_analysis )

@app.route('/download/<code>')
def download(code):    
    return render_template('download.html', today_codes=today_codes, code=code)

@app.route('/subscribe/<code>', methods=['GET', 'POST'])
def subscribe(code):   
    if request.method == 'POST':     
        if request.form['action'] == 'subscribe':
            phone = request.form['phone']
            formatted_number = "254" + phone[-9:]
            #send subscribe push 
            
            PostgresCRUD().add_or_remove_subscriber(formatted_number, 0)
            
            return redirect(url_for('today', code=code))
    
    return render_template('subscribe.html', today_codes=today_codes, code=code)

@app.route('/terms-and-conditions')
def terms_and_conditions():    
    return render_template('terms-and-conditions.html')

@app.route('/privacy-policy')
def privacy_policy():    
    return render_template('privacy-policy.html')

@app.route('/delivery-reports', methods=['POST'])
def delivery_reports():
    data = request.get_json(force=True)
    print(data) 
    
    status = data['status']
    phone_number = data['phoneNumber']
    if status == 'Success': 
        formatted_number = "254" + phone_number[-9:]
        PostgresCRUD().update_subscriber_on_dlr(formatted_number)
        
    return Response(status=200)

@app.route('/subscription-notifications', methods=['POST'])
def subscription_notifications():
    data = request.get_json(force=True)
    print(data) 
    
    phone_number = data['phoneNumber']
    short_code = data['shortCode']
    keyword = data['keyword']
    update_type = data['updateType']
    formatted_number = "254" + phone_number[-9:]
    status = 1 if update_type == "addition" else 2
    
    if keyword.lower() == 'tip':
        PostgresCRUD().add_or_remove_subscriber(formatted_number, status)
        
    return Response(status=200)

if __name__ == '__main__':
    app.run(debug=True)
