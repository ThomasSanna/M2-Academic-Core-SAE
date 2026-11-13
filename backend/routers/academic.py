"""Années, semestres, filières, matières, volumes horaires."""
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field, model_validator

from db import query, query_one, transaction, update_row
from security import get_current_user, require_staff

router = APIRouter(tags=["Structure pédagogique"])
NOT_FOUND = status.HTTP_404_NOT_FOUND
UNPROCESSABLE = status.HTTP_422_UNPROCESSABLE_ENTITY


def _or_404(row: dict | None, what: str) -> dict:
    if not row:
        raise HTTPException(NOT_FOUND, f"{what} introuvable")
    return row


def _check_dates(start: date | None, end: date | None) -> None:
    if start and end and end <= start:
        raise HTTPException(UNPROCESSABLE, "end_date doit être postérieure à start_date")


# ---------------------------------------------------------------------
# Années académiques
# ---------------------------------------------------------------------
class YearIn(BaseModel):
    label: str = Field(min_length=1, max_length=50)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def _dates(self):
        _check_dates(self.start_date, self.end_date)
        return self


class YearUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=50)
    start_date: date | None = None
    end_date: date | None = None


@router.get("/academic-years")
def list_years(_: dict = Depends(get_current_user)):
    return query("SELECT * FROM academic_years ORDER BY start_date DESC")


@router.post("/academic-years", status_code=status.HTTP_201_CREATED)
def create_year(body: YearIn, _: dict = Depends(require_staff)):
    return query_one(
        "INSERT INTO academic_years (label, start_date, end_date) VALUES (%s, %s, %s) RETURNING *",
        (body.label, body.start_date, body.end_date),
    )


@router.get("/academic-years/{year_id}")
def get_year(year_id: int, _: dict = Depends(get_current_user)):
    return _or_404(query_one("SELECT * FROM academic_years WHERE id = %s", (year_id,)), "Année académique")


@router.put("/academic-years/{year_id}")
def update_year(year_id: int, body: YearUpdate, _: dict = Depends(require_staff)):
    with transaction() as conn:
        current = _or_404(
            query_one("SELECT * FROM academic_years WHERE id = %s", (year_id,), conn), "Année académique"
        )
        data = body.model_dump(exclude_unset=True, exclude_none=True)
        _check_dates(data.get("start_date", current["start_date"]), data.get("end_date", current["end_date"]))
        return update_row("academic_years", year_id, data, conn)


# ---------------------------------------------------------------------
# Semestres
# ---------------------------------------------------------------------
class SemesterIn(BaseModel):
    label: str = Field(min_length=1, max_length=50)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def _dates(self):
        _check_dates(self.start_date, self.end_date)
        return self


class SemesterUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=50)
    start_date: date | None = None
    end_date: date | None = None


def _check_within_year(conn, year_id: int, start: date, end: date) -> None:
    year = _or_404(query_one("SELECT * FROM academic_years WHERE id = %s", (year_id,), conn), "Année académique")
    if start < year["start_date"] or end > year["end_date"]:
        raise HTTPException(UNPROCESSABLE, "Le semestre doit être inclus dans l'année académique")


@router.get("/academic-years/{year_id}/semesters")
def list_semesters(year_id: int, _: dict = Depends(get_current_user)):
    _or_404(query_one("SELECT id FROM academic_years WHERE id = %s", (year_id,)), "Année académique")
    return query("SELECT * FROM semesters WHERE academic_year_id = %s ORDER BY start_date", (year_id,))


@router.post("/academic-years/{year_id}/semesters", status_code=status.HTTP_201_CREATED)
def create_semester(year_id: int, body: SemesterIn, _: dict = Depends(require_staff)):
    with transaction() as conn:
        _check_within_year(conn, year_id, body.start_date, body.end_date)
        return query_one(
            """INSERT INTO semesters (label, academic_year_id, start_date, end_date)
               VALUES (%s, %s, %s, %s) RETURNING *""",
            (body.label, year_id, body.start_date, body.end_date),
            conn,
        )


@router.put("/semesters/{semester_id}")
def update_semester(semester_id: int, body: SemesterUpdate, _: dict = Depends(require_staff)):
    with transaction() as conn:
        current = _or_404(query_one("SELECT * FROM semesters WHERE id = %s", (semester_id,), conn), "Semestre")
        data = body.model_dump(exclude_unset=True, exclude_none=True)
        start = data.get("start_date", current["start_date"])
        end = data.get("end_date", current["end_date"])
        _check_dates(start, end)
        _check_within_year(conn, current["academic_year_id"], start, end)
        return update_row("semesters", semester_id, data, conn)


