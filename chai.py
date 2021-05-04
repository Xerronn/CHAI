from app import app
import requests
import pandas as pd
from datetime import datetime


token = "7301~YuF107qrayDlatOewpfCYgR7ixQ0qtUl6l92G7U77oonqekfik5RhSMrhhoHas1T"
headers = {"Authorization": "Bearer " + token}

#get the user ID
user = requests.get('https://canvas.instructure.com/api/v1/users/self/profile', headers=headers)
user_json = user.json()
userdf = pd.json_normalize(user_json)
userID = int(userdf['id'])

#get current courses
#filters out all the irrelevant courses
courses = requests.get('https://canvas.instructure.com/api/v1/courses?per_page=100&include[]=total_scores', headers=headers,)
coursedf = pd.json_normalize(courses.json())
coursedf = coursedf[list(set(["id", "name", "original_name", "course_code", "start_at", "created_at", "enrollment_term_id", "calendar.ics", "enrollments"]) & set(coursedf.columns))]
coursedf = coursedf[coursedf['name'].notna()]
coursedf = coursedf[coursedf['start_at'].notna()]
coursedf['start_at'] = coursedf['start_at'].apply(lambda x: datetime.strptime(x[:-1], "%Y-%m-%dT%H:%M:%S") if type(x) == str else x)
coursedf['name'] = coursedf['name'].apply(lambda x: x.replace(':', '-').replace('_', ' ').replace('&', 'and').split('-')[-1])
coursedf = coursedf.drop(coursedf[coursedf['start_at'] < datetime.strptime("2021-01-01T05:00:00", "%Y-%m-%dT%H:%M:%S")].index)
coursedf.reset_index(drop=True, inplace = True)

courseIDs = coursedf['id']

userCourseNames = coursedf['name']

#get all the grades in one string
grades = [str(x["enrollments"][0]["computed_current_score"]) + " in " + x["name"] for x in coursedf.iloc]
userGrades = ", ".join(grades)

#get all the upcoming assignments
userAssignmentsList = []
for i in courseIDs:
    upcoming = requests.get(f'https://canvas.instructure.com/api/v1/courses/{i}/assignments?bucket=upcoming', headers=headers)
    userAssignmentsList.append(pd.json_normalize(upcoming.json()))    
all_upcoming_assignments = pd.concat(userAssignmentsList)
    
userAssignments = ", ".join(list(all_upcoming_assignments['name'])).replace(':', '').replace('&', 'and').replace('-', ' ').replace('/', '')


