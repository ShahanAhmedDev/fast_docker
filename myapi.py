
# ----------/--------------/-----------

from fastapi import FastAPI, HTTPException, Depends
from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy.exc import IntegrityError

import uvicorn
from dotenv import load_dotenv
from schema import UserCreate, UserDisplay, CourseCreate, CourseDisplay, LessonCreate, LessonDisplay, MaterialCreate, MaterialDisplay
from schema import ProgressDisplay, ProgressCreate,EnrollmentBase, EnrollmentDisplay, CompletionBase, CompletionDisplay

from loguru import logger
from typing import List
# from pytest 
from passlib.context import CryptContext
from models import User, Course, Lesson, Material, Progress, Enrollment, Completion, UserRole


import os, sys

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Configure Loguru logger
logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")

#Initialize FAST API and the envs alongside the middleware Db connection
app = FastAPI()
load_dotenv(".env")


app.add_middleware(DBSessionMiddleware, db_url = os.environ["DATABASE_URL"])


# If main is inside localhost, run it locally not inside
# the docker container
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
    



@app.post("/create-user/", response_model=UserDisplay)
def create_user(user: UserCreate):
    try:
        hashed_password = pwd_context.hash(user.password)
        print(f"Hased PAssword is: {hashed_password}")
        db_user = User(name = user.name, 
                    email = user.email, 
                    hashed_password = hashed_password, 
                    role = user.role.value.upper())
        
        # Print the role before returning
        print(f"User Role: {db_user.role}")
        db.session.add(db_user)
        db.session.commit()    
        return db_user
    except IntegrityError:
        db.session.rollback()
        logger.error(f"User creation failed: Email {user.email} already exists.")
        raise HTTPException(status_code=400, detail="Email Already Exists!")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"User creation failed : {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
        

