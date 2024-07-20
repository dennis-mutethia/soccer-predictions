from app import app  # Import the Flask app object from app.py

if __name__ == "__main__":
    app.run()

# WSGI callable
def application(environ, start_response):
    return app(environ, start_response)
