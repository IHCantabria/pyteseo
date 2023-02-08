import json
import pyteseo
from pathlib import Path


def import_local(substance_type: str, substance_name: str) -> dict:
    substance_type = substance_type.lower()

    if substance_type not in ["oil", "hns"]:
        raise ValueError("Invalid substance_type")
    package_path = Path(pyteseo.__file__).parent
    path = Path(
        package_path, "data", "substances", substance_type, f"{substance_name}.json"
    )
    with open(path) as f:
        return json.loads(f.read())
