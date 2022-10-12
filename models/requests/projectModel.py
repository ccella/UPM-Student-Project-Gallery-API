from pydantic import BaseModel, Field, ValidationError
from enum import Enum
from typing import List, Optional

class projectSchema(BaseModel):
	project_name: str = Field(..., min_length=1, max_length=30, title="Project Name")	
	year_developed: str = Field(..., min_length=4, max_length=6, title="Year Developed")
	project_course: str = Field(..., min_length=1, title="Project Course")	
	project_banner_url: str = Field(..., min_length=1, title="Project Banner URL")
	project_screenshots_url: List[str]
	technologies_used: List[str]
	team_members: List[str] 