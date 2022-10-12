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
from bson import json_util
from pymongo import MongoClient
from datetime import datetime
from typing import List, Optional
from fastapi import Query

from models.requests.projectModel import projectSchema
from models.objects.projectObject import Project

connection_url = "mongodb+srv://upmdev:cs127@cluster0.1ghnf.mongodb.net/Gallery_Projects?retryWrites=true&w=majority"
client = pymongo.MongoClient(connection_url)
Gallery = client["Project_Gallery"] #db
Projects = Gallery["Projects"] # table/collection created 
Students = Gallery["Students"] # table/collection created 

def isValidUrl(url: str):
	if url[-4:] == ".png" or url[-4:] == ".jpg":
		return True
	else:
		return False

def isValidYear(year: str):
	year = int(year)
	if year > 9999:
		return False
	else:
		return True

def hasLetters(inputString: str):
	return any(char.isalpha() for char in inputString)

def removeEmptyStrings(array_list: str):
	while("" in array_list): 
		array_list.remove("") 
	return array_list 

#### GET functions ####
@router.get('/get-all-projects')
def get_all_projects():
	"""
	Returns all projects
	"""
	project_list = []

	for project in Projects.find():
		project['_id'] = str(project['_id'])
		project['team_members'] = str(project['team_members'])
		project_list.append(project)
	
	projectDict = {
		"Projects": project_list
	}

	return projectDict

@router.post('/')
def insert_project(project: projectSchema):
	"""
	 Register a project in the database
	"""
	
	# initialize status code and msg to None
	status_code = None
	msg = None

	#project_screenshots_url = removeEmptyStrings(project_screenshots_url)
	#technologies_used = removeEmptyStrings(technologies_used)
	
	if not isValidUrl(project.project_banner_url):
		return JSONResponse(status_code=400, content={"msg":"Invalid banner image format!"})

	for url in project.project_screenshots_url:
		if not isValidUrl(url):
			return JSONResponse(status_code=400, content={"msg":"Invalid screenshot image format!"})

	if hasLetters(project.year_developed):
		return JSONResponse(status_code=400, content={"msg":"Year must be numeric!"})

	if not isValidYear(project.year_developed):
		return JSONResponse(status_code=400, content={"msg":"Sumobra na yung year"})

	#generate a unique random id
	project_id = ObjectId() 

	project_entry = []
	member_list = []
	try:
		#link members with their respective student ObjectId
		for member_id in project.team_members:
			student = Students.find_one({'_id': ObjectId(member_id)})
			if not student:
				return JSONResponse(status_code=404, content={"msg":"Invalid member id! Student does not exist"})
			else: #update student if exists
				Students.update_one({ "_id": ObjectId(member_id) }, { "$addToSet": { "student_projects": project_id } })
				student['_id'] = str(student['_id'])
				member_list.append(student)
		
		project_entry = { "_id": project_id, "project_name": project.project_name, "year_developed": project.year_developed,
		"project_course": project.project_course, "project_banner_url": project.project_banner_url,
		"project_screenshots_url": project.project_screenshots_url, "technologies_used": project.technologies_used,
		"team_members": member_list }
		
		Projects.insert_one(project_entry) #insert to db

		if project_entry:
			status_code = 201
			msg = 'Project successfully inserted!'

	except (bson.errors.InvalidId, TypeError) as e:
		print(e)
		return JSONResponse(
			status_code=400,
			content={"msg":"Invalid student id format - " + str(e)}) 

	except AttributeError as e:
		print(e)
		return JSONResponse(
			status_code=500,
			content={"msg":"da heck happened"}) 

	except Exception as e:
		status_code = 500
		msg = e

	return JSONResponse(status_code=status_code, content={"msg":msg})

@router.get('/{project_id}')
def get_project(project_id: str = Query(..., min_length=24, max_length=24)):
	"""
	View a project's information given the project id
	"""
	try:
		project = Projects.find_one({'_id': ObjectId(project_id)})
		if project:
			del project['_id']
			for member in project["team_members"]:
				del member['_id']
				del member['student_projects']
			
			return project # automatically sets status code to 200.
		
		else:
			return JSONResponse(
			status_code=404,
			content={"msg":"Project does not exist"})
	
	except (bson.errors.InvalidId, TypeError) as e:
		print(e)
		return JSONResponse(
			status_code=400,
			content={"msg":"Invalid project id format - " + str(e)}) 

	except Exception as e:
		print(e)
		return JSONResponse(
			status_code=500,
			content={"msg":"DATABASE error"}) 

