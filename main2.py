from flask import Flask, jsonify, request, abort
import requests
import string

app = Flask(__name__)

# In-memory data structure for storing students
students = {}
next_id = 1

# Helper function to generate unique student IDs
def generate_student_id():
    global next_id
    student_id = next_id
    next_id += 1
    return student_id

# Endpoint to create a new student
@app.route('/students', methods=['POST'])
def create_student():
    if not request.json or 'name' not in request.json or 'age' not in request.json or 'email' not in request.json:
        abort(400, 'Bad request: Name, age, and email are required.')
    
    student_id = generate_student_id()
    student = {
        'id': student_id,
        'name': request.json['name'],
        'age': request.json['age'],
        'email': request.json['email']
    }
    students[student_id] = student
    return jsonify(student), 201

# Endpoint to get all students
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(list(students.values()))

# Endpoint to get a specific student by ID
@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = students.get(student_id)
    if student is None:
        abort(404, f'Student with ID {student_id} not found.')
    return jsonify(student)

# Endpoint to update a student by ID
@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    if student_id not in students:
        abort(404, f'Student with ID {student_id} not found.')
    
    if not request.json:
        abort(400, 'Bad request: Must be JSON data.')

    student = students[student_id]
    student['name'] = request.json.get('name', student['name'])
    student['age'] = request.json.get('age', student['age'])
    student['email'] = request.json.get('email', student['email'])

    return jsonify(student)

# Endpoint to delete a student by ID
@app.route('/students/<int:student_id>/summary', methods=['GET'])
def student_summary(student_id):
    
    student = students.get(student_id)
    student_string = f'{student}'
    if student is None:
        abort(404, f'Student with ID {student_id} not found.')
    # Corrected Ollama URL (no /ollama path)
    ollama_url = "http://localhost:11434/api/generate"
    prompt = f"Generate a short summary of this {student_string}"
    print(prompt)
    
    try:
        response = requests.post(ollama_url, json={'prompt': prompt,'model': 'llama3.2:1b', 'stream': False})
        
        # response.raise_for_status()  # Raise an error for HTTP error codes
        summary = response.json().get('response', 'No summary available')
        return jsonify({'summary': summary})
    except requests.exceptions.RequestException as e:
        # Log the error and respond with a message
        print(f"Error connecting to Ollama: {e}")
        abort(500, f"Failed to generate summary from Ollama: {e}")

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
