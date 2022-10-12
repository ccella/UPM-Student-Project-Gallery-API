from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
		title = "UPM Computer Science Project Gallery API",  
		description="REST API integrated with Mongodb",
		version="1.0.0")

#Fix course issue.
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

from routes import student
from routes import project

app.include_router(student.router, prefix = "/api/v1/student", tags = ['student'])
app.include_router(project.router, prefix = "/api/v1/project", tags = ['project'])

