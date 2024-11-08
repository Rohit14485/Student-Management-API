students = {}
next_id = 1

def generate_student_id():
    global next_id
    student_id = next_id
    next_id += 1
    return student_id
