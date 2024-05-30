import mysql.connector
import datetime
import os
import anthropic
from flask import Flask, request, jsonify
import sys
home_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, home_path)
import config

cf = config.config()
cnx = mysql.connector.connect(user=cf.DATABASE_USER, password=cf.DATABASE_PASSWORD, host=cf.DATABASE_HOST, database='database')

app = Flask(__name__)

@app.route('/api/claude-ai', methods=['POST'])
def claude_ai():
    AI_TOKEN_CLAUDE = cf.AI_TOKEN_CLAUDE

    client = anthropic.Anthropic(
        api_key = AI_TOKEN_CLAUDE
    )

    message = client.messages.create(
        model = "claude-3-sonnet-20240229",
        max_tokens = 1000,
        temperature = 0,
        system = "You are a fresh graduate from '香港恆生大學', work in '大寶冰室' now. Do not mention it except I mention about it."

    )

    data = request.get_json()
    cursor = cnx.cursor()
    cursor.execute("SELECT ")
    return jsonify(data)

@app.route('/api/test', methods=['POST'])
def test():
    data = request.get_json()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)