import unittest
from src.agent import run

def base(material, **kw):
    p={"material_ids":[material["id"]],"materials":[material],"rules":{"blocked_words":["违规"]},"slots":["18:00","19:00"],"schedule":{"2026-11-01":["18:00"]}}
    p.update(kw); return p

class AgentTests(unittest.TestCase):
    def test_normal_conflict_and_duplicate(self):
        m={"id":"M01","title":"片头","content":"正常","duration":30,"date":"2026-11-01","requested_time":"18:00"}
        r=run(base(m)); self.assertEqual(r["results"][0]["suggested_slot"],"19:00"); self.assertEqual(r["results"][0]["save_status"],"saved")
        r2=run(base(m)); self.assertEqual(r2["results"][0]["save_status"],"saved")
    def test_missing_and_risk(self):
        m={"id":"M02","title":"","content":"正常","duration":30,"date":"2026-11-01","requested_time":"19:00"}; self.assertEqual(run(base(m))["results"][0]["review_status"],"insufficient")
        m["id"]="M03"; m["title"]="含违规"; self.assertEqual(run(base(m))["results"][0]["review_status"],"risk")
    def test_save_failure_and_no_slot(self):
        m={"id":"M04","title":"片","content":"正常","duration":30,"date":"2026-11-01","requested_time":"19:00"}; self.assertEqual(run(base(m,save_failure=True))["results"][0]["save_status"],"failed")
        self.assertEqual(run(base(m,slots=["19:00"],schedule={"2026-11-01":["18:00","19:00"]}))["results"][0]["review_status"],"blocked")

if __name__ == "__main__": unittest.main()
