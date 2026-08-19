from pathlib import Path
import json
import numpy as np
import pandas as pd
import string
import random

from analysis import get_data
from analysis import get_data, get_topper
from analysis import get_data, get_topper, department_analysis
from analysis import (get_data,get_topper,department_analysis,subject_analysis)
from analysis import (get_data,get_topper,department_analysis,subject_analysis,failed_students)



def valid_marks(marks):
    return 0 <= marks <= 100


class StudentManagement:

    students_database = "students.json"
    marks_database = "marks.json"

    students = []
    marks = []

    # Load student data
    try:
        if Path(students_database).exists():
            with open(students_database, "r") as fs:
                students = json.loads(fs.read())

    except Exception as err:
        print(f"An error occurred: {err}")

    # Load marks data
    try:
        if Path(marks_database).exists():
            with open(marks_database, "r") as fs:
                marks = json.loads(fs.read())

    except Exception as err:
        print(f"An error occurred: {err}")

    # Save student data
    @classmethod
    def __update_students(cls):
        with open(cls.students_database, "w") as fs:
            fs.write(json.dumps(cls.students, indent=4))

    # Save marks data
    @classmethod
    def __update_marks(cls):
        with open(cls.marks_database, "w") as fs:
            fs.write(json.dumps(cls.marks, indent=4))

    # Add student
    def add_student(self):
     student_id = int(input("Enter Student ID: "))

    # Check duplicate Student ID
     existing = [
       i for i in StudentManagement.students
        if i["Student_ID"] == student_id
    ]

     if existing:
        print("Student ID already exists!")
        return

     info = {
        "Student_ID": student_id,
        "Name": input("Enter Name: "),
        "Department": input("Enter Department: ")
    }

     StudentManagement.students.append(info)
     StudentManagement.__update_students()

     print("Student added successfully!")


    # View students
    def view_students(self):

        if not StudentManagement.students:
            print("No students found.")
            return

        for student in StudentManagement.students:
            print("\n-------------------------")
            print(f"Student ID : {student['Student_ID']}")
            print(f"Name       : {student['Name']}")
            print(f"Department : {student['Department']}")


    #Search Student
    def search_student(self):
    
        student_id = int(input("Enter Student ID: "))
    
        user = [
              i for i in StudentManagement.students
              if i["Student_ID"] == student_id
        ]
    
        if user:
              print("\n===== STUDENT DETAILS =====")
              print("Student ID :", user[0]["Student_ID"])
              print("Name       :", user[0]["Name"])
              print("Department :", user[0]["Department"])
    
        else:
              print("Student not found!")


    #Update student
    def update_student(self):

     
      student_id = int(input("Enter Student ID: "))
     

      user = [
        i for i in StudentManagement.students
        if i["Student_ID"] == student_id
    ]

      if not user:
        print("Student not found!")
        return

      student = user[0]

      name = input("Enter new name (press Enter to skip): ")
      department = input("Enter new department (press Enter to skip): ")

      if name != "":
       student["Name"] = name

      if department != "":
        student["Department"] = department

      StudentManagement.__update_students()

    print("Student details updated successfully!")


    #Delete student
    def delete_student(self):

     
     student_id = int(input("Enter Student ID: "))
     

     user = [
        i for i in StudentManagement.students
        if i["Student_ID"] == student_id
    ]

     if not user:
        print("Student not found!")
        return

     confirm = input("Are you sure? Press Y/N: ")

     if confirm.lower() == "y":

        StudentManagement.students.remove(user[0])

        StudentManagement.__update_students()

        print("Student deleted successfully!")

     else:
        print("Deletion cancelled.")


    
    

    # Add marks
    def add_marks(self):

     student_id = int(input("Enter Student ID: "))

     user = [
        i for i in StudentManagement.students
        if i["Student_ID"] == student_id
    ]

     if not user:
        print("Student does not exist!")
        return

     python = int(input("Enter Python marks: "))
     maths = int(input("Enter Maths marks: "))
     dbms = int(input("Enter DBMS marks: "))

     if not valid_marks(python):
        print("Python marks must be between 0 and 100.")
        return

     if not valid_marks(maths):
      print("Maths marks must be between 0 and 100.")
      return

     if not valid_marks(dbms):
        print("DBMS marks must be between 0 and 100.")
        return

     info = {
        "Student_ID": student_id,
        "Python": python,
        "Maths": maths,
        "DBMS": dbms
    }

     StudentManagement.marks.append(info)
     StudentManagement.__update_marks()

    print("Marks added successfully!")


    # View marks
    def view_marks(self):

        if not StudentManagement.marks:
            print("No marks found.")
            return

        for mark in StudentManagement.marks:
            print("\n-------------------------")
            print(f"Student ID : {mark['Student_ID']}")
            print(f"Python     : {mark['Python']}")
            print(f"Maths      : {mark['Maths']}")
            print(f"DBMS       : {mark['DBMS']}")


    #Update marks
    def update_marks(self):

     student_id = int(input("Enter Student ID: "))

     user = [
        i for i in StudentManagement.marks
        if i["Student_ID"] == student_id
    ]

     if not user:
        print("Marks not found!")
        return

     mark = user[0]

     python = input("Enter new Python marks (Enter to skip): ")
     maths = input("Enter new Maths marks (Enter to skip): ")
     dbms = input("Enter new DBMS marks (Enter to skip): ")

     if python != "":
        mark["Python"] = int(python)

     if maths != "":
        mark["Maths"] = int(maths)

     if dbms != "":
        mark["DBMS"] = int(dbms)

     StudentManagement.__update_marks()

    print("Marks updated successfully!")


    # Generate result
    def generate_result(self):

        student_id = int(input("Enter Student ID: "))

        student = [
            i for i in StudentManagement.students
            if i["Student_ID"] == student_id
        ]

        mark = [
            i for i in StudentManagement.marks
            if i["Student_ID"] == student_id
        ]

        if not student:
            print("Student not found.")
            return

        if not mark:
            print("Marks not found.")
            return

        mark = mark[0]
        student = student[0]

        marks_array = np.array([
            mark["Python"],
            mark["Maths"],
            mark["DBMS"]
        ])


    


        total = np.sum(marks_array)
        percentage = np.mean(marks_array)

        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B"
        elif percentage >= 60:
            grade = "C"
        elif percentage >= 50:
            grade = "D"
        else:
            grade = "F"

        print("\n================================")
        print("          STUDENT RESULT")
        print("================================")
        print(f"Student ID : {student['Student_ID']}")
        print(f"Name       : {student['Name']}")
        print(f"Department : {student['Department']}")
        print("--------------------------------")
        print(f"Python     : {mark['Python']}")
        print(f"Maths      : {mark['Maths']}")
        print(f"DBMS       : {mark['DBMS']}")
        print("--------------------------------")
        print(f"Total      : {total}/300")
        print(f"Percentage : {percentage:.2f}%")
        print(f"Grade      : {grade}")
        print("================================")


