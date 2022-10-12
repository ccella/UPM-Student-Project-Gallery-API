from pydantic import BaseModel, Field, ValidationError
from enum import Enum
from typing import List, Optional

class studentSchema(BaseModel):
	student_name: str = Field(..., min_length=1, max_length=30, title="Student Name")	
	student_number: str = Field(..., min_length=1, max_length=24,title="Student Number")
	student_profile_photo: str = Field(..., min_length=1, title="Student Profile Photo")	
	student_projects: Optional[List[str]] = None