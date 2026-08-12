#!/usr/bin/env python3
"""Generate a minimal CycloneDX 1.5 SBOM for prism-eval releases."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def main(out_path: str = "sbom.cdx.json") -> None:
    try:
        ver = version("prism-eval")
    except PackageNotFoundError:
        import prism_eval

        ver = getattr(prism_eval, "__version__", "0.0.0")

    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": {
                "type": "library",
                "name": "prism-eval",
                "version": ver,
                "bom-ref": f"pkg:pypi/prism-eval@{ver}",
                "licenses": [{"license": {"id": "Apache-2.0"}}],
            },
        },
        "components": [
            {
                "type": "library",
                "name": "pydantic",
                "bom-ref": "pkg:pypi/pydantic",
                "purl": "pkg:pypi/pydantic",
            }
        ],
    }
    Path(out_path).write_text(json.dumps(bom, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sbom.cdx.json")
