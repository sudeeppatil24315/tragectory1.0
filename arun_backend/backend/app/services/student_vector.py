def build_vector(grades, attendance):
    if not grades:
        avg_marks = 0
    else:
        avg_marks = sum(grades)/len(grades)
    return {
        "academics": avg_marks,
        "attendance": attendance
    }
