from app import app

if __name__ == '__main__':
    # Run the Flask app
    # We disable reloader because it causes issues in some environments
    # We use threaded=True for better performance
    app.run(host='127.0.0.1', port=5002, debug=True, use_reloader=False)
