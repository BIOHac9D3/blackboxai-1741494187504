from flask import Flask
from backend.routes.route_manager_final_corrected import init_app

app = Flask(__name__)

# Initialize the application with all routes
init_app(app)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
