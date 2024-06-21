import mysql.connector
import os
import anthropic
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
home_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, home_path)
import config

cf = config.config()
cnx = mysql.connector.connect(user=cf.DATABASE_USER, password=cf.DATABASE_PASSWORD, host=cf.DATABASE_HOST, database='database')

app = Flask(__name__)
CORS(app)

@app.route('/api/claude-ai', methods=['POST'])
def claude_ai():
    AI_TOKEN_CLAUDE = cf.AI_TOKEN_CLAUDE

    client = anthropic.Anthropic(
        api_key = AI_TOKEN_CLAUDE
    )

    data = request.get_json()

    _messages = data.get('allMessages', None)

    
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system="以下是你的設定: " + repr({
            "chinese_name": "陳泊叡",
            "main_name": "Bandai",
            "english_name": ["Bong", "Patrick"],
            "born_day": "27 Oct 2000",
            "education_level": "B.M.W (Bachelor of Management & Waiter)",
            "university": "香港恆生大學",
            "workplace": "大寶冰室",
            "main_language": "廣東話",
            "job": "Senior Waiter"
        }),
        messages=_messages
    )

    ai_response = message.content[0].text

    _message = {
        "role": "assistant",
        "content": ai_response
    }

    all_messages = _messages + [_message]

    conversation_id = -1

    if 'conversationId' in data and data.get('conversationId', -1) != -1:
        conversation_id = data.get('conversationId', -1)

        cursor = cnx.cursor()
        query = ("UPDATE claude_ai_conversation SET content = %s, time_stamp = NOW() WHERE conversation_id = %s")
        cursor.execute(query, (str(all_messages), conversation_id))
        cnx.commit()
        cursor.close()
    elif 'conversationId' not in data or conversation_id == -1:
        content = str(all_messages)

        cursor = cnx.cursor()
        query = ("INSERT INTO claude_ai_conversation (content, time_stamp) VALUES (%s, NOW())")
        cursor.execute(query, (content,))
        conversation_id = cursor.lastrowid
        cnx.commit()
        cursor.close()

    response = {
        "conversationId": conversation_id,
        "aiResponse": ai_response,
        "allMessages": all_messages
    }

    return response

@app.route('/api/mathjax/insert', methods=['POST'])
def api_mathjax_insert():
    data = request.get_json()

    tab_name = data.get('tabName', None)
    content = data.get('content', None)
    sequence = data.get('sequence', None)

    response = {}

    if tab_name is not None and content is not None and sequence is not None:
        cursor = cnx.cursor()
        query = ("INSERT INTO mathjax (tab_name, content, sequence) VALUES (%s, %s, %s)")
        cursor.execute(query, (tab_name, content, sequence))
        try:
            cnx.commit()
            response = {
                "error": 0
            }
        except Exception as e:
            response = {
                "error": -2,
                "message": str(e)
            }
        finally:
            cursor.close()
    else:
        response = {
            "error": -1
        }

    return response

@app.route('/api/mathjax/index', methods=['GET'])
def api_mathjax_index():
    cursor = cnx.cursor()
    query = ("SELECT * FROM mathjax ORDER BY sequence ASC")
    cursor.execute(query)

    response = []

    for (mathjax_id, tab_name, content, sequence) in cursor:
        response.append({
            "id": mathjax_id,
            "tabName": tab_name,
            "content": content,
            "sequence": sequence
        })

    cnx.commit()
    cursor.close()

    return jsonify(response)

@app.route('/api/mathjax/delete', methods=['POST'])
def api_mathjax_delete():
    data = request.get_json()

    mathjax_id = data.get('id', None)

    response = {}

    if mathjax_id is not None:
        cursor = cnx.cursor()
        query = ("DELETE FROM mathjax WHERE mathjax_id = %s")
        cursor.execute(query, (mathjax_id,))

        try:
            cnx.commit()
            response = {
                "error": 0
            }
        except Exception as e:
            response = {
                "error": -2,
                "message": str(e)
            }
        finally:
            cursor.close()
    else:
        response = {
            "error": -1
        }

    return response

@app.route('/api/mathjax/update', methods=['POST'])
def api_mathjax_update():
    data = request.get_json()

    mathjax_id = data.get('id', None)
    tab_name = data.get('tabName', None)
    content = data.get('content', None)
    sequence = data.get('sequence', None)

    response = {}

    if mathjax_id is not None and tab_name is not None and content is not None and sequence is not None:
        cursor = cnx.cursor()
        query = ("UPDATE mathjax SET tab_name = %s, content = %s, sequence = %s WHERE mathjax_id = %s")
        cursor.execute(query, (tab_name, content, sequence, mathjax_id))

        try:
            cnx.commit()
            response = {
                "error": 0
            }
        except Exception as e:
            response = {
                "error": -2,
                "message": str(e)
            }
        finally:
            cursor.close()
    else:
        response = {
            "error": -1
        }

    return response

@app.route('/mathjax/insert', methods=['GET', 'POST'])
def mathjax_insert():
    return render_template('mathjax_insert.html')

@app.route('/mathjax', methods=['GET'])
def mathjax():
    return render_template('mathjax_index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)