
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Enum, Float
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base


from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum


Base = declarative_base()


# class Book(Base):
#     __tablename__ = "book"
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String)
#     rating = Column(Integer)
#     time_created = Column(DateTime(timezone=True), server_default=func.now())
#     time_updated = Column(DateTime(timezone=True), onupdate=func.now())
#     author_id = Column(Integer, ForeignKey("author.id"))
    
    
    
#     author = relationship("Author")
    
# class Author(Base):
#     __tablename__ = "author"
#     id = Column(Integer, primary_key=True,)
#     name = Column(String)
#     age = Column(Integer)
#     time_created = Column(DateTime(timezone=True), server_default= func.now())
#     time_updated = Column(DateTime(timezone= True), onupdate = func.now())


#When creating users I will use
#UserRole.TEACHER or UserRole.STUDENT

class UserRole(PyEnum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"


#But when querying users I will
#use as string values 'teacher' or 'student'

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole))
    

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index = True)
    title = Column(String, index= True)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User")
    
    
class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key= True, index=True)
    title = Column(String, index= True)
    content = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Course")
    

class Material(Base):
    __tablename__ = 'materials'
    id = Column(Integer,primary_key=True, index = True)
    title = Column(String, index=True)
    content_type = Column(String)
    content = Column(String)
    course_id = Column(Integer, ForeignKey('courses.id'))
    course = relationship('Course')
    

class Progress(Base):
    __tablename__ = 'progress'
    id = Column(Integer,primary_key=True, index = True)
    student_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    completion_status = Column(Enum('started', 'completed', 'in_progress', name='status_types'))
    progress_percentage = Column(Float)
    
    
    


class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    enrolled_date = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User")
    course = relationship("Course")

class Completion(Base):
    __tablename__ = 'completions'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'))
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    completed_date = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User")
    lesson = relationship("Lesson")