@app.get("/get-user/{user_id}", response_model=UserDisplay)
def get_user(user_id: int):
    try:
        user = db.session.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Retrieved user: {user.name}")
        return user
    except Exception as e:
        logger.error(f"Error retrieving user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



@app.post("/create-course/", response_model=CourseDisplay)
def create_course(course: CourseCreate):
    try:
        current_user = db.session.query(User).filter(User.id == course.creator_id).first()
        
        if not current_user or  current_user.role != UserRole.TEACHER:
            logger.warning(f"Unauthorized attempt to create course by user: {current_user.id}")
            raise HTTPException(status_code=403, detail="Only teachers can create courses, or maybe user doesn't exist!")
            
        db_course = Course(title=course.title, description=course.description, creator_id=course.creator_id)
        db.session.add(db_course)
        db.session.commit()
        logger.info(f"Created course: {db_course.title}")
        return db_course
    except HTTPException as http_exc:
        # Handle HTTP exceptions separately
        raise http_exc
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating course: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



@app.get("/get-course/{course_id}", response_model=CourseDisplay)
def get_course(course_id: int):
    try:
        course = db.session.query(Course).filter(Course.id == course_id).first()
        if not course:
            logger.warning(f"Course not found: {course_id}")
            raise HTTPException(status_code=404, detail="Course not found")
        logger.info(f"Retrieved course: {course.title}")
        return course
    
    except HTTPException as http_exc:
        raise http_exc
        
    except Exception as e:
        logger.error(f"Error retrieving course: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



@app.post("/create-lesson/", response_model=LessonDisplay)
def create_lesson(lesson: LessonCreate, current_user: User = Depends(get_user)):
    try:
        if not current_user or current_user.role != UserRole.TEACHER:
            logger.warning(f"Unauthorized attempt to create course by user: {current_user.id}")
            raise HTTPException(status_code=403, detail="Either user doesn't exist, Else Only teachers can create lessons")
        
        db_lesson = Lesson(title=lesson.title, content=lesson.content, course_id=lesson.course_id)
        db.session.add(db_lesson)
        db.session.commit()
        logger.info(f"Created lesson: {db_lesson.title}")
        return db_lesson
    
    except HTTPException as http_exc:
        # Handle HTTP exceptions separately
        raise http_exc
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating lesson: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/get-lesson/{lesson_id}", response_model=LessonDisplay)
def get_lesson(lesson_id: int):
    try:
        lesson = db.session.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            logger.warning(f"Lesson not found: {lesson_id}")
            raise HTTPException(status_code=404, detail="Lesson not found")
        logger.info(f"Retrieved lesson: {lesson.title}")
        return lesson
    
    except HTTPException as http_exc:
        # Handle HTTP exceptions separately
        raise http_exc
    
    except Exception as e:
        logger.error(f"Error retrieving lesson: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")





@app.post("/create-material/", response_model=MaterialDisplay)
def create_material(material: MaterialCreate, current_user_id: int):
    try:
        # Attempt to retrieve the user and throw execeiption if not found exception
        user = db.session.query(User).filter(User.id == current_user_id).first()
        
        if not user:
            logger.warning(f"User not found: {current_user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        # now check to see if  the current user is a teacher
        if user.role != UserRole.TEACHER:
            logger.warning(f"Unauthorized attempt to create material by user: {current_user_id}")
            raise HTTPException(status_code=403, detail="Only teachers can create materials")

        # Create material
        db_material = Material(title=material.title, content_type=material.content_type, content=material.content, course_id=material.course_id)
        db.session.add(db_material)
        db.session.commit()
        logger.info(f"Created material: {db_material.title}")
        return db_material

    except HTTPException as http_exc:
        # Handle HTTP exceptions, including user not found
        raise http_exc
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating material: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



@app.get("/get-material/{material_id}", response_model=MaterialDisplay)
def get_material(material_id: int):
    try:
        material = db.session.query(Material).filter(Material.id == material_id).first()
        if not material:
            logger.warning(f"Material not found: {material_id}")
            raise HTTPException(status_code=404, detail="Material not found")
        logger.info(f"Retrieved material: {material.title}")
        return material
    except Exception as e:
        logger.error(f"Error retrieving material: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")




@app.post("/create-progress/", response_model=ProgressDisplay)
def create_progress(progress: ProgressCreate, current_user: User = Depends(get_user)):
    try:
        if not current_user or current_user.role != UserRole.STUDENT:
            logger.warning(f"Unauthorized attempt to create course by user: {current_user.id}")
            raise HTTPException(status_code=403, detail="Either Student Doesn't Exist, or You're a dumb Teacher")
        
        db_progress = Progress(student_id=progress.student_id, course_id=progress.course_id, lesson_id=progress.lesson_id, completion_status=progress.completion_status, progress_percentage=progress.progress_percentage)
        db.session.add(db_progress)
        db.session.commit()
        logger.info(f"Created progress for student ID {db_progress.student_id}")
        return db_progress
    
    except HTTPException as http_exc:
        # Handle HTTP exceptions separately
        raise http_exc
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating progress: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


#fix only student
@app.get("/get-progress/{progress_id}", response_model=ProgressDisplay)
def get_progress(progress_id: int):
    try:
        progress = db.session.query(Progress).filter(Progress.id == progress_id).first()
        if not progress:
            logger.warning(f"Progress not found: {progress_id}")
            raise HTTPException(status_code=404, detail="Progress not found")
        logger.info(f"Retrieved progress for student ID {progress.student_id}")
        return progress
    except Exception as e:
        logger.error(f"Error retrieving progress: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")




@app.post("/enroll-in-course/", response_model=EnrollmentDisplay)
def enroll_in_course(enrollment: EnrollmentBase):
    try:
        course = db.session.query(Course).filter(Course.id == enrollment.course_id).first()
        user = db.session.query(User).filter(User.id == enrollment.student_id).first()


        if not course or not user or user.role != UserRole.STUDENT:
            logger.warning("Invalid course or user for enrollment")
            raise HTTPException(status_code=404, detail="Invalid course or user")

        existing_enrollment = db.session.query(Enrollment).filter_by(student_id=enrollment.student_id, course_id=enrollment.course_id).first()
        if existing_enrollment:
            logger.info("User already enrolled in course")
            raise HTTPException(status_code=400, detail="Already enrolled in course")

        new_enrollment = Enrollment(student_id=enrollment.student_id, course_id=enrollment.course_id)
        db.session.add(new_enrollment)
        db.session.commit()
        logger.info(f"User {new_enrollment.student_id} enrolled in course {new_enrollment.course_id}")
        return new_enrollment
    
    except HTTPException as http_exc:
        # Handle HTTP exceptions separately
        raise http_exc
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error enrolling in course: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/get-enrollments/{student_id}",response_model=List[EnrollmentDisplay], )
def get_enrollments(student_id: int):
    try:
        
         # Retrieve the user from the database
        student = db.session.query(User).filter(User.id == student_id).first()
    
        # Check if user exists and if the user is a student
        if not student or student.role != UserRole.STUDENT:
            logger.warning(f"Unauthorized access attempt by user ID: {student_id}");
            raise HTTPException(status_code=403, detail="Only Students can get enrolled in courses.")
        
         # Retrieve enrollments for the student
        enrollments = db.session.query(Enrollment).filter(Enrollment.student_id == student_id).all()
        logger.info(f"Retrieved enrollments for student {student_id}")
        return enrollments
    except HTTPException as http_exc:
        # Handle HTTP exceptions separately
        raise http_exc
    except Exception as e:
        logger.error(f"Error retrieving enrollments: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



@app.post("/mark-lesson-complete/", response_model=CompletionDisplay)
def mark_lesson_complete(completion: CompletionBase):
    try:
        lesson = db.session.query(Lesson).filter(Lesson.id == completion.lesson_id).first()
        user = db.session.query(User).filter(User.id == completion.student_id).first()

        if not lesson or not user or user.role != UserRole.STUDENT:
            logger.warning("Invalid lesson or user for marking completion")
            raise HTTPException(status_code=404, detail="Invalid lesson or user")

        new_completion = Completion(student_id=completion.student_id, lesson_id=completion.lesson_id)
        db.session.add(new_completion)
        db.session.commit()
        logger.info(f"Lesson {new_completion.lesson_id} marked complete for student {new_completion.student_id}")
        return new_completion
    
    except HTTPException as http_exc:
        # Handle HTTP exceptions separately
        raise http_exc
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error marking lesson complete: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/get-completions/{student_id}", response_model=List[CompletionDisplay])

def get_completions(student_id: int,):
    try:
        #      # Retrieve the user from the database
        student = db.session.query(User).filter(User.id == student_id).first()
    
        # Check if user exists and if the user is a student
        if not student or student.role != UserRole.STUDENT:
            logger.warning(f"Unauthorized access attempt by user ID: {student_id}");
            raise HTTPException(status_code=403, detail="Either student doesn't exist or you're a Teacher.")
        completions = db.session.query(Completion).filter(Completion.student_id == student_id).all()
        logger.info(f"Retrieved completions for student {student_id}")
        return completions
    
    except HTTPException as http_exc:
        # Handle HTTP exceptions separately
        raise http_exc
    
    except Exception as e:
        logger.error(f"Error retrieving completions: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
