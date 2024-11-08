from flask import Blueprint, jsonify, request, abort
import requests
import re
from models.student_model import students, generate_student_id

students_blueprint = Blueprint('students', __name__)

# Function to validate email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

@students_blueprint.route('/students', methods=['POST'])
def create_student():
    """
    Create a new student.
    ---
    tags:
      - Students
    parameters:
      - in: body
        name: student
        required: true
        description: The student to create
        schema:
          type: object
          required:
            - name
            - age
            - email
          properties:
            name:
              type: string
              example: "John Doe"
            age:
              type: integer
              example: 20
            email:
              type: string
              example: "johndoe@example.com"
    responses:
      201:
        description: Student created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "John Doe"
            age:
              type: integer
              example: 20
            email:
              type: string
              example: "johndoe@example.com"
      400:
        description: Bad request (missing or invalid fields)
    """
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

@students_blueprint.route('/students', methods=['GET'])
def get_students():
    """
    Get all students.
    ---
    tags:
      - Students
    responses:
      200:
        description: List of all students
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "John Doe"
              age:
                type: integer
                example: 20
              email:
                type: string
                example: "johndoe@example.com"
    """
    return jsonify(list(students.values()))

@students_blueprint.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """
    Get a student by ID.
    ---
    tags:
      - Students
    parameters:
      - name: student_id
        in: path
        type: integer
        required: true
        description: The ID of the student
    responses:
      200:
        description: Student data
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "John Doe"
            age:
              type: integer
              example: 20
            email:
              type: string
              example: "johndoe@example.com"
      404:
        description: Student not found
    """
    student = students.get(student_id)
    if student is None:
        abort(404, f'Student with ID {student_id} not found.')
    return jsonify(student)

@students_blueprint.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """
    Update a student by ID.
    ---
    tags:
      - Students
    parameters:
      - name: student_id
        in: path
        type: integer
        required: true
        description: The ID of the student
      - in: body
        name: student
        description: The student data to update
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Updated Name"
            age:
              type: integer
              example: 21
            email:
              type: string
              example: "updatedemail@example.com"
    responses:
      200:
        description: Updated student data
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Updated Name"
            age:
              type: integer
              example: 21
            email:
              type: string
              example: "updatedemail@example.com"
      404:
        description: Student not found
      400:
        description: Bad request (invalid data)
    """
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
    student['email'] = request.json.get('email', student['email'])

    return jsonify(student)

@students_blueprint.route('/students/<int:student_id>/summary', methods=['GET'])
def student_summary(student_id):
    """
    Generate a summary for a student.
    ---
    tags:
      - Students
    parameters:
      - name: student_id
        in: path
        type: integer
        required: true
        description: The ID of the student
    responses:
      200:
        description: Generated summary
        schema:
          type: object
          properties:
            summary:
              type: string
              example: "Summary of student John Doe, aged 20..."
      404:
        description: Student not found
      500:
        description: Internal server error (failure to connect to summary service)
    """
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
        abort(500, f"Failed to generate summary from external service: {e}")