@router.put('/{project_id}')
def update_project(project_id: str, project: projectSchema):
	"""
	Update a project's information
	"""
	count = 0
	try:
		project_entry = Projects.find_one({'_id': ObjectId(project_id)})

		if type(project_entry) != dict: 
			return JSONResponse(
			status_code=404,
			content={"msg":"Project does not exist"})
	
		myquery = { "_id": ObjectId(project_id) }

		if project.project_name != "string" or not project.project_name:
			Projects.update_one(myquery, { "$set": { "project_name": project.project_name } })
			count += 1

		if project.year_developed != "string" or not project.year_developed:
			Projects.update_one(myquery, { "$set": { "year_developed": project.year_developed } } )
			count += 1

		if project.project_course != "string" or not project.project_course:
			Projects.update_one(myquery, { "$set": { "project_course": project.project_course } })
			count += 1

		if project.project_banner_url != "string" or not  project.project_banner_url:
			Projects.update_one(myquery, { "$set": { "project_banner_url": project.project_banner_url } })
			count += 1

		if project.project_screenshots_url  != ["string"] or not project.project_screenshots_url:
			#remove brackets
			res = str(project.project_screenshots_url)[1:-1] 
			project_screenshots_url = res.replace("'","")
			Projects.update_one(myquery, {"$addToSet": { "project_screenshots_url": project_screenshots_url } })
			count += 1

		if project.technologies_used != ["string"] or not project.technologies_used:
			#remove brackets
			res = str(project.technologies_used)[1:-1]
			technologies_used = res.replace("'","")
			Projects.update_one(myquery, { "$addToSet": { "technologies_used": technologies_used } })
			count += 1

		if project.team_members != ["string"] or not project.team_members:
			member_list = {}
			#check if valid team member id
			for index in range(len(project.team_members)):
				member_id = project.team_members[index]
				student_entry = Students.find_one({'_id': ObjectId(member_id)})

				if type(student_entry) != dict: 
					return JSONResponse(
					status_code=404,
					content={"msg":"Invalid team member id! Student does not exist"})

				student_entry['_id'] = str(student_entry['_id'])
				member_list.update(student_entry)
				#update the project_list of student_entry
				Students.update_one({ "_id": ObjectId(member_id) }, { "$addToSet": { "student_projects": ObjectId(project_id) } })

			
			Projects.update_one(myquery, { "$addToSet": { "team_members": member_list } })
			count += 1
		

		if count == 0:
			return JSONResponse(status_code=400,content={"msg":"Must provide at least 1 field to update!"})

		return JSONResponse(status_code=200,content={"msg":"Project Record Updated successfully!"})

	except (bson.errors.InvalidId, TypeError) as e:
		print(e)
		return JSONResponse(
			status_code=400,
			content={"msg":"Invalid project id format - "+ str(e)}) 

	except Exception as e:
		print(e)
		return JSONResponse(
			status_code=500,
			content={"msg":"DATABASE error"}) 


@router.delete('/{project_id}')
def delete_project(project_id: str):
	"""
	Delete a project based on its id
	"""
	try:
		project = Projects.find_one({'_id': ObjectId(project_id)})

		if type(project) != dict: 
			return JSONResponse(
				status_code=404,
				content={"msg":"Project does not exist"})
	
		#get students that are part of the project and update each project accordingly
		#test for invalid objectIds
		students = project["team_members"]
		for student_object in students:
			student_id = student_object["_id"]
			myquery = { '_id': ObjectId(student_id) }
			newvalue = { "$pull": { "student_projects": ObjectId(project_id) } } 
			Students.update_many(myquery, newvalue)

		#delete project
		myquery = { "_id": ObjectId(project_id) }
		Projects.delete_one(myquery)

		return JSONResponse(status_code=200,content={"msg":"Project Record deleted successfully"})

	except (bson.errors.InvalidId, TypeError) as e:
		print(e)
		return JSONResponse(
			status_code=400,
			content={"msg":"Invalid project id format - " + str(e)}) 

	except Exception as e:
		print(e)
		print("nooo")
		return JSONResponse(
			status_code=500,
			content={"msg":"DATABASE error"}) 