import random
import uuid
from datetime import datetime, timedelta

from faker import Faker


def generate_review_text(sentiment, review_type):
    if review_type == "interview_experience":
        if sentiment == "positive":
            openings = [
                "I had a great time interviewing here.",
                "The interview process was very smooth.",
                "Really enjoyed meeting the team.",
            ]
            details = [
                "The recruiters were responsive.",
                "Technical questions were fair and relevant.",
                "The panel was very welcoming.",
            ]
            closings = [
                "Would highly recommend.",
                "Looking forward to hearing back.",
                "A very professional experience overall.",
            ]
        elif sentiment == "negative":
            openings = [
                "The interview process was frustrating.",
                "I had a terrible experience interviewing.",
                "Very disjointed interview process.",
            ]
            details = [
                "The interviewer showed up late.",
                "Technical questions were completely unrelated to the job.",
                "Recruiter ghosted me for weeks.",
            ]
            closings = [
                "Would not recommend applying.",
                "I withdrew my application.",
                "A huge waste of time.",
            ]
        else:
            openings = [
                "The interview was okay.",
                "Standard interview process.",
                "Nothing special about the interview.",
            ]
            details = [
                "Questions were standard Leetcode.",
                "Met with a few team members.",
                "Process took a few weeks.",
            ]
            closings = [
                "Overall an average experience.",
                "We will see what happens.",
                "Standard corporate process.",
            ]
    else:
        if sentiment == "positive":
            openings = [
                "I love working here.",
                "This is a great company.",
                "Fantastic culture and people.",
            ]
            details = [
                "Management really cares about you.",
                "Great work-life balance.",
                "Lots of opportunities for growth.",
            ]
            closings = [
                "I plan to stay here a long time.",
                "Highly recommend it to anyone.",
                "Best job I've had.",
            ]
        elif sentiment == "negative":
            openings = [
                "Working here has been difficult.",
                "I do not recommend this company.",
                "Toxic environment.",
            ]
            details = [
                "Management is completely out of touch.",
                "Zero work-life balance.",
                "No clear path for promotion.",
            ]
            closings = [
                "I am actively looking for a new job.",
                "Avoid at all costs.",
                "Turnover is very high for a reason.",
            ]
        else:
            openings = [
                "It's an okay place to work.",
                "Average corporate job.",
                "Pays the bills.",
            ]
            details = [
                "Some teams are better than others.",
                "Benefits are standard.",
                "Work can be monotonous.",
            ]
            closings = [
                "Not bad, but not great.",
                "I might stay a year or two.",
                "It's just a job.",
            ]

    return (
        f"{random.choice(openings)} {random.choice(details)} {random.choice(closings)}"
    )


