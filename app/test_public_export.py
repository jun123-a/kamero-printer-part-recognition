import json
import unittest
from pathlib import Path
from export_public_catalog import export


class PublicExportTests(unittest.TestCase):
    def test_export_contains_only_parts(self):
        export()
        root = Path(__file__).resolve().parent.parent
        data = json.loads((root / "docs/catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual(set(data), {"parts"})
        self.assertEqual(len(data["parts"]), 31)
        for part in data["parts"]:
            self.assertEqual(set(part), {"part_no", "svc_number", "description"})
        text = json.dumps(data)
        self.assertNotIn("drive.google.com", text)
        self.assertNotIn(".mp4", text)
