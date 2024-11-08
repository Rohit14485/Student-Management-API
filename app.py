from flask import Flask
from routes.students import students_blueprint

app = Flask(__name__)

# Register blueprints
app.register_blueprint(students_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
