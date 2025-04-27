from flask import Flask, request, jsonify, send_from_directory
from elastic import MedicalSearch
from flask_cors import CORS
import os
import mysql.connector
from dotenv import load_dotenv
import jwt
import datetime
from elastic import SymptomSearch  

load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)
PORT = 5001
SECRET_KEY = os.getenv('SECRET_KEY')

mysql_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            database=os.getenv('MYSQL_DATABASES'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )

@app.route('/api/patientSearch', methods=['GET'])
def search():
    query = request.args.get('q', '')
    email = request.args.get('email', '')
    print(email)
    if not query or not email:
        return jsonify({'error': 'Query and email parameters are required'}), 400

    try:
        mysql_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            database=os.getenv('MYSQL_DATABASES'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        cursor = mysql_conn.cursor()

        check_query = """
        SELECT 1 FROM Patient_Search_Log WHERE Email = %s AND Search_text = %s
        """
        cursor.execute(check_query, (email, query))
        exists = cursor.fetchone()
        
        if not exists:
            insert_query = """
            INSERT INTO Patient_Search_Log (Email, Search_text)
            VALUES (%s, %s)
            """
            cursor.execute(insert_query, (email, query))
            mysql_conn.commit()

        search = MedicalSearch()
        results = search.search(query)

        return jsonify({'results': results})

    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        if 'search' in locals():
            search.close()
        if 'cursor' in locals():
            cursor.close()
        if 'mysql_conn' in locals():
            mysql_conn.close()

@app.route("/api/upvote", methods=["POST"])
def upvote_record():
    try:
        record_id = request.args.get('id', '')
        print(record_id)
        if not record_id:
            return jsonify({"error": "Missing recordId"}), 400

        cursor = mysql_conn.cursor()

        update_query = """
            UPDATE Patient_Diagnosis_Records
            SET Upvotes = Upvotes + 1
            WHERE RecordID = %s
        """
        cursor.execute(update_query, (record_id,))
        mysql_conn.commit()

        select_query = """
            SELECT Upvotes FROM Patient_Diagnosis_Records
            WHERE RecordID = %s
        """
        cursor.execute(select_query, (record_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Record not found"}), 404

        new_upvotes = row[0]

        search = MedicalSearch()
        search.update_upvotes(record_id, new_upvotes)
        search.close()

        return jsonify({"message": "Upvote recorded successfully", "new_upvotes": new_upvotes}), 200

    except Exception as e:
        print(f"Upvote error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/downvote", methods=["POST"])
def downvote_record():
    try:
        record_id = request.args.get('id', '')
        if not record_id:
            return jsonify({"error": "Missing recordId"}), 400

        cursor = mysql_conn.cursor()

        update_query = """
            UPDATE Patient_Diagnosis_Records
            SET Upvotes = CASE WHEN Upvotes > 0 THEN Upvotes - 1 ELSE 0 END
            WHERE RecordID = %s
        """
        cursor.execute(update_query, (record_id,))
        mysql_conn.commit()

        select_query = """
            SELECT Upvotes FROM Patient_Diagnosis_Records
            WHERE RecordID = %s
        """
        cursor.execute(select_query, (record_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Record not found"}), 404

        new_upvotes = row[0]

        search = MedicalSearch()
        search.update_upvotes(record_id, new_upvotes)
        search.close()

        return jsonify({"message": "Downvote recorded successfully", "new_upvotes": new_upvotes}), 200

    except Exception as e:
        print(f"Downvote error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/patient-search-log', methods=['GET'])
def get_patient_search_logs():
    email = request.args.get('email', '')

    if not email:
        return jsonify({'error': 'Email parameter is required'}), 400

    try:
        mysql_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            database=os.getenv('MYSQL_DATABASES'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        cursor = mysql_conn.cursor(dictionary=True)

        query = """
        SELECT Email, Search_text
        FROM Patient_Search_Log
        WHERE Email = %s
        LIMIT 3
        """
        cursor.execute(query, (email,))
        logs = cursor.fetchall()

        return jsonify(logs), 200

    except Exception as e:
        print(f"Patient log fetch error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'mysql_conn' in locals():
            mysql_conn.close()

@app.route('/api/qa-search-log', methods=['GET'])
def get_qa_search_logs():
    email = request.args.get('email', '')

    if not email:
        return jsonify({'error': 'Email parameter is required'}), 400

    try:
        mysql_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            database=os.getenv('MYSQL_DATABASES'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        cursor = mysql_conn.cursor(dictionary=True)

        query = """
        SELECT Email, Search_text
        FROM QA_Search_Log
        WHERE Email = %s
        LIMIT 3
        """
        cursor.execute(query, (email,))
        logs = cursor.fetchall()

        return jsonify(logs), 200

    except Exception as e:
        print(f"QA log fetch error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'mysql_conn' in locals():
            mysql_conn.close()

@app.route('/api/keyword-symptoms', methods=['GET'])
def keyword_symptoms():
    keyword = request.args.get('keyword', '')

    if not keyword:
        return jsonify({'error': 'Keyword parameter is required'}), 400

    try:
        mysql_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            database=os.getenv('MYSQL_DATABASES'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        cursor = mysql_conn.cursor(dictionary=True)

        cursor.callproc('GetKeywordCountsForKeyword', [keyword])

        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())

        return jsonify({'results': results}), 200

    except Exception as e:
        print(f"Keyword symptom fetch error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'mysql_conn' in locals():
            mysql_conn.close()


@app.route("/api/symptomGraph", methods=["POST"])
def symptom_graph():
    print("Hello")
    data = request.get_json()
    keyword = data.get("keyword")
    
    print(f"Received keyword: {keyword}")
    
    try:
        mysql_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            database=os.getenv('MYSQL_DATABASES'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        
        cursor = mysql_conn.cursor(dictionary=True)
        
        query = """
        SELECT DoctorSpecialty, COUNT(*) AS NumRecords
        FROM Patient_Diagnosis_Records
        WHERE RecordID IN (
            SELECT RecordID
            FROM Patient_Diagnosis_Records
            WHERE MedicalTranscription LIKE %s OR Keywords LIKE %s
        )
        GROUP BY DoctorSpecialty
        HAVING COUNT(*) >= 2
        ORDER BY NumRecords DESC
        """
        
        search_term = f'%{keyword}%'
        cursor.execute(query, (search_term, search_term))
        results = cursor.fetchall()
        
        if not results:
            print("No results found for keyword:", keyword)
            return jsonify({
                "message": f"No specialties found matching '{keyword}'",
                "results": []
            })
        
        result = []
        for row in results:
            specialty = row.get('DoctorSpecialty', 'Unknown Specialty')
            count = row.get('NumRecords', 0)
            result.append({
                "specialty": specialty,
                "count": count
            })
        
        print("Formatted results:", result)
        
        return jsonify({
            "message": f"Returning specialties matching '{keyword}'",
            "results": result
        })
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'mysql_conn' in locals():
            mysql_conn.close()


@app.route('/api/signup', methods=["POST"])
def signup_function():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    print("Name ", name)
    print("email ", email)
    print("password ", password)
    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    try:
        mysql_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            database=os.getenv('MYSQL_DATABASES'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        cursor = mysql_conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM User_Info WHERE Email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email already exists"}), 409

        query = """
        INSERT INTO User_Info (Name, Email, Password)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (name, email, password))
        mysql_conn.commit()

        token = jwt.encode(
        {
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # token valid for 24 hours
        },
        SECRET_KEY,
        algorithm="HS256"
        )


        return jsonify({"token": token}), 201

    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'mysql_conn' in locals():
            mysql_conn.close()

@app.route('/api/login', methods=["POST"])
def login_function():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        mysql_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            database=os.getenv('MYSQL_DATABASES'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        cursor = mysql_conn.cursor(dictionary=True)

        # 🔍 Find user by email
        query = "SELECT * FROM User_Info WHERE Email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # 🔐 Verify password
        if user["Password"] != password:
            return jsonify({"error": "Incorrect password"}), 401

        # 🔐 Create JWT token
        token = jwt.encode(
            {
                'email': email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({"token": token}), 200

    except Exception as e:
        print("Login error:", e)
        return jsonify({'error': str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'mysql_conn' in locals():
            mysql_conn.close()
            
@app.route('/api/questionSearch', methods=['GET'])
def question_search():
    query = request.args.get('q', '')
    email = request.args.get('email', '')
    
    if not query or not email:
        return jsonify({'error': 'Query and email parameters are required'}), 400

    try:
        mysql_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            database=os.getenv('MYSQL_DATABASES'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        cursor = mysql_conn.cursor()

        check_query = """
        SELECT 1 FROM QA_Search_Log WHERE Email = %s AND Search_text = %s
        """
        cursor.execute(check_query, (email, query))
        exists = cursor.fetchone()

        if not exists:
            insert_query = """
            INSERT INTO QA_Search_Log (Email, Search_text)
            VALUES (%s, %s)
            """
            cursor.execute(insert_query, (email, query))
            mysql_conn.commit()

        search = SymptomSearch()
        results = search.search(query)

        return jsonify({'results': results})

    except Exception as e:
        print(f"Question search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        if 'search' in locals():
            search.close()
        if 'cursor' in locals():
            cursor.close()
        if 'mysql_conn' in locals():
            mysql_conn.close()

@app.route("/api/questionUpvote", methods=["POST"])
def upvote_question():
    try:
        question_id = request.args.get('id', '')
        if not question_id:
            return jsonify({"error": "Missing questionId"}), 400

        cursor = mysql_conn.cursor()

        update_query = """
            UPDATE Question_Answer_Symptoms
            SET Upvotes = Upvotes + 1
            WHERE QuestionID = %s
        """
        cursor.execute(update_query, (question_id,))
        mysql_conn.commit()

        select_query = """
            SELECT Upvotes FROM Question_Answer_Symptoms
            WHERE QuestionID = %s
        """
        cursor.execute(select_query, (question_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Question not found"}), 404

        new_upvotes = row[0]

        search = SymptomSearch()
        search.update_upvotes(question_id, new_upvotes)
        search.close()

        return jsonify({"message": "Upvote recorded successfully", "new_upvotes": new_upvotes}), 200

    except Exception as e:
        print(f"Question upvote error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/focusareas', methods=['GET'])
def get_focus_areas():
    try:
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT 
              TRIM(FocusArea) AS FocusArea,
              COUNT(*) AS NumQuestions,
              MIN(TRIM(Question)) AS ExampleQuestion
            FROM Question_Answer_Symptoms
            WHERE TRIM(FocusArea) IS NOT NULL AND TRIM(FocusArea) != ''
            GROUP BY TRIM(FocusArea)
            HAVING COUNT(*) > 1
            ORDER BY NumQuestions DESC
            LIMIT 10;
        ''')
        results = cursor.fetchall()
        return jsonify({'focusAreas': results})
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Failed to fetch focus areas'}), 500
    
    
@app.route("/api/questionDownvote", methods=["POST"])
def downvote_question():
    try:
        question_id = request.args.get('id', '')
        if not question_id:
            return jsonify({"error": "Missing questionId"}), 400

        cursor = mysql_conn.cursor()

        update_query = """
            UPDATE Question_Answer_Symptoms
            SET Upvotes = CASE WHEN Upvotes > 0 THEN Upvotes - 1 ELSE 0 END
            WHERE QuestionID = %s
        """
        cursor.execute(update_query, (question_id,))
        mysql_conn.commit()

        select_query = """
            SELECT Upvotes FROM Question_Answer_Symptoms
            WHERE QuestionID = %s
        """
        cursor.execute(select_query, (question_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Question not found"}), 404

        new_upvotes = row[0]

        search = SymptomSearch()
        search.update_upvotes(question_id, new_upvotes)
        search.close()

        return jsonify({"message": "Downvote recorded successfully", "new_upvotes": new_upvotes}), 200

    except Exception as e:
        print(f"Question downvote error: {str(e)}")
        return jsonify({"error": str(e)}), 500

    

if __name__ == "__main__":
    print(f"✅ Server running at http://localhost:{PORT}")
    app.run(port=PORT) 