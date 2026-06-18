from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pytest
from fastapi.testclient import TestClient

app = FastAPI()

class Student(BaseModel):
    id: int
    name: str
    grade: int

db = []

@app.post("/students/", response_model=Student)
def create_student(student: Student):
    for s in db:
        if s.id == student.id:
            raise HTTPException(status_code=400, detail="Student already exists")
    db.append(student)
    return student

@app.get("/students/", response_model=List[Student])
def get_students():
    return db

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    for s in db:
        if s.id == student_id:
            return s
    raise HTTPException(status_code=404, detail="Student not found")

# --- Tests ---

client = TestClient(app)

def test_create_student():
    response = client.post("/students/", json={"id": 1, "name": "Alice", "grade": 10})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice", "grade": 10}

def test_get_students():
    response = client.get("/students/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_student_not_found():
    response = client.get("/students/999")
    assert response.status_code == 404

def test_duplicate_student():
    client.post("/students/", json={"id": 2, "name": "Bob", "grade": 11})
    response = client.post("/students/", json={"id": 2, "name": "Bob", "grade": 11})
    assert response.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__])