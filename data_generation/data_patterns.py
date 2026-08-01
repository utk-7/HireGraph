import random
import uuid
from datetime import datetime, timedelta

from data_gen import generate_review_text


class PatternInjector:
    def __init__(self, nodes, relationships, seed=42):
        self.nodes = nodes
        self.relationships = relationships
        self.seed = seed
        random.seed(self.seed)
        self.target_ids = {"attrition": [], "control": []}

    def inject_attrition_pattern(self):
        # Find candidates who were hired
        hired_cands = [
            e for e in self.nodes["Employee"] if e.get("converted_from_candidate")
        ]

        # Select proportionally: ~5% for attrition, 5% for control
        num_pattern = max(5, int(len(hired_cands) * 0.05))

        if len(hired_cands) < num_pattern * 2:
            num_pattern = len(hired_cands) // 2

        selected = random.sample(hired_cands, num_pattern * 2)
        attrition_group = selected[:num_pattern]
        control_group = selected[num_pattern:]

        # For demo purposes, we only log the first 5 of each to pattern_targets.json
        # to keep the JSON clean, but we inject the pattern into all of them.

        for idx, emp in enumerate(attrition_group):
            cand_id = emp["candidate_id"]
            if idx < 5:
                self.target_ids["attrition"].append(
                    {"cand_id": cand_id, "emp_id": emp["id"]}
                )

            # 1. Negative Interview Review
            self._ensure_review(
                cand_id, "Candidate", "interview_experience", "negative"
            )

            # 2. Short tenure, left company
            emp["tenure_months"] = random.randint(1, 5)
            emp["still_employed"] = False

            # 3. Negative Employee Review
            self._ensure_review(
                emp["id"],
                "Employee",
                "employee_experience",
                "negative",
                company_id=emp["company_id"],
            )

        for idx, emp in enumerate(control_group):
            cand_id = emp["candidate_id"]
            if idx < 5:
                self.target_ids["control"].append(
                    {"cand_id": cand_id, "emp_id": emp["id"]}
                )

            # 1. Positive Interview Review
            self._ensure_review(
                cand_id, "Candidate", "interview_experience", "positive"
            )

            # 2. Long tenure, still employed
            emp["tenure_months"] = random.randint(36, 60)
            emp["still_employed"] = True

            # 3. Positive Employee Review
            self._ensure_review(
                emp["id"],
                "Employee",
                "employee_experience",
                "positive",
                company_id=emp["company_id"],
            )

    def _ensure_review(
        self, author_id, author_type, review_type, sentiment, company_id=None
    ):
        # Find existing review by this author of this type
        existing_rel = next(
            (
                r
                for r in self.relationships
                if r["source_id"] == author_id
                and r["source_type"] == author_type
                and r["rel_type"] == "WROTE"
            ),
            None,
        )

        target_entity_id = None
        target_entity_type = None

        if review_type == "interview_experience":
            # Target is a job posting from their application
            app_rel = next(
                (
                    r
                    for r in self.relationships
                    if r["source_id"] == author_id and r["rel_type"] == "SUBMITTED"
                ),
                None,
            )
            if app_rel:
                job_rel = next(
                    (
                        r
                        for r in self.relationships
                        if r["source_id"] == app_rel["target_id"]
                        and r["rel_type"] == "FOR_POSTING"
                    ),
                    None,
                )
                if job_rel:
                    target_entity_id = job_rel["target_id"]
                    target_entity_type = "JobPosting"
        else:
            target_entity_id = company_id
            target_entity_type = "Company"

        if not target_entity_id:
            return  # Cannot associate

        rev_id = None
        if existing_rel:
            rev_id = existing_rel["target_id"]
            # Find the review node
            rev_node = next(
                (n for n in self.nodes["Review"] if n["id"] == rev_id), None
            )
            if rev_node and rev_node["review_type"] == review_type:
                rev_node["text"] = generate_review_text(sentiment, review_type)
                rev_node["rating"] = (
                    random.randint(4, 5)
                    if sentiment == "positive"
                    else (random.randint(1, 2) if sentiment == "negative" else 3)
                )
                if review_type == "employee_experience":
                    rev_node["recommends"] = True if sentiment == "positive" else False
                return

        # Create new review if not existing
        rev_id = f"REV-{uuid.UUID(int=random.getrandbits(128), version=4)}"
        self.nodes["Review"].append(
            {
                "id": rev_id,
                "text": generate_review_text(sentiment, review_type),
                "rating": (
                    random.randint(4, 5)
                    if sentiment == "positive"
                    else (random.randint(1, 2) if sentiment == "negative" else 3)
                ),
                "review_date": "2024-01-01T12:00:00.000000",  # fixed mock date for exact reproducibility
                "review_type": review_type,
                "recommends": (
                    True
                    if sentiment == "positive"
                    else (
                        (False if sentiment == "negative" else None)
                        if review_type == "employee_experience"
                        else None
                    )
                ),
            }
        )
        self.relationships.append(
            {
                "source_type": author_type,
                "source_id": author_id,
                "rel_type": "WROTE",
                "target_type": "Review",
                "target_id": rev_id,
            }
        )
        self.relationships.append(
            {
                "source_type": "Review",
                "source_id": rev_id,
                "rel_type": "ABOUT",
                "target_type": target_entity_type,
                "target_id": target_entity_id,
            }
        )

    def inject_delayed_offer_pattern(self):
        # Pick one department
        if not self.nodes["Department"]:
            return
        target_dept = self.nodes["Department"][0]

        # Find applications for jobs in this dept that resulted in an offer
        dept_jobs = [
            r["target_id"]
            for r in self.relationships
            if r["source_id"] == target_dept["id"] and r["rel_type"] == "POSTED"
        ]

        for app in self.nodes["Application"]:
            job_rel = next(
                (
                    r
                    for r in self.relationships
                    if r["source_id"] == app["id"] and r["rel_type"] == "FOR_POSTING"
                ),
                None,
            )
            offer_rel = next(
                (
                    r
                    for r in self.relationships
                    if r["source_id"] == app["id"] and r["rel_type"] == "RESULTED_IN"
                ),
                None,
            )

            if job_rel and job_rel["target_id"] in dept_jobs and offer_rel:
                # Inflate the gap between applied_date and offer decision_date
                offer_node = next(
                    o for o in self.nodes["Offer"] if o["id"] == offer_rel["target_id"]
                )

                app_date = datetime.fromisoformat(app["applied_date"])
                # Make decision date 90-120 days later
                new_dec_date = app_date + timedelta(days=random.randint(90, 120))

                offer_node["decision_date"] = new_dec_date.isoformat()
                offer_node["extended_date"] = (
                    new_dec_date - timedelta(days=5)
                ).isoformat()

    def inject_negative_interview_round_pattern(self):
        # Pick one JobPosting
        if not self.nodes["JobPosting"]:
            return
        target_job = self.nodes["JobPosting"][-1]

        # Find applications for this job
        apps_for_job = [
            r["source_id"]
            for r in self.relationships
            if r["target_id"] == target_job["id"] and r["rel_type"] == "FOR_POSTING"
        ]

        for app_id in apps_for_job:
            # Find interviews for this application in round 3
            interview_rels = [
                r
                for r in self.relationships
                if r["source_id"] == app_id and r["rel_type"] == "HAS_INTERVIEW"
            ]
            for ir in interview_rels:
                int_node = next(
                    i for i in self.nodes["Interview"] if i["id"] == ir["target_id"]
                )
                if int_node["round_number"] == 3:
                    # Inject extremely negative review specifically citing round 3
                    cand_id = next(
                        r["source_id"]
                        for r in self.relationships
                        if r["target_id"] == app_id and r["rel_type"] == "SUBMITTED"
                    )
                    self._ensure_review(
                        cand_id, "Candidate", "interview_experience", "negative"
                    )

                    # Make it specifically about round 3
                    rev_rel = next(
                        (
                            r
                            for r in self.relationships
                            if r["source_id"] == cand_id and r["rel_type"] == "WROTE"
                        ),
                        None,
                    )
                    if rev_rel:
                        rev_node = next(
                            (
                                n
                                for n in self.nodes["Review"]
                                if n["id"] == rev_rel["target_id"]
                                and n["review_type"] == "interview_experience"
                            ),
                            None,
                        )
                        if rev_node:
                            rev_node["text"] = (
                                f"Round 3 was a disaster. {rev_node['text']}"
                            )

    def run_all(self):
        self.inject_attrition_pattern()
        self.inject_delayed_offer_pattern()
        self.inject_negative_interview_round_pattern()
        return self.nodes, self.relationships
