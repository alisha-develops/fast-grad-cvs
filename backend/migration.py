import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
import base64

from backend.database import SessionLocal, Base, engine
from backend.student_model import Student

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set in .env")

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

_preview_cache = {
    "ready": False,
    "student_ids": [],
    "docs_by_id": {}
}


def get_value(doc, key):
    value = doc.get(key)
    if value is None:
        return None
    return str(value).strip()


def upload_photo_if_present(doc, full_name, dry_run):
    photo_data = doc.get("photoUrl")

    if not photo_data:
        return None

    if not photo_data.startswith("data:image"):
        return photo_data

    if dry_run:
        return "[would upload photo]"

    try:
        header, encoded = photo_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)

        result = cloudinary.uploader.upload(
            image_bytes,
            folder="fast-nu-grad-cvs-migrated",
            resource_type="image"
        )

        return result["secure_url"]

    except Exception as e:
        print("  Photo upload FAILED for " + full_name + ": " + str(e))
        return None


def normalize_timestamp(ts):
    if ts is None:
        return None
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts


def build_student_object(newest_doc, student_id, full_name, v1_submitted_at, photo_url):
    return Student(
        full_name=full_name,
        student_id=student_id,
        email=get_value(newest_doc, "email"),
        phone=get_value(newest_doc, "phone"),
        cgpa=get_value(newest_doc, "cgpa"),
        degree_program=get_value(newest_doc, "degreeProgram"),
        linkedin=get_value(newest_doc, "linkedin"),
        portfolio=get_value(newest_doc, "portfolio"),
        objective=get_value(newest_doc, "objective"),
        education=get_value(newest_doc, "education"),
        fyp_title=get_value(newest_doc, "fypTitle"),
        fyp_desc=get_value(newest_doc, "fypDesc"),
        fyp_supervisor=get_value(newest_doc, "fypSupervisor"),
        elective_courses=get_value(newest_doc, "electiveCourses"),
        areas_of_interest=get_value(newest_doc, "areasOfInterest"),
        technical_skills=get_value(newest_doc, "technicalSkills"),
        personal_skills=get_value(newest_doc, "personalSkills"),
        certifications=get_value(newest_doc, "certifications"),
        honors=get_value(newest_doc, "honors"),
        internship=get_value(newest_doc, "internship"),
        leadership=get_value(newest_doc, "leadership"),
        photo_url=photo_url,
        is_deleted=False,
        source_submitted_at=v1_submitted_at
    )


