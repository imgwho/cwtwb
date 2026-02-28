import sys
import os
from pathlib import Path

# Add src to path so we can import local cwtwb
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from cwtwb.twb_editor import TWBEditor

def main():
    print("=== Demo: Declarative JSON Dashboard Layout ===")

    template_path = Path(__file__).parent.parent / "templates" / "twb" / "superstore.twb"
    output_path = Path(__file__).parent.parent / "output" / "demo_declarative_dash.twb"
    
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        return

    print("1. Loading template...")
    editor = TWBEditor(template_path)
    editor.clear_worksheets()

    print("2. Generating some mock worksheets...")
    # Creating some simple charts to fill the layout
    charts = ["Sales By Category", "Profit Map", "Discount Trend", "Daily Highlights"]
    for i, name in enumerate(charts):
        editor.add_worksheet(name)
        # Just simple bar chart configs to ensure they are valid
        editor.configure_chart(name, mark_type="Bar", rows=["ship_mode"], columns=["SUM(sales)"])
        print(f"   - Added Worksheet: {name}")

    print("3. Building Complex Declarative Layout (JSON/Dict)...")
    # This JSON represents a complex, multi-level nested dashboard layout inspired by Figma Auto-Layout
    layout_schema = {
        "type": "container",
        "direction": "vertical",     # Root container is vertical
        "children": [
            {
                # TOP ROW: Fixed height of 100px (like a header/navbar)
                "type": "container",
                "direction": "horizontal",
                "fixed_size": 100,
                "style": {"background_color": "#182b3a"}, # Dark blue background
                "children": [
                    {
                        "type": "text", 
                        "text": "MY DECLARATIVE EXECUTIVE DASHBOARD", 
                        "font_size": "24", 
                        "font_color": "#ffffff",
                        "bold": True, 
                        "fixed_size": 800  # Title takes up left 800px exactly
                    },
                    {
                        "type": "text", 
                        "text": "Powered by cwtwb JSON Engine", 
                        "font_color": "#aaaaaa",
                        "weight": 1        # Takes up remaining flexible space
                    }
                ]
            },
            {
                # MAIN CONTENT: Remaining vertical space
                "type": "container",
                "direction": "horizontal",
                "weight": 1, 
                "children": [
                    {
                        # LEFT SIDEBAR: 300px Fixed Width Menu / Detail Zone
                        "type": "container",
                        "direction": "vertical",
                        "fixed_size": 300,
                        "layout_strategy": "distribute-evenly",
                        "style": {"background_color": "#f3f3f3"},
                        "children": [
                            {"type": "worksheet", "name": "Daily Highlights"}
                        ]
                    },
                    {
                        # RIGHT CONTENT AREA: Flexible Width (weight=2)
                        "type": "container",
                        "direction": "vertical",
                        "weight": 2,
                        "children": [
                            {
                                # Top half of content area: Spread 2 charts evenly
                                "type": "container",
                                "direction": "horizontal",
                                "weight": 1,
                                "layout_strategy": "distribute-evenly",
                                "children": [
                                    {"type": "worksheet", "name": "Sales By Category"},
                                    {"type": "worksheet", "name": "Discount Trend"},
                                ]
                            },
                            {
                                # Bottom half: Large Map chart (gets more height weight)
                                "type": "worksheet", 
                                "name": "Profit Map", 
                                "weight": 2 
                            }
                        ]
                    }
                ]
            }
        ]
    }

    print("4. Applying the layout to Dashboard Canvas...")
    editor.add_dashboard(
        dashboard_name="Executive Summary",
        width=1400,
        height=900,
        layout=layout_schema,
        worksheet_names=charts # Needed for internal registry tracking
    )

    print(f"5. Saving workbook to: {output_path}")
    editor.save(output_path)
    
    print("\nSuccess! Open the file above in Tableau Desktop, and inspect the 'Executive Summary' Dashboard.")
    print("   You should see:")
    print("   - A fixed 100px dark-blue top title bar")
    print("   - A fixed 300px left light-grey sidebar")
    print("   - A right content area flexibly split into 2 horizontal charts on top, and 1 large chart on bottom.")

if __name__ == "__main__":
    main()
