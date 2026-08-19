import pandas as pd


def get_data():

    students = pd.read_json("students.json")
    marks = pd.read_json("marks.json")

    result = pd.merge(
        students,
        marks,
        on="Student_ID",
        how="inner"
    )

    return result


def get_topper():

    df = get_data()

    df["Percentage"] = df[
        ["Python", "Maths", "DBMS"]
    ].mean(axis=1)

    topper = df.loc[df["Percentage"].idxmax()]

    return topper


def department_analysis():

    df = get_data()

    df["Percentage"] = df[
        ["Python", "Maths", "DBMS"]
    ].mean(axis=1)

    result = df.groupby("Department")["Percentage"].mean()

    return result



def subject_analysis():

    df = get_data()

    subjects = ["Python", "Maths", "DBMS"]

    for subject in subjects:

        highest = df.loc[df[subject].idxmax()]
        lowest = df.loc[df[subject].idxmin()]

        print(f"\n===== {subject} =====")

        print(
            "Highest :",
            highest["Name"],
            "-",
            highest[subject]
        )

        print(
            "Lowest  :",
            lowest["Name"],
            "-",
            lowest[subject]
        )

        print(
            "Average :",
            round(df[subject].mean(), 2)
        )


def failed_students():

    df = get_data()

    df["Percentage"] = df[
        ["Python", "Maths", "DBMS"]
    ].mean(axis=1)

    failed = df[df["Percentage"] < 40]

    return failed



