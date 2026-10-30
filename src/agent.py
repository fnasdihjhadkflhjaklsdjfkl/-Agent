"""Offline material review and scheduling agent."""
import argparse, json, sys
from dataclasses import dataclass
from pathlib import Path

@dataclass
class State:
    calls: int = 0
    max_calls: int = 8
    trace: list = None
    def __post_init__(self): self.trace = [] if self.trace is None else self.trace

class Tools:
    def __init__(self, payload):
        self.p = payload; self.saved = {}
    def call(self, state, name, args):
        if state.calls >= state.max_calls: raise RuntimeError("tool_call_limit")
        state.calls += 1
        try: result = getattr(self, name)(**args)
        except Exception as e: result = {"ok": False, "error": str(e)}
        state.trace.append({"step": state.calls, "tool": name, "params": args, "result": result})
        return result
    def read_material(self, material_id):
        m = next((x for x in self.p.get("materials", []) if x.get("id") == material_id), None)
        return {"ok": bool(m), "material": m, "error": None if m else "material_not_found"}
    def check_rules(self, material):
        missing = [k for k in ("title", "content", "duration") if not material.get(k)]
        risks = []
        for word in self.p.get("rules", {}).get("blocked_words", []):
            if word in (material.get("title", "") + material.get("content", "")): risks.append("blocked_word:" + word)
        return {"ok": True, "status": "insufficient" if missing else ("risk" if risks else "pass"), "missing": missing, "risks": risks}
    def query_slots(self, date, requested, duration):
        occupied = self.p.get("schedule", {}).get(date, [])
        available = [x for x in self.p.get("slots", []) if x not in occupied]
        return {"ok": True, "requested": requested, "occupied": requested in occupied, "available": available}
    def save_draft(self, draft):
        if self.p.get("save_failure"): return {"ok": False, "error": "save_failed"}
        key = json.dumps(draft, sort_keys=True, ensure_ascii=False)
        if key in self.saved: return {"ok": True, "status": "duplicate", "draft_id": self.saved[key]}
        did = "D%03d" % (len(self.saved) + 1); self.saved[key] = did
        return {"ok": True, "status": "saved", "draft_id": did}

def run(payload):
    state = State(max_calls=payload.get("max_calls", 8)); tools = Tools(payload); results=[]
    for material_id in payload.get("material_ids", []):
        read = tools.call(state, "read_material", {"material_id": material_id})
        if not read["ok"]:
            results.append({"material_id": material_id, "review_status":"blocked", "risk_reasons":[read["error"]], "save_status":"not_saved"}); continue
        material = read["material"]; rule = tools.call(state, "check_rules", {"material": material})
        base = {"material_id": material_id, "review_status": rule["status"], "risk_reasons": rule["risks"], "pending_confirmation": [], "suggested_slot": None, "save_status":"not_saved"}
        if rule["status"] == "insufficient":
            base["risk_reasons"] = ["missing:" + x for x in rule["missing"]]; results.append(base); continue
        if rule["status"] == "risk": results.append(base); continue
        req = material.get("requested_time"); q = tools.call(state, "query_slots", {"date": material.get("date"), "requested": req, "duration": material.get("duration")})
        if not q["ok"]: base.update(review_status="blocked", risk_reasons=[q.get("error","slot_query_failed")]); results.append(base); continue
        slot = req
        if q["occupied"]:
            alternatives = [x for x in q["available"] if x != req]
            if not alternatives:
                base.update(review_status="blocked", risk_reasons=["no_available_slot"]); results.append(base); continue
            slot = alternatives[0]; base["pending_confirmation"] = ["requested_time_occupied", "confirm_alternative_slot"]
        base["suggested_slot"] = slot
        draft = {"material_id": material_id, "date": material.get("date"), "slot": slot}
        save = tools.call(state, "save_draft", {"draft": draft})
        base["save_status"] = save.get("status", "failed") if save.get("ok") else "failed"
        if not save.get("ok"): base["risk_reasons"].append(save.get("error", "save_failed"))
        base["draft_id"] = save.get("draft_id")
        results.append(base)
    complete = state.calls < state.max_calls
    return {"status":"complete" if complete else "incomplete", "results":results, "trace":state.trace, "tool_calls":state.calls}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input"); a=ap.parse_args()
    payload=json.loads(Path(a.input).read_text(encoding="utf-8") if a.input else sys.stdin.read()); print(json.dumps(run(payload), ensure_ascii=False, indent=2))
if __name__ == "__main__": main()
