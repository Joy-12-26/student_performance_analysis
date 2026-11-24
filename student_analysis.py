"""
Student Performance Analysis System
-----------------------------------
Loads student records from a CSV file, calculates performance metrics,
identifies scholarship-eligible students and generates performance reports.

OOP concepts demonstrated:
  * Classes and objects      -> Student, AIUStudent, ScholarshipStudent, PerformanceAnalyzer
  * Encapsulation            -> private attributes (__name) exposed via properties/methods
  * Abstraction              -> Student is an abstract base class with abstract get_status()
  * Inheritance              -> AIUStudent(Student), ScholarshipStudent(AIUStudent)
  * Method overriding        -> get_status() and generate_report() in ScholarshipStudent
  * Polymorphism             -> one list of mixed objects, same method call in a loop
  * Flexible interfaces      -> average_of(*marks) with variable-length arguments
"""

import csv
from abc import ABC, abstractmethod


# ----------------------------------------------------------------------
# Task 2: Base class (encapsulation + abstraction)
# ----------------------------------------------------------------------
class Student(ABC):
    """Abstract base class holding a student's data and common behaviour."""

    SUBJECTS = ("Math", "English", "Science")

    def __init__(self, student_id, first_name, last_name, programme, marks):
        # Double underscore -> name-mangled (private) attributes.
        self.__student_id = student_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__programme = programme
        self.__marks = {}
        self.set_marks(marks)  # goes through validation

    # ---- controlled access (getters) ----
    @property
    def student_id(self):
        return self.__student_id

    @property
    def first_name(self):
        return self.__first_name

    @property
    def last_name(self):
        return self.__last_name

    @property
    def full_name(self):
        return f"{self.__first_name} {self.__last_name}"

    @property
    def programme(self):
        return self.__programme

    @programme.setter
    def programme(self, value):
        if not str(value).strip():
            raise ValueError("Programme cannot be empty.")
        self.__programme = str(value).strip()

    @property
    def marks(self):
        # Return a copy so outside code cannot change the private dict directly.
        return dict(self.__marks)

    # ---- controlled update (setter with validation) ----
    def set_marks(self, marks):
        for subject, mark in marks.items():
            if not 0 <= mark <= 100:
                raise ValueError(f"Mark for {subject} must be between 0 and 100, got {mark}.")
        self.__marks = dict(marks)

    # ---- Task 6: flexible interface (overloading equivalent) ----
    @staticmethod
    def average_of(*marks):
        """
        Average of any number of marks.
        Works with  average_of(75, 80, 70)  (three separate marks)
        and         average_of(*[60, 70, 80, 90])  (any number of marks).
        Validates that at least one mark is given and each is a number in 0-100.
        """
        if len(marks) == 0:
            raise ValueError("At least one mark is required.")
        for m in marks:
            if isinstance(m, bool) or not isinstance(m, (int, float)):
                raise TypeError(f"Marks must be numbers, got {m!r}.")
            if not 0 <= m <= 100:
                raise ValueError(f"Marks must be between 0 and 100, got {m}.")
        return sum(marks) / len(marks)

    def calculate_average(self):
        """Average of this student's own subject marks."""
        return self.average_of(*self.__marks.values())

    def determine_grade(self):
        avg = self.calculate_average()
        if avg >= 80:
            return "A"
        if avg >= 70:
            return "B"
        if avg >= 60:
            return "C"
        if avg >= 50:
            return "D"
        return "F"

    # ---- abstract method every subclass must implement ----
    @abstractmethod
    def get_status(self):
        """Return a short status string for the student."""

    def __str__(self):
        return f"{self.student_id} {self.full_name}"


# ----------------------------------------------------------------------
# Task 2 (cont.): Concrete subclass
# ----------------------------------------------------------------------
class AIUStudent(Student):
    """A regular AIU student. Implements the abstract get_status()."""

    def get_status(self):
        return f"Regular student - grade {self.determine_grade()}"

    # ---- Task 7: report generation ----
    def generate_report(self):
        lines = [
            "-" * 50,
            f"Student ID : {self.student_id}",
            f"Name       : {self.full_name}",
            f"Programme  : {self.programme}",
            "Marks      : " + ", ".join(f"{s}: {m}" for s, m in self.marks.items()),
            f"Average    : {self.calculate_average():.2f}",
            f"Grade      : {self.determine_grade()}",
            f"Status     : {self.get_status()}",
        ]
        lines.extend(self._extra_report_lines())
        return "\n".join(lines)

    def _extra_report_lines(self):
        """Hook for subclasses to add report lines."""
        return ["Scholarship: Not applicable"]


# ----------------------------------------------------------------------
# Task 4: Inheritance + method overriding
# ----------------------------------------------------------------------
class ScholarshipStudent(AIUStudent):
    """An AIUStudent who may qualify for a scholarship."""

    ELIGIBILITY_THRESHOLD = 85

    def __init__(self, student_id, first_name, last_name, programme, marks,
                 scholarship_amount=0):
        super().__init__(student_id, first_name, last_name, programme, marks)
        self.scholarship_amount = scholarship_amount

    def is_eligible(self):
        return self.calculate_average() >= self.ELIGIBILITY_THRESHOLD

    # Overridden: different behaviour from AIUStudent.get_status()
    def get_status(self):
        if self.is_eligible():
            return (f"Scholarship student - ELIGIBLE "
                    f"(award: ${self.scholarship_amount:,.2f})")
        return "Scholarship student - not eligible (average below 85)"

    # Overridden: replaces the parent's extra lines
    def _extra_report_lines(self):
        if self.is_eligible():
            return [f"Scholarship: ELIGIBLE - ${self.scholarship_amount:,.2f}"]
        return ["Scholarship: Not eligible (average below 85)"]


