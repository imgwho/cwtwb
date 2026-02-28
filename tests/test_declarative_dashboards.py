import pytest
from pathlib import Path
from lxml import etree
import shutil

from cwtwb.twb_editor import TWBEditor


@pytest.fixture
def tmp_superstore(tmp_path):
    src = Path(__file__).parent.parent / "templates" / "twb" / "superstore.twb"
    dst = tmp_path / "superstore_tmp.twb"
    shutil.copy(src, dst)
    return dst


def test_declarative_json_dashboard(tmp_superstore, tmp_path):
    """Test generating a dashboard with extremely complex declarative nesting."""
    editor = TWBEditor(tmp_superstore)
    editor.clear_worksheets()
    
    # Generate mock worksheets
    charts = ["D_Sales", "D_Profit", "D_Discount", "D_Quantity", "Main Chart", "Line Trend"]
    for c in charts:
        editor.add_worksheet(c)
        editor.configure_chart(c, mark_type="Bar", rows=["ship_mode"], columns=["SUM(sales)"])
        
    # Extremely complex layout matching (similar to c.2 replica)
    layout = {
        "type": "container",
        "direction": "vertical",
        "children": [
            {
                "type": "container",
                "direction": "horizontal",
                "fixed_size": 100,
                "style": {"bg_color": "#ff0000"},
                "children": [
                    {"type": "text", "text": "MY AWESOME DASHBOARD", "font_size": "24", "bold": True, "fixed_size": 300},
                    {"type": "text", "text": "Logo Area", "weight": 1}
                ]
            },
            {
                "type": "container",
                "direction": "horizontal",
                "weight": 1,
                "children": [
                    {
                        "type": "container",
                        "direction": "vertical",
                        "fixed_size": 250,
                        "layout_strategy": "distribute-evenly",
                        "children": [
                            {"type": "worksheet", "name": "D_Sales"},
                            {"type": "worksheet", "name": "D_Profit"},
                            {"type": "worksheet", "name": "D_Discount"},
                            {"type": "worksheet", "name": "D_Quantity"},
                        ]
                    },
                    {
                        "type": "container",
                        "direction": "vertical",
                        "weight": 2,
                        "children": [
                            {"type": "worksheet", "name": "Main Chart", "weight": 2},
                            {"type": "worksheet", "name": "Line Trend", "weight": 1}
                        ]
                    }
                ]
            }
        ]
    }
    
    # 3. Add Dashboard
    msg = editor.add_dashboard(
        "Complex JSON Dash", 
        width=1400, 
        height=900, 
        layout=layout,
        worksheet_names=charts # Pass for validation
    )
    
    assert "Created dashboard 'Complex JSON Dash'" in msg
    
    # Check tree directly for generated XML structures
    db = editor.root.find(".//dashboards/dashboard[@name='Complex JSON Dash']")
    assert db is not None
    
    # Check that sizing-mode="fixed" is applied
    size_el = db.find("size")
    assert size_el is not None
    assert size_el.get("sizing-mode") == "fixed"
    
    zones = db.find("zones")
    assert zones is not None
    
    # The wrapper's child zone should be vertically oriented
    root_zone = zones.find("zone")
    assert root_zone.get("param") == "vert"
    
    # It should have exactly two horizontal children inside
    child_zones = list(root_zone.findall("zone"))
    assert len(child_zones) == 2
    assert child_zones[0].get("param") == "horz"
    assert child_zones[1].get("param") == "horz"
    
    # Check height absolute proportion logic (Top header is fixed 100px of 900px, 11% -> 11111 height)
    h_top = int(child_zones[0].get("h"))
    h_remaining = int(child_zones[1].get("h"))
    assert h_top > 10000 and h_top < 12000 # ~11%
    assert h_remaining > 88000 and h_remaining < 89000 # ~89%
    
    # Optional: Save and print location for manual visual sanity check
    out_path = tmp_path / "test_nested_dashboard.twb"
    editor.save(out_path)
    print(f"\\nSaved declarative Layout TWB to {out_path}")


def test_fallback_basic_layouts(tmp_superstore):
    """Test that classic simple string layout still generates correct JSON internally."""
    editor = TWBEditor(tmp_superstore)
    editor.clear_worksheets()
    
    editor.add_worksheet("S1")
    editor.add_worksheet("S2")
    
    # Test built in horizontal
    editor.add_dashboard("Dash Horz", layout="horizontal", worksheet_names=["S1", "S2"])
    db_h = editor.root.find(".//dashboards/dashboard[@name='Dash Horz']")
    rz_h = db_h.find("zones/zone")
    assert rz_h.get("param") == "horz"
    assert len(list(rz_h.findall("zone"))) == 2
    
    # Test built in vertical
    editor.add_dashboard("Dash Vert", layout="vertical", worksheet_names=["S1", "S2"])
    db_v = editor.root.find(".//dashboards/dashboard[@name='Dash Vert']")
    rz_v = db_v.find("zones/zone")
    assert rz_v.get("param") == "vert"
    assert len(list(rz_v.findall("zone"))) == 2
