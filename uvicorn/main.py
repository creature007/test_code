from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn

# Boshlang‘ich ma’lumotlar (lug‘at sifatida)
initial_students = {
    1: {"id": 1, "name": "Ali Akbarov", "email": "ali@example.com", "tests_taken": []},
    2: {"id": 2, "name": "Zarina Ismailova", "email": "zarina@example.com", "tests_taken": []}
}

initial_tests = {
    101: {"id": 101, "name": "Matematika Imtihoni", "max_score": 100},
    102: {"id": 102, "name": "Kimyo Sinovi", "max_score": 50}
}

initial_results = [
    {"student_id": 1, "test_id": 101, "score": 85},
    {"student_id": 2, "test_id": 101, "score": 92},
    {"student_id": 1, "test_id": 102, "score": 45}
]

# Ma’lumotlarni Pydantic obyektlariga aylantirish
students = {k: Student(**v) for k, v in initial_students.items()}
tests = {k: Test(**v) for k, v in initial_tests.items()}
results = [TestResult(**r) for r in initial_results]

# Talabalar sinov tizimi
app = FastAPI(title="Talabalar Sinov Tizimi")

# Pydantic modelar
class Student(BaseModel):
    id: int
    name: str
    email: str
    tests_taken: List[int] = []

class Test(BaseModel):
    id: int
    name: str
    max_score: int

class TestResult(BaseModel):
    student_id: int
    test_id: int
    score: int

# Talaba endpointlari
@app.post("/students/")
async def create_student(student: Student):
    if student.id in students:
        raise HTTPException(400, "Student ID kiritildi")
    students[student.id] = student
    return student

@app.get("/students/{student_id}")
async def get_student(student_id: int):
    if student_id not in students:
        raise HTTPException(404, "Student topilmadi")
    return students[student_id]

@app.get("/students/")
async def get_all_students():
    return list(students.values())

@app.delete("/students/{student_id}")
async def delete_student(student_id: int):
    if student_id not in students:
        raise HTTPException(404, "Student topilmadi")
    del students[student_id]
    return {"message": f"Student {student_id} ochirildi"}

# Sinov endpointlari
@app.post("/tests/")
async def create_test(test: Test):
    if test.id in tests:
        raise HTTPException(400, "Test ID yaratildi")
    tests[test.id] = test
    return test

@app.get("/tests/{test_id}")
async def get_test(test_id: int):
    if test_id not in tests:
        raise HTTPException(404, "Test topilmadi")
    return tests[test_id]

@app.get("/tests/")
async def get_all_tests():
    return list(tests.values())

# Natija endpointlari
@app.post("/results/")
async def submit_result(result: TestResult):
    if result.student_id not in students or result.test_id not in tests:
        raise HTTPException(404, "Student yoki Test topilmadi")
    if result.score > tests[result.test_id].max_score:
        raise HTTPException(400, "ball juda katta")
    results.append(result)
    students[result.student_id].tests_taken.append(result.test_id)
    return result

@app.get("/results/student/{student_id}")
async def get_student_results(student_id: int):
    if student_id not in students:
        raise HTTPException(404, "Student topilmadi")
    return [r for r in results if r.student_id == student_id]

@app.get("/results/test/{test_id}")
async def get_test_results(test_id: int):
    if test_id not in tests:
        raise HTTPException(404, "Test topimadi")
    return [r for r in results if r.test_id == test_id]

@app.get("/results/test/{test_id}/average")
async def get_test_average(test_id: int):
    if test_id not in tests:
        raise HTTPException(404, "Test topilmadi")
    scores = [r.score for r in results if r.test_id == test_id]
    return sum(scores) / len(scores) if scores else HTTPException(404, "natija chiqmadi")

@app.get("/results/test/{test_id}/eng katta")
async def get_test_highest(test_id: int):
    if test_id not in tests:
        raise HTTPException(404, "Test topilmadi")
    scores = [r.score for r in results if r.test_id == test_id]
    return max(scores) if scores else HTTPException(404, "natija chiqmad")

# Ilovani ishga tushirish (terminal orqali ishlatilsa, izohga olish mumkin)
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)   