# ----------------------------------------------------------------------
# Task 3: Performance analyzer (composition)
# ----------------------------------------------------------------------
class PerformanceAnalyzer:
    """Analyses a collection of Student objects (holds references, no copies)."""

    def __init__(self, students):
        if not students:
            raise ValueError("PerformanceAnalyzer needs at least one student.")
        self.__students = students

    def highest_average(self):
        return max(self.__students, key=lambda s: s.calculate_average())

    def lowest_average(self):
        return min(self.__students, key=lambda s: s.calculate_average())

    def class_average(self):
        return sum(s.calculate_average() for s in self.__students) / len(self.__students)

    # ---- Task 7: class summary ----
    def class_summary(self):
        high, low = self.highest_average(), self.lowest_average()
        return "\n".join([
            "=" * 50,
            "CLASS PERFORMANCE SUMMARY",
            "=" * 50,
            f"Highest average : {high.calculate_average():.2f} ({high.full_name})",
            f"Lowest average  : {low.calculate_average():.2f} ({low.full_name})",
            f"Class average   : {self.class_average():.2f}",
        ])

    def generate_report(self):
        parts = ["=" * 50, "STUDENT PERFORMANCE REPORT", "=" * 50]
        parts.extend(s.generate_report() for s in self.__students)
        parts.append(self.class_summary())
        return "\n".join(parts)


# ----------------------------------------------------------------------
# Task 1: Load the dataset from CSV
# ----------------------------------------------------------------------
def scholarship_amount_for(average):
    """Award tiers used when a student qualifies (average >= 85)."""
    if average >= 90:
        return 5000.0
    if average >= 85:
        return 3000.0
    return 0.0


def load_students(csv_path):
    """
    Read students from a CSV file. Students with an average of 85+ become
    ScholarshipStudent objects; the rest become AIUStudent objects.
    """
    students = []
    with open(csv_path, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            marks = {subject: float(row[subject]) for subject in Student.SUBJECTS}
            average = Student.average_of(*marks.values())
            if average >= ScholarshipStudent.ELIGIBILITY_THRESHOLD:
                student = ScholarshipStudent(
                    row["StudentID"], row["FName"], row["LName"], row["Programme"],
                    marks, scholarship_amount=scholarship_amount_for(average))
            else:
                student = AIUStudent(
                    row["StudentID"], row["FName"], row["LName"], row["Programme"], marks)
            students.append(student)
    return students


# ----------------------------------------------------------------------
# Demonstration
# ----------------------------------------------------------------------
def main():
    students = load_students("students.csv")
    analyzer = PerformanceAnalyzer(students)

    # Task 7: full report
    print(analyzer.generate_report())

    # Task 4: inheritance - subclass reuses parent methods and adds its own
    print("\n" + "=" * 50)
    print("TASK 4: INHERITANCE DEMO")
    print("=" * 50)
    ruth = next(s for s in students if isinstance(s, ScholarshipStudent))
    print(f"{ruth.full_name} (inherited) average : {ruth.calculate_average():.2f}")
    print(f"{ruth.full_name} (inherited) grade   : {ruth.determine_grade()}")
    print(f"{ruth.full_name} (new) eligible      : {ruth.is_eligible()}")
    print(f"{ruth.full_name} (overridden) status : {ruth.get_status()}")

    # Task 5: polymorphism - one list, same call, different behaviour
    print("\n" + "=" * 50)
    print("TASK 5: POLYMORPHISM DEMO")
    print("=" * 50)
    for student in students:
        print(f"{student.full_name:<15} [{type(student).__name__}] -> {student.get_status()}")
    print("""
Explanation: AIUStudent and ScholarshipStudent are stored in the same list and
get_status() is called on each in one loop. Python picks the version that
belongs to the actual object (method overriding), so regular students report
their grade while scholarship students report their eligibility and award.""")

    # Task 6: flexible interface
    print("\n" + "=" * 50)
    print("TASK 6: FLEXIBLE METHOD INTERFACE")
    print("=" * 50)
    print("average_of(75, 80, 70)       =", round(Student.average_of(75, 80, 70), 2))
    print("average_of(60, 70, 80, 90)   =", round(Student.average_of(60, 70, 80, 90), 2))
    print("average_of(*[88, 92])        =", round(Student.average_of(*[88, 92]), 2))
    for bad_input in [(), (50, 120), (70, "A")]:
        try:
            Student.average_of(*bad_input)
        except (ValueError, TypeError) as error:
            print(f"average_of{bad_input} -> rejected: {error}")
    print("""
Explanation: Python has no true overloading (a later def replaces an earlier
one), so average_of(*marks) uses variable-length arguments. The caller can pass
three marks, two, or ten, and one method handles them all. It validates that
at least one mark is given and that every mark is a number between 0 and 100.""")


if __name__ == "__main__":
    main()
