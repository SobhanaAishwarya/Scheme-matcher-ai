"""Run with:  python -m unittest discover -s tests -v   (or: pytest)"""
import unittest

from scheme_matcher.orchestrator import run_pipeline
from scheme_matcher.personas import PERSONAS
from scheme_matcher.questions import next_question, progress
from scheme_matcher.rules_engine import evaluate_scheme, load_schemes

SCHEMES = {s["id"]: s for s in load_schemes()}


def status(scheme_id, profile):
    return evaluate_scheme(SCHEMES[scheme_id], profile)["status"]


def persona(name_prefix):
    return next(p["profile"] for p in PERSONAS if p["name"].startswith(name_prefix))


class TestDataset(unittest.TestCase):
    def test_dataset_is_well_formed(self):
        self.assertGreaterEqual(len(SCHEMES), 12)
        for s in SCHEMES.values():
            for key in ("name", "short_name", "benefit", "rules", "documents", "apply_url",
                        "how_to_apply", "benefit_score", "specificity"):
                self.assertIn(key, s, f"{s['id']} missing {key}")
            self.assertTrue(s["documents"], f"{s['id']} has no documents checklist")
            for r in s["rules"]:
                self.assertIn("label", r)
                self.assertIn("hint", r)


class TestRules(unittest.TestCase):
    def test_pmegp_eligible(self):
        p = dict(age=30, gender="male", category="general", occupation="entrepreneur",
                 income=100000, business_stage="new", project_cost=800000)
        self.assertEqual(status("pmegp", p), "eligible")

    def test_pmegp_existing_business_is_near_miss(self):
        p = dict(age=30, gender="male", category="general", occupation="entrepreneur",
                 income=100000, business_stage="existing", project_cost=800000)
        self.assertEqual(status("pmegp", p), "near_miss")

    def test_wrong_occupation_not_eligible(self):
        p = dict(age=30, gender="male", category="general", occupation="student",
                 income=100000, education="undergraduate", marks=90.0)
        self.assertEqual(status("pm_kisan", p), "not_eligible")
        self.assertEqual(status("pmegp", p), "not_eligible")

    def test_standup_india_or_group(self):
        base = dict(age=35, occupation="entrepreneur", income=300000,
                    business_stage="new", project_cost=2000000)
        self.assertEqual(status("standup_india", {**base, "gender": "female", "category": "general"}), "eligible")
        self.assertEqual(status("standup_india", {**base, "gender": "male", "category": "st"}), "eligible")
        self.assertEqual(status("standup_india", {**base, "gender": "male", "category": "general"}), "not_eligible")

    def test_standup_india_small_loan_is_near_miss_and_mudra_matches(self):
        p = dict(age=35, gender="female", category="general", occupation="entrepreneur",
                 income=300000, business_stage="new", project_cost=600000)
        self.assertEqual(status("standup_india", p), "near_miss")
        self.assertEqual(status("mudra", p), "eligible")

    def test_income_near_miss_vs_far(self):
        base = dict(age=17, gender="male", category="sc", occupation="student",
                    education="class_11_12")
        self.assertEqual(status("post_matric_sc", {**base, "income": 240000}), "eligible")
        self.assertEqual(status("post_matric_sc", {**base, "income": 300000}), "near_miss")
        self.assertEqual(status("post_matric_sc", {**base, "income": 900000}), "not_eligible")

    def test_boundary_is_inclusive(self):
        p = dict(age=17, gender="male", category="sc", occupation="student",
                 education="class_11_12", income=250000)
        self.assertEqual(status("post_matric_sc", p), "eligible")

    def test_landless_farmer_near_miss_for_pm_kisan(self):
        p = dict(age=40, gender="male", category="general", occupation="farmer",
                 income=100000, land_ha=0.0)
        self.assertEqual(status("pm_kisan", p), "near_miss")
        self.assertEqual(status("kcc", p), "eligible")

    def test_age_boundaries(self):
        p = dict(gender="male", category="general", occupation="homemaker", income=1)
        self.assertEqual(status("apy", {**p, "age": 40}), "eligible")
        self.assertEqual(status("apy", {**p, "age": 41}), "not_eligible")
        self.assertEqual(status("pmsby", {**p, "age": 70}), "eligible")
        self.assertEqual(status("pmsby", {**p, "age": 71}), "not_eligible")
        self.assertEqual(status("ayushman_vay_vandana", {**p, "age": 70}), "eligible")
        self.assertEqual(status("ayushman_vay_vandana", {**p, "age": 69}), "not_eligible")

    def test_salaried_excluded_from_apy(self):
        p = dict(age=30, gender="male", category="general", occupation="salaried", income=600000)
        self.assertEqual(status("apy", p), "not_eligible")
        self.assertEqual(status("pmjjby", p), "eligible")

    def test_missing_value_never_passes(self):
        p = dict(age=30, gender="male", category="general", occupation="entrepreneur", income=1)
        self.assertNotEqual(status("pmegp", p), "eligible")