student_system = StudentManagement()

student_system = StudentManagement()

student_system = StudentManagement()

while True:

    print("\n========================================")
    print("       STUDENT MANAGEMENT SYSTEM")
    print("========================================")

    print("\n----- STUDENT MANAGEMENT -----")
    print("Press 1 to add student")
    print("Press 2 to view students")
    print("Press 3 to search student")
    print("Press 4 to update student")
    print("Press 5 to delete student")

    print("\n----- MARKS MANAGEMENT -----")
    print("Press 6 to add marks")
    print("Press 7 to view marks")
    print("Press 8 to update marks")

    print("\n----- ANALYSIS -----")
    print("Press 9 to view complete data")
    print("Press 10 to show topper")
    print("Press 11 to show failed students")
    print("Press 12 for subject analysis")
    print("Press 13 for department analysis")

    print("\n----- RESULT -----")
    print("Press 14 to generate result")

    print("\nPress 0 to exit")

    print("========================================")

  
    choice = int(input("Enter your choice: "))
   



    if choice == 1:
        student_system.add_student()

    elif choice == 2:
        student_system.view_students()

    elif choice == 3:
        student_system.search_student()

    elif choice == 4:
        student_system.update_student()

    elif choice == 5:
        student_system.delete_student()

    elif choice == 6:
        student_system.add_marks()

    elif choice == 7:
        student_system.view_marks()

    elif choice == 8:
        student_system.update_marks()

    elif choice == 9:

        df = get_data()

        if df.empty:
            print("No complete data available!")

        else:
            print("\n========== COMPLETE STUDENT DATA ==========")
            print(df)

    elif choice == 10:

        topper = get_topper()

        if topper is None:
            print("No student data available!")

        else:
            print("\n========== TOPPER ==========")
            print("Student ID :", topper["Student_ID"])
            print("Name       :", topper["Name"])
            print("Department :", topper["Department"])
            print("Percentage :", round(topper["Percentage"], 2))

    elif choice == 11:

        failed = failed_students()

        if failed.empty:
            print("\nNo failed students!")

        else:
            print("\n========== FAILED STUDENTS ==========")
            print(
                failed[
                    [
                        "Student_ID",
                        "Name",
                        "Department",
                        "Percentage"
                    ]
                ]
            )

    elif choice == 12:
        subject_analysis()

    elif choice == 13:

        result = department_analysis()

        if result.empty:
            print("No data available for department analysis!")

        else:
            print("\n========== DEPARTMENT ANALYSIS ==========")
            print(result)

    elif choice == 14:
        student_system.generate_result()

    elif choice == 0:
        print("\nThank you for using Student Management System!")
        print("Program closed successfully.")
        break

    else:
        print("Invalid choice!")
        print("Please choose a number between 0 and 14.")
