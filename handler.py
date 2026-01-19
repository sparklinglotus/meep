import subprocess, tempfile, base64, zipfile
from pathlib import Path
import runpod

def handler(job):
    inp = job.get("input", {})
    script_b64 = inp.get("python_script_b64", "")
    if not script_b64:
        return {"ok": False, "error": "python_script_b64 missing"}

    work = Path(tempfile.mkdtemp(prefix="meep_"))
    script = work / "run.py"
    script.write_bytes(base64.b64decode(script_b64))

    p = subprocess.run(["python3", "run.py"], cwd=str(work), capture_output=True, text=True)

    zpath = work / "out.zip"
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in work.rglob("*"):
            if f.is_file() and f.name != "out.zip":
                zf.write(f, arcname=str(f.relative_to(work)))

    return {
        "ok": True,
        "returncode": p.returncode,
        "stdout": (p.stdout or "")[-12000:],
        "stderr": (p.stderr or "")[-12000:],
        "zip_b64": base64.b64encode(zpath.read_bytes()).decode("ascii"),
    }

runpod.serverless.start({"handler": handler})
