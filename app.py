from flask import Flask
from routes.students import students_blueprint
from  flasgger import Swagger
app = Flask(__name__)

# Register blueprints
app.register_blueprint(students_blueprint)

Swagger(app)
if __name__ == '__main__':
    app.run(debug=True)
