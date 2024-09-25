from flask import Blueprint, request, jsonify
# from .auth import register_user, login_user
from flask_cors import CORS

# Create a Blueprint for the API routes
api = Blueprint('api', __name__)
cors = CORS(api, origins='*')

@api.route("/api/ask", methods=["POST"])
def answer_prompt():
    # Get the prompt sent from the React frontend
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing prompt in request body"}), 400

    # LLM processing

    # Return the answer as JSON
    return jsonify({"message": "received"})

@api.route('/handle-query', methods=['POST'])
def handle_query():
    # handles embedding the user's question,
    # finding relevant context from the vector database,
    # building the prompt for the LLM,
    # and sending the prompt to the LLM's API to get an answer.
    pass

# @app.route('/register', methods=['POST'])
# def register():
#     data = request.json
#     register_user(data['username'], data['password'])
#     return {'message': 'User registered successfully'}

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     if login_user(data['username'], data['password']):
#         return {'message': 'Login successful'}
#     return {'message': 'Invalid credentials'}, 401