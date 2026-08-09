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


def migrate():
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client["fastnu_cv_tool"]
    submissions_collection = mongo_db["submissions"]

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    total_docs = submissions_collection.count_documents({})
    print("Found " + str(total_docs) + " documents in MongoDB.")
    print("DRY_RUN is set to " + str(DRY_RUN))
    print("")

    migrated_count = 0
    skipped_count = 0
    error_count = 0

    for doc in submissions_collection.find():
        full_name = get_value(doc, "fullName")
        student_id = get_value(doc, "studentId")

        if not full_name or not student_id:
            print("SKIPPING doc with missing fullName or studentId: " + str(doc.get("_id")))
            skipped_count = skipped_count + 1
            continue

        existing = db.query(Student).filter(Student.student_id == student_id).first()
        if existing:
            print("SKIPPING (already migrated): " + full_name + " (" + student_id + ")")
            skipped_count = skipped_count + 1
            continue

        try:
            photo_url = upload_photo_if_present(doc, full_name, DRY_RUN)

            new_student = Student(
                full_name=full_name,
                student_id=student_id,
                email=get_value(doc, "email"),
                phone=get_value(doc, "phone"),
                cgpa=get_value(doc, "cgpa"),
                degree_program=get_value(doc, "degreeProgram"),
                linkedin=get_value(doc, "linkedin"),
                portfolio=get_value(doc, "portfolio"),
                objective=get_value(doc, "objective"),
                education=get_value(doc, "education"),
                fyp_title=get_value(doc, "fypTitle"),
                fyp_desc=get_value(doc, "fypDesc"),
                fyp_supervisor=get_value(doc, "fypSupervisor"),
                elective_courses=get_value(doc, "electiveCourses"),
                areas_of_interest=get_value(doc, "areasOfInterest"),
                technical_skills=get_value(doc, "technicalSkills"),
                personal_skills=get_value(doc, "personalSkills"),
                certifications=get_value(doc, "certifications"),
                honors=get_value(doc, "honors"),
                internship=get_value(doc, "internship"),
                leadership=get_value(doc, "leadership"),
                photo_url=photo_url,
                is_deleted=False
            )

            print("MIGRATING: " + full_name + " (" + student_id + ")" + (" [photo uploaded]" if photo_url else ""))

            if not DRY_RUN:
                db.add(new_student)
                db.commit()

            migrated_count = migrated_count + 1

        except Exception as e:
            print("ERROR migrating " + full_name + ": " + str(e))
            db.rollback()
            error_count = error_count + 1

    db.close()
    mongo_client.close()

    print("")
    print("=== Migration Summary ===")
    print("Migrated: " + str(migrated_count))
    print("Skipped: " + str(skipped_count))
    print("Errors: " + str(error_count))
    if DRY_RUN:
        print("")
        print("This was a DRY RUN. No data was actually written to Postgres.")
        print("Review the output above, then set DRY_RUN = False and run again.")


if __name__ == "__main__":
    migrate()