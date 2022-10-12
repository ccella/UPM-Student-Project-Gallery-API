from bson import ObjectId

class Project:
  def __init__(
    self, _id, 
    project_name, year_developed, project_course,
    project_banner_url, project_screenshots_url, 
	technologies_used, team_members):
    self._id = ObjectId()
    self.project_name = project_name
    self.year_developed = year_developed
    self.project_course = project_course
    self.project_banner_url = project_banner_url
    self.project_screenshots_url = project_screenshots_url
    self.technologies_used = technologies_used
    self.team_members = team_members