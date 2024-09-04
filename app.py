
import uuid
from datetime import datetime
from flask import Flask, jsonify, redirect, render_template, request, url_for

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
            formatted_number = "+254" + phone[-9:]
            #send subscribe push 
            
            PostgresCRUD().add_subscriber(formatted_number)
            
            return redirect(url_for('today', code=code))
    
    return render_template('subscribe.html', today_codes=today_codes, code=code)

@app.route('/terms-and-conditions')
def terms_and_conditions():    
    return render_template('terms-and-conditions.html')

@app.route('/privacy-policy')
def privacy_policy():    
    return render_template('privacy-policy.html')

@app.route('/dlr', methods=['POST'])
def dlr():
    try:
        if request.method == 'POST':
            # Extracting form data
            id = request.form['id']
            status = request.form['status']
            phone_number = request.form['phoneNumber']
            network_code = request.form['networkCode']
            failure_reason = request.form['failureReason']
            retry_count = request.form['retryCount']
            
            # Print the extracted data
            print(f"""
                  id: {id}
                  status: {status}
                  phone_number: {phone_number}
                  network_code: {network_code}
                  failure_reason: {failure_reason}
                  retry_count: {retry_count} 
                  """)

            # If the status is 'Success', update the subscriber in the database
            if status == 'Success': 
                PostgresCRUD().update_subscriber_on_dlr(phone_number)

            # Return a success response
            return 'success', 200

    except KeyError as e:
        # Handle missing form data
        error_message = f"Missing required form field: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 400

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
