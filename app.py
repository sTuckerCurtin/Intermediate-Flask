from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from marshmallow import post_load, fields, ValidationError
from dotenv import load_dotenv
from os import environ

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Creating student_course junction table
student_course = db.Table('student_course',
                    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                    db.Column('grade', db.String(5))
                    )

# Models
class Student(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer())
    gpa = db.Column(db.Float())

class Course(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    instructor_id = db.Column(db.Integer(), db.ForeignKey('instructor.id'))
    credits = db.Column(db.Integer())
    instructor=db.relationship("Instructor")
    students = db.relationship("Student", secondary=student_course, backref='courses')

class Instructor(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    hire_date = db.Column(db.Date())



# Schemas
class StudentSchema(ma.Schema):
    id = fields.Integer(primary_key=True)
    first_name = fields.String(requred=True)
    last_name = fields.String(required=True)
    year = fields.Integer(requred=True)
    gpa = fields.Float(required=True)

    class Meta:
        fields = ("id", "first_name", "last_name", "year", "gpa")



student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

class StudentNameSchema(ma.Schema):
    first_name = fields.String(requred=True)
    last_name = fields.String(required=True)
    class Meta:
        fields = ("first_name", "last_name")
student_name_scehma = StudentNameSchema()
students_names_schema = StudentNameSchema(many=True)

# Resources
class StudentListResouce(Resource):
    def get(self):
        order_by = request.args.get("order", default=None)

        if order_by == "last_name":
            all_students = Student.query.order_by(Student.last_name).all()
        elif order_by == "gpa":
            all_students = Student.query.order_by(Student.gpa).all()
        else:
            all_students = Student.query.all()



        
        return students_schema.dump(all_students), 201
    
class FullCourseDetailResource(Resource):
    def get(self, course_id):
        course = Course.query.get(course_id)

        if not course:
            return{"message": "Course Not Found!"}, 404
        
        course_name = course.name
        instructor_name = f"{course.instructor.first_name} {course.instructor.last_name}"
        num_of_students = len(course.students)
        serialized_students = students_names_schema.dump(course.students)


        response = {
            "Course Name": course_name,
            "Instructor name" : instructor_name,
            "student info" : {
                "number of students" : num_of_students,
                "students" : serialized_students
            }
        }
        return response


# Routes
api.add_resource(StudentListResouce, "/api/students")
api.add_resource(FullCourseDetailResource, "/api/course_details/<int:course_id>")


