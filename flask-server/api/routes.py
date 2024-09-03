from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, origins='*')

@app.route("/api/ask", methods=["POST"])
def answer_prompt():
  # Get the prompt sent from the React frontend
  data = request.get_json()
  if not data:
    return jsonify({"error": "Missing prompt in request body"}), 400

  #LLM processing

  # Return the answer as JSON
  return jsonify({"message": "received"})

@app.route('/handle-query', methods=['POST'])
def handle_query():
  # handles embedding the user's question,
  # finding relevant context from the vector database,
  # building the prompt for the LLM,
  # and sending the prompt to the LLM's API to get an answer.
  pass

if __name__ == "__main__":
  app.run(debug=True, port=8080)

  # google sheet - problems face