class DataGenerator:
    def __init__(self, seed: int = 42, scale_factor: int = 1):
        self.seed = seed
        self.scale_factor = scale_factor

        # We must seed both random and faker
        random.seed(self.seed)
        self.fake = Faker()
        Faker.seed(self.seed)

        self.nodes = {
            "Company": [],
            "Department": [],
            "JobPosting": [],
            "Candidate": [],
            "Application": [],
            "Interview": [],
            "Recruiter": [],
            "Interviewer": [],
            "Offer": [],
            "Employee": [],
            "Review": [],
        }
        self.relationships = []

        self.job_to_dept = {}
        self.dept_to_company = {}
        self.dept_to_interviewers = {}
        self.dept_to_name = {}

    def add_rel(
        self, source_type, source_id, rel_type, target_type, target_id, props=None
    ):
        rel = {
            "source_type": source_type,
            "source_id": source_id,
            "rel_type": rel_type,
            "target_type": target_type,
            "target_id": target_id,
        }
        if props:
            rel.update(props)
        self.relationships.append(rel)

    def generate_all(self):
        num_companies = 10 * self.scale_factor

        departments = [
            "Engineering",
            "Sales",
            "Marketing",
            "HR",
            "Product",
            "Design",
            "Finance",
        ]
        levels = ["Entry", "Mid", "Senior", "Lead", "Director"]
        remote_types = ["Remote", "Hybrid", "On-site"]

        # Generate Companies & Departments
        for c_idx in range(num_companies):
            company_id = f"CMP-{c_idx}"
            self.nodes["Company"].append(
                {
                    "id": company_id,
                    "name": self.fake.company(),
                    "industry": random.choice(
                        ["Tech", "Healthcare", "Finance", "Retail", "Energy"]
                    ),
                    "size": random.choice(
                        ["1-50", "51-200", "201-500", "501-1000", "1000+"]
                    ),
                    "headquarters": self.fake.city(),
                    "founded_year": random.randint(1990, 2023),
                }
            )

            # Each company has a few departments
            num_deps = random.randint(3, len(departments))
            deps_for_company = random.sample(departments, num_deps)

            for dept_name in deps_for_company:
                dept_id = f"{company_id}-DEPT-{dept_name}"
                self.dept_to_name[dept_id] = dept_name
                self.dept_to_company[dept_id] = company_id
                self.dept_to_interviewers[dept_id] = []

                self.nodes["Department"].append({"id": dept_id, "name": dept_name})
                self.add_rel(
                    "Company", company_id, "HAS_DEPARTMENT", "Department", dept_id
                )

                # Each department has some JobPostings
                num_jobs = random.randint(1, 5) * (1 if self.scale_factor < 10 else 2)
                for _ in range(num_jobs):
                    job_id = f"JOB-{uuid.UUID(int=random.getrandbits(128), version=4)}"
                    self.job_to_dept[job_id] = dept_id

                    sal_base = random.randint(60000, 150000)
                    self.nodes["JobPosting"].append(
                        {
                            "id": job_id,
                            "title": f"{random.choice(levels)} {dept_name} {random.choice(['Specialist', 'Manager', 'Analyst', 'Engineer'])}",
                            "level": random.choice(levels),
                            "salary_min": sal_base,
                            "salary_max": sal_base + random.randint(10000, 50000),
                            "status": random.choice(["Open", "Closed"]),
                            "posted_date": self.fake.date_between(
                                start_date="-1y", end_date="today"
                            ).isoformat(),
                            "remote_type": random.choice(remote_types),
                        }
                    )
                    self.add_rel("Department", dept_id, "POSTED", "JobPosting", job_id)

                # Generate some Interviewers for this department
                num_interviewers = random.randint(1, 3)
                for _ in range(num_interviewers):
                    int_id = f"INTV-{uuid.UUID(int=random.getrandbits(128), version=4)}"
                    self.nodes["Interviewer"].append(
                        {
                            "id": int_id,
                            "name": self.fake.name(),
                            "role": f"{dept_name} Staff",
                            "department": dept_name,
                        }
                    )
                    self.add_rel(
                        "Interviewer", int_id, "WORKS_IN", "Department", dept_id
                    )
                    self.dept_to_interviewers[dept_id].append(int_id)

        # Generate Recruiters
        num_recruiters = 5 * self.scale_factor
        recruiters = []
        for _ in range(num_recruiters):
            rec_id = f"REC-{uuid.UUID(int=random.getrandbits(128), version=4)}"
            recruiters.append(rec_id)
            self.nodes["Recruiter"].append(
                {
                    "id": rec_id,
                    "name": self.fake.name(),
                    "tenure_years": random.randint(1, 10),
                }
            )

        # Generate Candidates and their Applications
        num_candidates = 400 * self.scale_factor
        job_ids = [j["id"] for j in self.nodes["JobPosting"]]
        all_interviewers = [i["id"] for i in self.nodes["Interviewer"]]

        for _ in range(num_candidates):
            cand_id = f"CAND-{uuid.UUID(int=random.getrandbits(128), version=4)}"
            cand_name = self.fake.name()
            self.nodes["Candidate"].append(
                {
                    "id": cand_id,
                    "name": cand_name,
                    "years_experience": random.randint(0, 15),
                    "location": self.fake.city(),
                    "source": random.choice(
                        ["LinkedIn", "Referral", "Indeed", "Company Website", "Agency"]
                    ),
                }
            )

            # Candidate applies to 1-3 jobs
            num_apps = random.randint(1, 3)
            applied_jobs = random.sample(job_ids, min(num_apps, len(job_ids)))

            for job_id in applied_jobs:
                app_id = f"APP-{uuid.UUID(int=random.getrandbits(128), version=4)}"
                app_date = self.fake.date_between(start_date="-6m", end_date="today")
                status = random.choice(
                    ["Rejected", "Withdrawn", "Hired", "In Progress"]
                )

                self.nodes["Application"].append(
                    {
                        "id": app_id,
                        "applied_date": app_date.isoformat(),
                        "current_stage": random.choice(
                            ["Screen", "Technical", "Onsite", "Offer"]
                        ),
                        "status": status,
                    }
                )

                self.add_rel("Candidate", cand_id, "SUBMITTED", "Application", app_id)
                self.add_rel("Application", app_id, "FOR_POSTING", "JobPosting", job_id)
                self.add_rel(
                    "Application",
                    app_id,
                    "MANAGED_BY",
                    "Recruiter",
                    random.choice(recruiters),
                )

                # Interviews for application
                num_interviews = random.randint(1, 4)
                dept_id = self.job_to_dept[job_id]
                dept_interviewers = self.dept_to_interviewers.get(dept_id, [])
                if not dept_interviewers:
                    dept_interviewers = all_interviewers

                for round_num in range(1, num_interviews + 1):
                    int_id = f"INT-{uuid.UUID(int=random.getrandbits(128), version=4)}"
                    int_date = app_date + timedelta(
                        days=round_num * random.randint(3, 10)
                    )
                    self.nodes["Interview"].append(
                        {
                            "id": int_id,
                            "round_number": round_num,
                            "interview_type": random.choice(
                                ["Behavioral", "Technical", "Panel", "Hiring Manager"]
                            ),
                            "date": int_date.isoformat(),
                            "outcome": random.choice(["Pass", "Fail", "Borderline"]),
                        }
                    )
                    self.add_rel(
                        "Application", app_id, "HAS_INTERVIEW", "Interview", int_id
                    )
                    self.add_rel(
                        "Interview",
                        int_id,
                        "CONDUCTED_BY",
                        "Interviewer",
                        random.choice(dept_interviewers),
                    )

                # Candidate might leave an interview review
                if random.random() < 0.35:
                    rev_id = f"REV-{uuid.UUID(int=random.getrandbits(128), version=4)}"
                    sentiment = random.choice(["positive", "neutral", "negative"])
                    self.nodes["Review"].append(
                        {
                            "id": rev_id,
                            "text": generate_review_text(
                                sentiment, "interview_experience"
                            ),
                            "rating": (
                                random.randint(4, 5)
                                if sentiment == "positive"
                                else (
                                    random.randint(1, 2)
                                    if sentiment == "negative"
                                    else 3
                                )
                            ),
                            "review_date": (app_date + timedelta(days=30)).isoformat(),
                            "review_type": "interview_experience",
                            "recommends": None,  # Only for employee
                        }
                    )
                    self.add_rel("Candidate", cand_id, "WROTE", "Review", rev_id)
                    self.add_rel("Review", rev_id, "ABOUT", "JobPosting", job_id)

                # Offer and Employee creation if hired
                if status == "Hired":
                    offer_id = (
                        f"OFF-{uuid.UUID(int=random.getrandbits(128), version=4)}"
                    )
                    dec_date = app_date + timedelta(days=random.randint(15, 45))
                    self.nodes["Offer"].append(
                        {
                            "id": offer_id,
                            "base_salary": random.randint(80000, 160000),
                            "equity": random.randint(0, 50000),
                            "bonus": random.randint(0, 20000),
                            "extended_date": (dec_date - timedelta(days=3)).isoformat(),
                            "decision": "Accepted",
                            "decision_date": dec_date.isoformat(),
                        }
                    )
                    self.add_rel(
                        "Application", app_id, "RESULTED_IN", "Offer", offer_id
                    )

                    emp_id = f"EMP-{uuid.UUID(int=random.getrandbits(128), version=4)}"
                    hire_date = dec_date + timedelta(days=random.randint(10, 30))
                    still_employed = random.choice([True, False])
                    company_id = self.dept_to_company[dept_id]

                    # Quick lookup for job title
                    job_title = "Unknown"
                    for j in self.nodes["JobPosting"]:
                        if j["id"] == job_id:
                            job_title = j["title"]
                            break

                    self.nodes["Employee"].append(
                        {
                            "id": emp_id,
                            "name": cand_name,
                            "title": job_title,
                            "department": self.dept_to_name[dept_id],
                            "hire_date": hire_date.isoformat(),
                            "tenure_months": (
                                random.randint(1, 48)
                                if not still_employed
                                else random.randint(1, 60)
                            ),
                            "still_employed": still_employed,
                            "converted_from_candidate": True,
                            "candidate_id": cand_id,  # useful for linkage later
                            "company_id": company_id,
                        }
                    )
                    self.add_rel("Candidate", cand_id, "HIRED_AS", "Employee", emp_id)
                    self.add_rel("Employee", emp_id, "WORKS_IN", "Department", dept_id)

                    # Employee might leave an employee review
                    if company_id and random.random() < 0.7:
                        rev_id = (
                            f"REV-{uuid.UUID(int=random.getrandbits(128), version=4)}"
                        )
                        sentiment = random.choice(["positive", "neutral", "negative"])
                        self.nodes["Review"].append(
                            {
                                "id": rev_id,
                                "text": generate_review_text(
                                    sentiment, "employee_experience"
                                ),
                                "rating": (
                                    random.randint(4, 5)
                                    if sentiment == "positive"
                                    else (
                                        random.randint(1, 2)
                                        if sentiment == "negative"
                                        else 3
                                    )
                                ),
                                "review_date": (
                                    hire_date + timedelta(days=random.randint(30, 365))
                                ).isoformat(),
                                "review_type": "employee_experience",
                                "recommends": (
                                    True if sentiment == "positive" else False
                                ),
                            }
                        )
                        self.add_rel("Employee", emp_id, "WROTE", "Review", rev_id)
                        self.add_rel("Review", rev_id, "ABOUT", "Company", company_id)

        return self.nodes, self.relationships
