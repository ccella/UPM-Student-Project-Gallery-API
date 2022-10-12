from bson import ObjectId

class Student:
  def __init__(
    self, _id, 
    student_name, student_number, student_profile_photo):
    self._id = ObjectId()
    self.student_name = student_name
    self.student_number = student_number
    self.student_profile_photo = student_profile_photo