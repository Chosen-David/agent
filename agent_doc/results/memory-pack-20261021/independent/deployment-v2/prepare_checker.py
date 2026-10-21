"""Reuse the independent oracle implementation, with new bound inputs/outputs."""
from pathlib import Path
RUN=Path(__file__).resolve().parent
s=(RUN.parent/'check_payloads.py').read_text(encoding='utf-8')
s=s.replace('parents[2]','parents[3]')
s=s.replace("SOURCE=ROOT/'agent_doc/results/memory-pack-20261021'","SOURCE=ROOT/'agent_doc/results/memory-pack-20261021/deployment-v2'")
s=s.replace('rerun-v1/','rerun-v2/').replace("load(SOURCE/'config.json')","load(SOURCE.parent/'config.json')")
start=s.index("properties=load(RUN/'properties-v1.json')")
end=s.index("manifest=load(SOURCE/'manifest.json')",start)
s=s[:start]+s[end:]
s=s.replace("require(dump(producer['cases'])==dump(rerun['cases']),'six deterministic case outputs did not reproduce exactly')",
            "require(dump(producer['cases'])==dump(rerun['cases'])==dump(load(SOURCE.parent/'raw.json')['cases']),'six deterministic case outputs differ from rerun or retained v1')")
s=s.replace("'payload-checks-v1.json'","'payload-checks-v2.json'")
(RUN/'check_payloads.py').write_text(s,encoding='utf-8')
