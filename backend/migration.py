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


def sync_from_v1_stream(dry_run):
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client["fastnu_cv_tool"]
    submissions_collection = mongo_db["submissions"]

    db = SessionLocal()

    yield "dry_run is set to " + str(dry_run)

    pipeline = [
        {"$sort": {"submittedAt": -1}},
        {"$group": {"_id": "$studentId", "doc": {"$first": "$$ROOT"}}}
    ]
    newest_docs_cursor = submissions_collection.aggregate(pipeline)

    all_existing = db.query(Student).all()
    existing_by_id = {}
    for student in all_existing:
        existing_by_id[student.student_id] = student

    new_count = 0
    updated_count = 0
    unchanged_count = 0
    error_count = 0

    new_students = []
    updated_students = []
    error_students = []

    for row in newest_docs_cursor:
        student_id = row["_id"]
        newest_doc = row["doc"]

        if not student_id:
            continue

        full_name = get_value(newest_doc, "fullName")

        if not full_name:
            continue

        v1_submitted_at = newest_doc.get("submittedAt")

        try:
            existing = existing_by_id.get(student_id)

            if existing and existing.source_submitted_at is not None:
                existing_ts = existing.source_submitted_at
                if existing_ts.tzinfo is None:
                    existing_ts = existing_ts.replace(tzinfo=timezone.utc)

                if v1_submitted_at and v1_submitted_at <= existing_ts:
                    unchanged_count = unchanged_count + 1
                    continue

            if existing:
                yield "UPDATING: " + full_name + " (" + student_id + ")"
                if not dry_run:
                    db.delete(existing)
                    db.commit()
                updated_count = updated_count + 1
                updated_students.append(full_name + " (" + student_id + ")")
            else:
                yield "NEW FROM V1: " + full_name + " (" + student_id + ")"
                new_count = new_count + 1
                new_students.append(full_name + " (" + student_id + ")")

            photo_url = upload_photo_if_present(newest_doc, full_name, dry_run)

            new_student = Student(
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

            if not dry_run:
                db.add(new_student)
                db.commit()

        except Exception as e:
            yield "ERROR syncing " + student_id + ": " + str(e)
            db.rollback()
            error_count = error_count + 1
            error_students.append(student_id + ": " + str(e))

    db.close()
    mongo_client.close()

    yield "=== Sync Summary ==="
    yield "New from v1: " + str(new_count)
    yield "Updated (newer version found): " + str(updated_count)
    yield "Unchanged (already up to date): " + str(unchanged_count)
    yield "Errors: " + str(error_count)

    summary = {
        "dry_run": dry_run,
        "new_count": new_count,
        "updated_count": updated_count,
        "unchanged_count": unchanged_count,
        "error_count": error_count,
        "new_students": new_students,
        "updated_students": updated_students,
        "error_students": error_students
    }

    yield "SUMMARY:" + json.dumps(summary)

if __name__ == "__main__":
    for line in sync_from_v1_stream(dry_run=True):
        if line.startswith("SUMMARY:"):
            print("")
            print(line)
        else:
            print(line)