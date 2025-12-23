from typing import List, Dict, Optional

class Course:
    GRADE_VALUES = {
        "A": 4.0, "B+": 3.5, "B": 3.0, "C+": 2.5, "C": 2.0,
        "D+": 1.5, "D": 1.0, "F": 0.0,
        "I": None, "S": None, "U": None, "P": None, "NP": None, "N": None
    }

    def __init__(self, name: str, credits: float, grade: str):
        self.name = name
        self.credits = credits
        self.grade = grade
        self.points = self.GRADE_VALUES.get(grade)

    def to_dict(self):
        return {
            "name": self.name,
            "credits": self.credits,
            "grade": self.grade
        }

class Semester:
    def __init__(self, name: str, year: str, courses: List[Course] = None):
        self.name = name
        self.year = year
        self.courses = courses if courses else []

    def add_course(self, course: Course):
        self.courses.append(course)

    def calculate_stats(self):
        total_points = 0.0
        total_credits = 0.0
        
        for course in self.courses:
            if course.points is not None:
                total_points += course.points * course.credits
                total_credits += course.credits
        
        gpa = (total_points / total_credits) if total_credits > 0 else 0.0
        return gpa, total_points, total_credits

    def to_dict(self):
        gpa, points, credits = self.calculate_stats()
        return {
            "name": self.name,
            "points": points,
            "credits": credits,
            "gpa": gpa,
            "courses": [c.to_dict() for c in self.courses]
        }

    @classmethod
    def from_dict(cls, data: dict, year: str):
        semester = cls(data['name'], year)
        for c_data in data.get('courses', []):
            semester.add_course(Course(c_data['name'], float(c_data['credits']), c_data['grade']))
        return semester

class GradeManager:
    def __init__(self):
        # Structure: { "Year 1": [SemesterObj, ...], ... }
        self.semesters_by_year: Dict[str, List[Semester]] = {}

    def add_semester(self, semester: Semester):
        if semester.year not in self.semesters_by_year:
            self.semesters_by_year[semester.year] = []
        self.semesters_by_year[semester.year].append(semester)

    def update_semester(self, new_semester: Semester, old_year: str, index: int):
        # If year changed, remove from old year list
        if old_year != new_semester.year:
            self.delete_semester(old_year, index)
            self.add_semester(new_semester)
        else:
            # Update in place
            if old_year in self.semesters_by_year and 0 <= index < len(self.semesters_by_year[old_year]):
                self.semesters_by_year[old_year][index] = new_semester

    def delete_semester(self, year: str, index: int):
        if year in self.semesters_by_year and 0 <= index < len(self.semesters_by_year[year]):
            del self.semesters_by_year[year][index]
            if not self.semesters_by_year[year]:
                del self.semesters_by_year[year]

    def get_cumulative_gpa(self):
        cum_points = 0.0
        cum_credits = 0.0
        for year, semesters in self.semesters_by_year.items():
            for s in semesters:
                _, points, credits = s.calculate_stats()
                cum_points += points
                cum_credits += credits
        return (cum_points / cum_credits) if cum_credits > 0 else 0.0

    def load_data(self, data: dict):
        self.semesters_by_year = {}
        for year, semesters_data in data.items():
            self.semesters_by_year[year] = []
            for s_data in semesters_data:
                self.semesters_by_year[year].append(Semester.from_dict(s_data, year))

    def get_data_as_dict(self):
        data = {}
        for year, semesters in self.semesters_by_year.items():
            data[year] = [s.to_dict() for s in semesters]
        return data
