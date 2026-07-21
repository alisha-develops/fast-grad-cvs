# FAST graduate directory cv collection 2026

i created this to support the career services department at [FAST NUCES Karachi](https://khi.nu.edu.pk/). this idea came from my sister, a liaison officer, who was managing graduate information through google forms. to simplify the process, i built this form as a centralized platform for collecting student profiles, managing submissions, and generating professional cvs.

> note: this is the version 2! i did make a version 1 that has 500 submissions already, but first version proved the concept but wasn't designed for long term scalability. as the number of real student submissions grew(and is still growing), it became difficult to maintain and lacked a robust backend. v2 rebuilds the platform with a proper backend architecture.

<table border="1" cellpadding="12" cellspacing="0">
  <tr>
    <th align="left">ai usage</th>
    <th align="center">cv template</th>
  </tr>
  <tr>
    <td valign="top" width="65%">
      <code>livepreview.js</code> and <code>preview.css</code> (livepreview.css almost also uses the same code) were mostly generated with claude's help, based on a design carried over and adapted from an earlier prototype (v1) of this tool. the final template(showed in picture) was approved by my sister before being used for actual graduate submissions, so i had the code generated to match that approved design. however generated file was really messy so i had to make some modifications.<br>
      note: i also pasted some code directly from the previous version (v1) where i needed to match its structure and mainly frontend :)
    </td>
    <td align="center" width="35%">
      <img src="https://cdn.hackclub.com/019f77a8-336e-75b1-8452-b0d59a73cfcf/2026-07-19%20(1).png" alt="cv template" width="220">
    </td>
  </tr>
</table>

## admin access

the admin dashboard at `/admin` requires a password, managed via the
`ADMIN_PASSWORD` environment variable and not included in this repository.

[here](https://youtu.be/lYwLreLOLP4) i have attached a demo video that shows the admin panel in action including search/filter,
cv preview, print, delete, and restore without requiring login access. **if you still would like to try the live dashboard yourself then pls reach me out on slack:  @Alisha**


### deployment
this project is currently deployed on a free vercel domain
(https://fast-grad-cvs.vercel.app/). this is intentional as this tool was built as an
independent student effort, not an official fast nuces deployment, so it
doesn't carry a university branded domain at this stage. that said, it(v1 of it) is actively in use by the career service department for
collecting and managing 2026 graduate cv submissions. the Vercel domain
reflects the project's current status honestly and if this v2 is reviewed and approved by the karachi campus administration,
a university associated domain may become appropriate at that point.

**also:** existing v1 submissions (stored in mongodb) have not yet been migrated to
this v2 system. migration to neon postgres, along with credential rotation,
is planned following external review.

### project structure and some notes (learning along the way + yap)

earlier in development, i split the backend folder into `core/`, `models/`, and
`schemas/` subfolders. but as the project grew, each of those folders ended up holding exactly one file so the separation wasn't actually organizing anything yet - it was structure
without content to justify it. today (20-july-2026), i flattened them into the `backend/` root directly (`database.py`, `student_model.py`, `submission_schema.py`), using
suffixes instead of folder names to keep each file's role clear (and ofc to make it easier for reviewers).

i'm keeping this note because i think it's worth yapping about that you don't always know the right structure for a project on day one. building with time gives you more perspective so you see what you actually reach for, what stays empty scaffolding, and what genuinely needs separating once real complexity shows up. if this project grows to include more models (e.g. an
admin users table, a feedback table), reintroducing a `models/` folder at
that point would take minutes but forcing that structure prematurely, with nothing to organize, just adds friction without benefit so yeah! 

## tech

i built the backend with [FastAPI (Python)](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/) for the database
ORM and PostgreSQL (hosted on [neon](https://neon.com/)) to store everything. form
submissions are checked with pydantic before saving, and the admin
dashboard and cv pages are rendered server side with jinja2 templates.

the frontend is plain html, css, and javascript with no framework,
split into separate files per page, the graduate submission form, the
admin dashboard, and the cv preview, to keep things maintainable.

one more thing that the student passport photos are uploaded to and served from [cloudinary](https://cloudinary.com/), cvs are exported as pdfs using the browser's native print function
as i looked into using weasyprint for real server side pdf generation, but
decided against it since it needs system level dependencies that vercel's
serverless environment doesnt support.
