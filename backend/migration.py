import os
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

DRY_RUN = False


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


def fix_duplicates():
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client["fastnu_cv_tool"]
    submissions_collection = mongo_db["submissions"]

    db = SessionLocal()

    print("DRY_RUN is set to " + str(DRY_RUN))
    print("")

    duplicated_ids_cursor = submissions_collection.aggregate([
        {"$group": {"_id": "$studentId", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ])

    duplicated_student_ids = []
    for row in duplicated_ids_cursor:
        duplicated_student_ids.append(row["_id"])

    print("Found " + str(len(duplicated_student_ids)) + " student IDs with duplicate submissions.")
    print("")

    fixed_count = 0
    error_count = 0

    for student_id in duplicated_student_ids:
        if not student_id:
            continue

        newest_doc = submissions_collection.find(
            {"studentId": student_id}
        ).sort("submittedAt", -1).limit(1)

        newest_doc = list(newest_doc)
        if not newest_doc:
            continue

        newest_doc = newest_doc[0]
        full_name = get_value(newest_doc, "fullName")

        if not full_name:
            print("SKIPPING " + student_id + " (newest doc missing fullName)")
            continue

        try:
            existing = db.query(Student).filter(Student.student_id == student_id).first()

            if existing:
                print("REPLACING: " + full_name + " (" + student_id + ") - deleting old row, id=" + str(existing.id))
                if not DRY_RUN:
                    db.delete(existing)
                    db.commit()
            else:
                print("INSERTING NEW: " + full_name + " (" + student_id + ")")

            photo_url = upload_photo_if_present(newest_doc, full_name, DRY_RUN)

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
                is_deleted=False
            )

            if not DRY_RUN:
                db.add(new_student)
                db.commit()

            fixed_count = fixed_count + 1

        except Exception as e:
            print("ERROR fixing " + student_id + ": " + str(e))
            db.rollback()
            error_count = error_count + 1

    db.close()
    mongo_client.close()

    print("")
    print("=== Fix Summary ===")
    print("Fixed: " + str(fixed_count))
    print("Errors: " + str(error_count))
    if DRY_RUN:
        print("")
        print("This was a DRY RUN. No data was actually changed in Postgres.")
        print("Review the output above, then set DRY_RUN = False and run again.")


if __name__ == "__main__":
    fix_duplicates()