def sync_preview_stream():
    """
    Scans v1, figures out who's new or has a newer resubmission, and caches
    that exact list (with their mongo doc already attached) in memory.
    Never writes to postgres. Opens a postgres connection just long enough
    to read existing students, then closes it before the (potentially slow)
    mongo work starts, so nothing sits idle.
    """
    global _preview_cache

    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client["fastnu_cv_tool"]
    submissions_collection = mongo_db["submissions"]

    yield "checking existing students in postgres..."

    db = SessionLocal()
    all_existing = db.query(Student).all()
    existing_by_id = {}
    for student in all_existing:
        existing_by_id[student.student_id] = student
    db.close()

    print("found " + str(len(all_existing)) + " existing students in postgres")
    yield "found " + str(len(all_existing)) + " existing students in postgres"

    all_student_ids_cursor = submissions_collection.distinct("studentId")

    new_count = 0
    updated_count = 0
    unchanged_count = 0

    new_students = []
    updated_students = []
    pending_ids = []
    pending_docs = {}

    checked_count = 0

    for student_id in all_student_ids_cursor:
        if not student_id:
            continue

        checked_count = checked_count + 1
        if checked_count % 25 == 0:
            print("checking... (" + str(checked_count) + " students checked)")
            yield "checking... (" + str(checked_count) + " students checked)"

        newest_doc_list = list(
            submissions_collection.find({"studentId": student_id})
            .sort("submittedAt", -1)
            .limit(1)
        )

        if not newest_doc_list:
            continue

        newest_doc = newest_doc_list[0]
        full_name = get_value(newest_doc, "fullName")

        if not full_name:
            continue

        v1_submitted_at = normalize_timestamp(newest_doc.get("submittedAt"))
        existing = existing_by_id.get(student_id)

        if existing and existing.source_submitted_at is not None:
            existing_ts = normalize_timestamp(existing.source_submitted_at)

            if v1_submitted_at and v1_submitted_at <= existing_ts:
                unchanged_count = unchanged_count + 1
                continue

        if existing:
            yield "UPDATING: " + full_name + " (" + student_id + ")"
            updated_count = updated_count + 1
            updated_students.append(full_name + " (" + student_id + ")")
        else:
            yield "NEW FROM V1: " + full_name + " (" + student_id + ")"
            new_count = new_count + 1
            new_students.append(full_name + " (" + student_id + ")")

        pending_ids.append(student_id)
        pending_docs[student_id] = newest_doc

    mongo_client.close()

    _preview_cache["ready"] = True
    _preview_cache["student_ids"] = pending_ids
    _preview_cache["docs_by_id"] = pending_docs

    yield "=== Sync Summary ==="
    yield "New from v1: " + str(new_count)
    yield "Updated (newer version found): " + str(updated_count)
    yield "Unchanged (already up to date): " + str(unchanged_count)

    summary = {
        "new_count": new_count,
        "updated_count": updated_count,
        "unchanged_count": unchanged_count,
        "error_count": 0,
        "new_students": new_students,
        "updated_students": updated_students
    }

    yield "SUMMARY:" + json.dumps(summary)


def sync_confirm_stream():
    """
    Replays whatever the last preview found - no rescanning mongo, no
    recomputing who's new/updated. Opens a fresh, short-lived postgres
    session per student so a long run never holds one connection idle
    long enough for it to get dropped.
    """
    global _preview_cache

    if not _preview_cache["ready"] or len(_preview_cache["student_ids"]) == 0:
        yield "ERROR: no preview data available. Run a preview first."
        yield "SUMMARY:" + json.dumps({"new_count": 0, "updated_count": 0, "error_count": 1})
        return

    student_ids = _preview_cache["student_ids"]
    docs_by_id = _preview_cache["docs_by_id"]

    new_count = 0
    updated_count = 0
    error_count = 0

    for student_id in student_ids:
        newest_doc = docs_by_id.get(student_id)
        if not newest_doc:
            continue

        full_name = get_value(newest_doc, "fullName")
        if not full_name:
            continue

        v1_submitted_at = normalize_timestamp(newest_doc.get("submittedAt"))

        db = SessionLocal()

        try:
            existing = db.query(Student).filter(Student.student_id == student_id).first()

            if existing:
                yield "UPDATING: " + full_name + " (" + student_id + ")"
                db.delete(existing)
                db.commit()
                updated_count = updated_count + 1
            else:
                yield "NEW FROM V1: " + full_name + " (" + student_id + ")"
                new_count = new_count + 1

            photo_url = upload_photo_if_present(newest_doc, full_name, False)

            new_student = build_student_object(newest_doc, student_id, full_name, v1_submitted_at, photo_url)

            db.add(new_student)
            db.commit()
            db.close()

        except Exception as e:
            yield "ERROR syncing " + student_id + ": " + str(e)
            db.rollback()
            db.close()
            error_count = error_count + 1

    _preview_cache["ready"] = False
    _preview_cache["student_ids"] = []
    _preview_cache["docs_by_id"] = {}

    yield "=== Sync Summary ==="
    yield "New from v1: " + str(new_count)
    yield "Updated (newer version found): " + str(updated_count)
    yield "Errors: " + str(error_count)

    summary = {
        "new_count": new_count,
        "updated_count": updated_count,
        "error_count": error_count
    }

    yield "SUMMARY:" + json.dumps(summary)


if __name__ == "__main__":
    for line in sync_preview_stream():
        if line.startswith("SUMMARY:"):
            print("")
            print(line)
        else:
            print(line)