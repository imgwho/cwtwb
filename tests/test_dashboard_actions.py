import unittest
from pathlib import Path
from lxml import etree
from cwtwb.twb_editor import TWBEditor

class TestDashboardActions(unittest.TestCase):
    def setUp(self):
        template_path = Path(__file__).parent.parent / "templates" / "twb" / "superstore.twb"
        self.editor = TWBEditor(template_path)
        
    def test_filter_action(self):
        # 1. Setup worksheets
        self.editor.add_worksheet("SourceMap")
        self.editor.configure_chart("SourceMap", mark_type="Circle", columns=["SUM(Sales)"], rows=["State"])
        
        self.editor.add_worksheet("TargetBar")
        self.editor.configure_chart("TargetBar", mark_type="Bar", columns=["SUM(Profit)"], rows=["Category"])
        
        # 2. Setup dashboard
        self.editor.add_dashboard("ActionTestDash", worksheet_names=["SourceMap", "TargetBar"])
        
        # 3. Add action
        msg = self.editor.add_dashboard_action(
            dashboard_name="ActionTestDash",
            action_type="filter",
            source_sheet="SourceMap",
            target_sheet="TargetBar",
            fields=["State"],
            event_type="on-select",
        )
        self.assertIn("Added filter action", msg)
        
        # 4. Verify XML
        actions_el = self.editor.root.find("actions")
        self.assertIsNotNone(actions_el)
        
        action_el = actions_el.find("action")
        self.assertIsNotNone(action_el)
        self.assertTrue(action_el.get("name").startswith("[Action"))
        
        source_el = action_el.find("source")
        self.assertIsNotNone(source_el)
        self.assertEqual(source_el.get("dashboard"), "ActionTestDash")
        self.assertEqual(source_el.get("worksheet"), "SourceMap")
        
        link_el = action_el.find("link")
        self.assertIsNotNone(link_el)
        self.assertTrue("~s0=" in link_el.get("expression"))
        
        cmd_el = action_el.find("command")
        self.assertIsNotNone(cmd_el)
        self.assertEqual(cmd_el.get("command"), "tsc:tsl-filter")
        
        params = cmd_el.findall("param")
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].get("name"), "target")
        self.assertEqual(params[0].get("value"), "TargetBar")

if __name__ == "__main__":
    unittest.main()