@router.delete("/semesters/{semester_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_semester(semester_id: int, _: dict = Depends(require_staff)):
    # 409 géré globalement si des matières référencent encore ce semestre (ON DELETE RESTRICT)
    _or_404(query_one("DELETE FROM semesters WHERE id = %s RETURNING id", (semester_id,)), "Semestre")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------
# Filières
# ---------------------------------------------------------------------
class ProgramIn(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    level: str | None = Field(default=None, max_length=50)


class ProgramUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    level: str | None = Field(default=None, max_length=50)


@router.get("/programs")
def list_programs(_: dict = Depends(get_current_user)):
    return query("SELECT * FROM programs ORDER BY name")


@router.post("/programs", status_code=status.HTTP_201_CREATED)
def create_program(body: ProgramIn, _: dict = Depends(require_staff)):
    return query_one(
        "INSERT INTO programs (name, level) VALUES (%s, %s) RETURNING *", (body.name, body.level)
    )


@router.get("/programs/{program_id}")
def get_program(program_id: int, _: dict = Depends(get_current_user)):
    return _or_404(query_one("SELECT * FROM programs WHERE id = %s", (program_id,)), "Filière")


@router.put("/programs/{program_id}")
def update_program(program_id: int, body: ProgramUpdate, _: dict = Depends(require_staff)):
    data = body.model_dump(exclude_unset=True)
    if data.get("name") is None:
        data.pop("name", None)
    return _or_404(update_row("programs", program_id, data), "Filière")


# ---------------------------------------------------------------------
# Matières
# ---------------------------------------------------------------------
class SubjectIn(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=200)
    semester_id: int


class SubjectUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=50)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    semester_id: int | None = None


@router.get("/programs/{program_id}/subjects")
def list_subjects(
    program_id: int,
    semester_id: int | None = Query(None),
    _: dict = Depends(get_current_user),
):
    _or_404(query_one("SELECT id FROM programs WHERE id = %s", (program_id,)), "Filière")
    sql = "SELECT * FROM subjects WHERE program_id = %s"
    params: list = [program_id]
    if semester_id is not None:
        sql += " AND semester_id = %s"
        params.append(semester_id)
    return query(sql + " ORDER BY code", params)


@router.post("/programs/{program_id}/subjects", status_code=status.HTTP_201_CREATED)
def create_subject(program_id: int, body: SubjectIn, _: dict = Depends(require_staff)):
    with transaction() as conn:
        _or_404(query_one("SELECT id FROM programs WHERE id = %s", (program_id,), conn), "Filière")
        _or_404(query_one("SELECT id FROM semesters WHERE id = %s", (body.semester_id,), conn), "Semestre")
        return query_one(
            """INSERT INTO subjects (code, title, program_id, semester_id)
               VALUES (%s, %s, %s, %s) RETURNING *""",
            (body.code, body.title, program_id, body.semester_id),
            conn,
        )


@router.get("/subjects/{subject_id}")
def get_subject(subject_id: int, _: dict = Depends(get_current_user)):
    return _or_404(query_one("SELECT * FROM subjects WHERE id = %s", (subject_id,)), "Matière")


@router.put("/subjects/{subject_id}")
def update_subject(subject_id: int, body: SubjectUpdate, _: dict = Depends(require_staff)):
    data = body.model_dump(exclude_unset=True, exclude_none=True)
    with transaction() as conn:
        if "semester_id" in data:
            _or_404(query_one("SELECT id FROM semesters WHERE id = %s", (data["semester_id"],), conn), "Semestre")
        return _or_404(update_row("subjects", subject_id, data, conn), "Matière")


@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, _: dict = Depends(require_staff)):
    _or_404(query_one("DELETE FROM subjects WHERE id = %s RETURNING id", (subject_id,)), "Matière")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------
# Volumes horaires
# ---------------------------------------------------------------------
VOLUME_SELECT = """
    SELECT v.id, v.subject_id, v.session_type_id, v.planned_hours,
           t.code AS session_type_code, t.label AS session_type_label
    FROM subject_volumes v JOIN session_types t ON t.id = v.session_type_id
"""


class VolumeIn(BaseModel):
    session_type_id: int
    planned_hours: Decimal = Field(ge=0, max_digits=6, decimal_places=2)


class VolumeUpdate(BaseModel):
    planned_hours: Decimal = Field(ge=0, max_digits=6, decimal_places=2)


@router.get("/session-types")
def list_session_types(_: dict = Depends(get_current_user)):
    return query("SELECT * FROM session_types ORDER BY id")


@router.get("/subjects/{subject_id}/volumes")
def list_volumes(subject_id: int, _: dict = Depends(get_current_user)):
    _or_404(query_one("SELECT id FROM subjects WHERE id = %s", (subject_id,)), "Matière")
    return query(VOLUME_SELECT + " WHERE v.subject_id = %s ORDER BY t.id", (subject_id,))


@router.post("/subjects/{subject_id}/volumes", status_code=status.HTTP_201_CREATED)
def create_volume(subject_id: int, body: VolumeIn, _: dict = Depends(require_staff)):
    with transaction() as conn:
        _or_404(query_one("SELECT id FROM subjects WHERE id = %s", (subject_id,), conn), "Matière")
        _or_404(
            query_one("SELECT id FROM session_types WHERE id = %s", (body.session_type_id,), conn),
            "Type de séance",
        )
        row = query_one(
            """INSERT INTO subject_volumes (subject_id, session_type_id, planned_hours)
               VALUES (%s, %s, %s) RETURNING id""",
            (subject_id, body.session_type_id, body.planned_hours),
            conn,
        )
        return query_one(VOLUME_SELECT + " WHERE v.id = %s", (row["id"],), conn)


@router.put("/subject-volumes/{volume_id}")
def update_volume(volume_id: int, body: VolumeUpdate, _: dict = Depends(require_staff)):
    with transaction() as conn:
        _or_404(
            query_one(
                "UPDATE subject_volumes SET planned_hours = %s WHERE id = %s RETURNING id",
                (body.planned_hours, volume_id),
                conn,
            ),
            "Volume horaire",
        )
        return query_one(VOLUME_SELECT + " WHERE v.id = %s", (volume_id,), conn)


@router.delete("/subject-volumes/{volume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_volume(volume_id: int, _: dict = Depends(require_staff)):
    _or_404(query_one("DELETE FROM subject_volumes WHERE id = %s RETURNING id", (volume_id,)), "Volume horaire")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