class TestQuestions(unittest.TestCase):
    def test_adaptive_flow_farmer_gets_land_not_business(self):
        p = {"age": 40, "gender": "male", "category": "obc", "occupation": "farmer", "income": 1}
        self.assertEqual(next_question(p)["id"], "land_ha")
        p["land_ha"] = 1.0
        self.assertIsNone(next_question(p))

    def test_student_flow(self):
        p = {"age": 20, "gender": "male", "category": "obc", "occupation": "student", "income": 1}
        self.assertEqual(next_question(p)["id"], "education")
        p["education"] = "class_9_10"
        self.assertIsNone(next_question(p))  # marks only asked for UG/PG
        p["education"] = "undergraduate"
        self.assertEqual(next_question(p)["id"], "marks")

    def test_question_count_between_5_and_8(self):
        for persona_ in PERSONAS:
            n = len(persona_["profile"])
            self.assertTrue(5 <= n <= 8, f"{persona_['name']} answered {n} questions")

    def test_progress(self):
        answered, total = progress({})
        self.assertEqual(answered, 0)
        self.assertGreaterEqual(total, 5)


class TestPipeline(unittest.TestCase):
    def test_lakshmi(self):
        state = run_pipeline(persona("Lakshmi"))
        elig = {e["scheme_id"] for e in state["ranked"]["eligible"]}
        near = {e["scheme_id"] for e in state["ranked"]["near_miss"]}
        self.assertTrue({"pmegp", "standup_india", "apy", "pmjjby", "pmsby"} <= elig)
        self.assertIn("mudra", near)
        # ranking: highest benefit + targeting first, ranks are consecutive
        ranks = [e["rank"] for e in state["ranked"]["eligible"]]
        self.assertEqual(ranks, list(range(1, len(ranks) + 1)))
        scores = [e["rank_score"] for e in state["ranked"]["eligible"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_ramesh(self):
        state = run_pipeline(persona("Ramesh"))
        elig = {e["scheme_id"] for e in state["ranked"]["eligible"]}
        self.assertEqual(elig, {"pm_kisan", "kcc", "pmjjby", "pmsby"})

    def test_priya(self):
        state = run_pipeline(persona("Priya"))
        elig = {e["scheme_id"] for e in state["ranked"]["eligible"]}
        near = {e["scheme_id"] for e in state["ranked"]["near_miss"]}
        self.assertIn("csss_college", elig)
        self.assertIn("post_matric_sc", near)

    def test_ravi_and_kamala(self):
        ravi = run_pipeline(persona("Ravi"))
        self.assertIn("pmkvy", {e["scheme_id"] for e in ravi["ranked"]["eligible"]})
        kamala = run_pipeline(persona("Kamala"))
        self.assertIn("ayushman_vay_vandana", {e["scheme_id"] for e in kamala["ranked"]["eligible"]})

    def test_every_scheme_has_explanation_and_trace(self):
        state = run_pipeline(persona("Lakshmi"))
        for ev in state["evaluations"]:
            self.assertTrue(ev["explanation"])
        agents = [t["agent"] for t in state["trace"]]
        self.assertEqual(len(agents), 5)
        self.assertIn("Report Agent", agents[-1])

    def test_report_contains_documents_checklist_and_disclaimer(self):
        state = run_pipeline(persona("Ramesh"))
        md = state["report_md"]
        self.assertIn("Documents to keep ready", md)
        self.assertIn("Land ownership records", md)
        self.assertIn("Disclaimer", md)
        if state["report_pdf"] is not None:
            self.assertTrue(state["report_pdf"].startswith(b"%PDF"))

    def test_incomplete_profile_rejected(self):
        with self.assertRaises(ValueError):
            run_pipeline({"age": 30})

    def test_llm_failure_falls_back_to_template(self):
        class BrokenLLM:
            label = "broken"

            def complete(self, *a, **k):
                raise RuntimeError("boom")

        state = run_pipeline(persona("Lakshmi"), llm=BrokenLLM())
        self.assertIn("failed", state["llm_mode"])
        self.assertTrue(all(e["explanation"] for e in state["evaluations"]))

    def test_llm_json_is_used_when_valid(self):
        class FakeLLM:
            label = "fake"

            def complete(self, *a, **k):
                return '```json\n{"summary": "Hello!", "explanations": {"pmegp": "Custom text."}}\n```'

        state = run_pipeline(persona("Lakshmi"), llm=FakeLLM())
        self.assertEqual(state["summary"], "Hello!")
        pmegp = next(e for e in state["evaluations"] if e["scheme_id"] == "pmegp")
        self.assertEqual(pmegp["explanation"], "Custom text.")
        self.assertEqual(pmegp["explanation_source"], "llm")
        other = next(e for e in state["evaluations"] if e["scheme_id"] == "standup_india")
        self.assertEqual(other["explanation_source"], "template")


if __name__ == "__main__":
    unittest.main()
