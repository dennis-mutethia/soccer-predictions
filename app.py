
import os, uuid
from datetime import datetime
from flask import Flask, Response, redirect, render_template, request, url_for
from dotenv import load_dotenv

from broadcast import Broadcast
from utils.helper import Helper
from utils.postgres_crud import PostgresCRUD
from utils.waapi import WaAPI

app = Flask(__name__)

load_dotenv()
waapi_instance_id = os.getenv('WAAPI_INSTANCE_ID')
waapi_token = os.getenv('WAAPI_TOKEN')

today_codes = str(uuid.uuid5(uuid.NAMESPACE_DNS, datetime.now().strftime('%Y%m%d'))).split('-')
#today_codes = ['guest']

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

@app.route('/jackpots/<code>')
def jackpots(code): 
    jackpots = PostgresCRUD().fetch_jackpots()   
    return render_template('jackpots.html', today_codes=today_codes, code=code, header="Jackpot Predictions", jackpots = jackpots )

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
    print(str(request.form)) 
    
    status = request.form.get('status')
    phone_number = request.form.get('phoneNumber')
    if phone_number is not None and status == 'Success': 
        formatted_number = "254" + phone_number[-9:]
        PostgresCRUD().update_subscriber_on_dlr(formatted_number)
        
    return Response(status=200)

@app.route('/subscription-notifications', methods=['POST'])
def subscription_notifications():
    print(str(request.form)) 
    
    phone_number = request.form.get('phoneNumber')
    short_code = request.form.get('shortCode')
    keyword = request.form.get('keyword')
    update_type = request.form.get('updateType')
    
    if phone_number is not None and keyword is not None and keyword.lower() == 'tip':
        formatted_number = "254" + phone_number[-9:]
        status = 1 if update_type == "addition" else 2
        PostgresCRUD().add_or_remove_subscriber(formatted_number, status)
        
    return Response(status=200)

@app.route(f'/webhooks/whatsapp/<security_token>', methods=['POST'])
def handle_webhook(security_token):
    data = request.get_json()

    if not data or 'instanceId' not in data or 'event' not in data or 'data' not in data:
        print('Invalid request')
        return '', 400

    instance_id = data['instanceId']
    event_name = data['event']
    event_data = data['data']

    # check if the security token and the instanceId match in our records
    if str(instance_id) != waapi_instance_id  or waapi_token != security_token:
        print('Authentication failed')
        return '', 401

    # the request is validated and the requester authenticated
    if event_name == 'message':
        message_data = event_data['message']
        message_type = message_data['type']
        
        if message_type == 'chat':
            message_sender_id = message_data['from']  # unique WhatsApp ID
            message_created_at = datetime.fromtimestamp(message_data['timestamp'])  # timestamp is in seconds
            message_content = message_data['body']

            # this is the phone number of the message sender
            message_sender_phone_number = message_sender_id.replace('@c.us', '')
            
            # run your business logic: someone has sent you a WhatsApp message
                
            if 'unsubscribe' in message_content.lower():
                PostgresCRUD().add_or_remove_subscriber(message_sender_phone_number, 2)                
                Broadcast().send_goodbye_message(message_sender_phone_number)        

            elif 'subscribe' in message_content.lower():
                PostgresCRUD().add_or_remove_subscriber(message_sender_phone_number, 1)
                Broadcast().send_welcome_message(message_sender_phone_number)

        return '', 200
    else:
        print(f"Cannot handle this event: {event_name}")
        return '', 404
    
if __name__ == '__main__':
    app.run(debug=True)
