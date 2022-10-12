from fastapi import APIRouter, Path, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from typing import List
from starlette.responses import JSONResponse
from starlette.status import *

router = APIRouter()

import pymongo
import json
import bson
from bson import ObjectId
from pymongo import MongoClient
from typing import Optional
from fastapi import Query

from models.requests.studentModel import studentSchema
from models.objects.studentObject import Student

connection_url = "mongodb+srv://upmdev:cs127@cluster0.1ghnf.mongodb.net/Gallery_Projects?retryWrites=true&w=majority"
client = pymongo.MongoClient(connection_url)
Gallery = client["Project_Gallery"] #db
Students = Gallery["Students"] # table/collection created 
Projects = Gallery["Projects"] # table/collection created 

#####helper functions####
def isValidUrl(url: str):
	if url[-4:] == ".png" or url[-4:] == ".jpg":
		return True
	else:
		return False

def hasLetters(inputString: str):
    return any(char.isalpha() for char in inputString)

@router.get('/get-all-students')
def get_all_students():
	"""
	Returns all students
	"""
	student_list = []
	for student in Students.find():
		student["_id"] = str(student["_id"])
		student["student_projects"] = str(student["student_projects"])
		student_list.append(student)
	
	studentDict = {
		"Students": student_list
	}

	return student_list

@router.post('/')
def insert_student(student: studentSchema):
	"""
	 Register a single student in the database
	"""
	
	# initialize status code and msg to None
	status_code = None
	msg = None

	if not isValidUrl(student.student_profile_photo):
		return JSONResponse(status_code=400, content={"msg":"Invalid image format!"})

	if hasLetters(student.student_number):
		return JSONResponse(status_code=400, content={"msg":"Invalid student number format!"})

	if student.student_projects != ["string"]:
		return JSONResponse(status_code=400,content={"msg":"The student projects field cannot be edited!"})

	student_entry = []
	try:
		student_entry = { "student_name": student.student_name, "student_number": student.student_number, 
		"student_profile_photo": student.student_profile_photo, "student_projects" : []}
		
		Students.insert_one(student_entry) #insert to db

		if student_entry:
			status_code = 201
			msg = 'Student successfully inserted!'

	except Exception as e:
		status_code = 500
		msg = e

	return JSONResponse(status_code=status_code, content={"msg":msg})

@router.get('/{student_id}')
def get_student(student_id: str = Query(..., min_length=24, max_length=24)):
	"""
	View a student's information given their student id

	"""
	try:
		student = Students.find_one({'_id': ObjectId(student_id)})
		if student:
			del student['_id']
			del student["student_projects"]
			return student # automatically sets status code to 200.
		
		else:
			return JSONResponse(
			status_code=404,
			content={"msg":"Student does not exist"})
	
	except (bson.errors.InvalidId, TypeError) as e:
		print(e)
		return JSONResponse(
			status_code=400,
			content={"msg":"Invalid student id format - " + str(e)}) 

	except Exception as e:
		print(e)
		return JSONResponse(
			status_code=500,
			content={"msg":"DATABASE error"}) 

@router.put('/{student_id}')
def update_student(student_id: str, student: studentSchema):
	"""
	Update a student's information
	"""
	emptyCount = 0
	try:
		student_entry = Students.find_one({'_id': ObjectId(student_id)})

		if type(student_entry) != dict: 
			return JSONResponse(
			status_code=404,
			content={"msg":"Student does not exist"})

		if student.student_name == "string":
			student.student_name = student_entry["student_name"]
			emptyCount += 1

		if student.student_number  == "string":
			student.student_number = student_entry["student_number"]
			emptyCount += 1

		if student.student_profile_photo == "string":
			student.student_profile_photo = student_entry["student_profile_photo"]
			emptyCount += 1

		if student.student_projects != ["string"]:
			return JSONResponse(status_code=400,content={"msg":"The student projects field cannot be edited!"})

		if emptyCount == 3:
			return JSONResponse(status_code=400,content={"msg":"Must provide at least 1 field to update!"})

		if not isValidUrl(student.student_profile_photo):
			return JSONResponse(status_code=400, content={"msg":"Student profile photo uses an invalid image format!"})

		if hasLetters(student.student_number):
			return JSONResponse(status_code=400, content={"msg":"Invalid student number format!"})

		#update student info in projects accordingly
		projects = student_entry["student_projects"]
		for project_id in projects:
			myquery_project = { "_id": ObjectId(project_id), "team_members._id": student_id }
			newvalues_project = { "$set": { "team_members.$.student_name": student.student_name, 
			"team_members.$.student_number": student.student_number, 
			"team_members.$.student_profile_photo": student.student_profile_photo } } 
			Projects.update_many(myquery_project, newvalues_project)

		myquery = { "_id": ObjectId(student_id) }
		newvalues = { "$set": { "student_name": student.student_name, 
		"student_number": student.student_number,
		"student_profile_photo": student.student_profile_photo } }

		Students.update_one(myquery, newvalues)

		return JSONResponse(status_code=200,content={"msg":"Student Record Updated successfully!"})

	except (bson.errors.InvalidId, TypeError) as e:
		print(e)
		return JSONResponse(
			status_code=400,
			content={"msg":"Invalid student id format - " + str(e)}) 

	except Exception as e:
		print(e)
		return JSONResponse(
			status_code=500,
			content={"msg":"DATABASE error"}) 

@router.delete('/{student_id}')
def delete_student(student_id: str):
	"""
	Delete a student based on their student id
	"""

	try:
		student = Students.find_one({'_id': ObjectId(student_id)})

		if type(student) != dict: 
			return JSONResponse(
				status_code=404,
				content={"msg":"Student does not exist"})

		#get projects student is a member of and update each project accordingly
		#test for invalid objectIds
		projects = student["student_projects"]
		for project_id in projects:
			myquery = { '_id': project_id }
			newvalue = { "$pull": { "team_members": {"_id": student_id } } }
			Projects.update_many(myquery, newvalue)
		
		#delete student
		myquery = { "_id": ObjectId(student_id) }
		Students.delete_one(myquery)

		return JSONResponse(status_code=200,content={"msg":"Student Record deleted successfully"})

	except (bson.errors.InvalidId, TypeError) as e:
		print(e)
		return JSONResponse(
			status_code=400,
			content={"msg":"Invalid student id format - " + str(e)}) 

	except Exception as e:
		print(e)
		print("nooo")
		return JSONResponse(
			status_code=500,
			content={"msg":"DATABASE error"}) 