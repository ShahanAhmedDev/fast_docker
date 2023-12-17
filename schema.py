#Precribe what data will be received from the API

from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime



# class Book(BaseModel):
#     title: str
#     rating: int
#     author_id: int
    
#     class Config:
#         orm_mode = True
        
        
# class Author(BaseModel):
#     name: str
#     age: int
    
#     class Config:
#         orm_mode = True
        


class UserRole(str, Enum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    
class UserBase(BaseModel):
    name: str
    email: str
    role: UserRole
    

class UserCreate(UserBase):
    password: str
    
    
class UserDisplay(UserBase):
    id: int
    
    class Config:
        orm_mode = True



class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None


class CourseCreate(CourseBase):
    creator_id: int
    
    

class CourseDisplay(CourseBase):
    id: int
    creator: UserDisplay
    
    class Config:
        orm_mode = True
        

class LessonBase(BaseModel):
    title: str
    content: str
    
    
class LessonCreate(LessonBase):
    course_id: int


class LessonDisplay(LessonBase):
    id: int
    class Config:
        orm_mode = True
    
    
class MaterialBase(BaseModel):
    title: str
    content_type: str
    content: str

class MaterialCreate(MaterialBase):
    course_id: int

class MaterialDisplay(MaterialBase):
    id: int
    class Config:
        orm_mode = True

class ProgressBase(BaseModel):
    completion_status: str
    progress_percentage: float

class ProgressCreate(ProgressBase):
    student_id: int
    course_id: int
    lesson_id: int

class ProgressDisplay(ProgressBase):
    id: int
    class Config:
        orm_mode = True
        


class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int

class EnrollmentDisplay(EnrollmentBase):
    id: int
    enrolled_date: datetime
    class Config:
        orm_mode = True

class CompletionBase(BaseModel):
    student_id: int
    lesson_id: int

class CompletionDisplay(CompletionBase):
    id: int
    completed_date: datetime
    class Config:
        orm_mode = True
