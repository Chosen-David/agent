def measure(n):
    if type(n) is not int or n < 0: raise ValueError("nonnegative integer required")
    return sum(i*i for i in range(n))

if __name__ == "__main__":
    import json
    from pathlib import Path
    inputs = json.loads(Path("inputs.json").read_text())["n"]
    config = json.loads(Path("config.json").read_text())
    raw = [{"n": n, "repeat": r, "value": measure(n)} for r in range(config["repeats"]) for n in inputs]
    Path("raw.json").write_text(json.dumps({"samples": raw}, indent=2) + "\n")
    Path("output.json").write_text(json.dumps({"sum": sum(x["value"] for x in raw)}, indent=2) + "\n")
