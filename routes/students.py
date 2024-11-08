from flask import Blueprint, jsonify, request, abort
import requests
import re  # Import for email validation
from models.student_model import students, generate_student_id

students_blueprint = Blueprint('students', __name__)

# Function to validate email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

@students_blueprint.route('/students', methods=['POST'])
def create_student():
    if not request.json or 'name' not in request.json or 'age' not in request.json or 'email' not in request.json:
        abort(400, 'Bad request: Name, age, and email are required.')

    email = request.json['email']
    if not is_valid_email(email):
        abort(400, 'Bad request: Invalid email format.')

    student_id = generate_student_id()
    student = {
        'id': student_id,
        'name': request.json['name'],
        'age': request.json['age'],
        'email': email
    }
    students[student_id] = student
    return jsonify(student), 201

@students_blueprint.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    if student_id not in students:
        abort(404, f'Student with ID {student_id} not found.')

    if not request.json:
        abort(400, 'Bad request: Must be JSON data.')

    email = request.json.get('email')
    if email and not is_valid_email(email):
        abort(400, 'Bad request: Invalid email format.')

    student = students[student_id]
    student['name'] = request.json.get('name', student['name'])
    student['age'] = request.json.get('age', student['age'])
    student['email'] = email if email else student['email']

    return jsonify(student)


@students_blueprint.route('/students/<int:student_id>/summary', methods=['GET'])
def student_summary(student_id):
    student = students.get(student_id)
    if student is None:
        abort(404, f'Student with ID {student_id} not found.')

    student_string = f'{student}'
    ollama_url = "http://localhost:11434/api/generate"
    prompt = f"Generate a short summary of this {student_string}"

    try:
        response = requests.post(ollama_url, json={'prompt': prompt, 'model': 'llama3.2:1b', 'stream': False})
        summary = response.json().get('response', 'No summary available')
        return jsonify({'summary': summary})
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        abort(500, f"Failed to generate summary from Ollama: {e}")
