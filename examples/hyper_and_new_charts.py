import sys
from pathlib import Path
from cwtwb import TWBEditor

def main():
    # Helper path assuming run from project root
    project_root = Path(__file__).parent.parent
    
    # Check if a template or a data file exists, else use standard setup
    template_path = project_root / "templates" / "twb" / "superstore.twb"
    output_path = project_root / "output" / "hyper_and_new_charts.twb"
    
    # Initialize editor
    print("Initializing Editor...")
    editor = TWBEditor(str(template_path) if template_path.exists() else None)
    
    # 1. Connect to Hyper Extract
    print("Setting Hyper Connection...")
    # Pointing to the actual .hyper file location based on user's project
    hyper_path = str(project_root / "templates" / "viz" / "Tableau Advent Calendar.twb 个文件" / "Data" / "Tableau Advent Calendar" / "Sample - EU Superstore.hyper")
    editor.set_hyper_connection(hyper_path, table_name="Orders_4A2273C4362E41DEA7258D5051022F80")

    # 2. Add New Chart Types
    print("Generating Scatterplot...")
    editor.add_worksheet("Scatterplot Example")
    editor.configure_chart(
        "Scatterplot Example", 
        mark_type="Scatterplot", 
        columns=["SUM(Sales)"], 
        rows=["SUM(Profit)"],
        color="Category",
        detail="Customer Name"
    )
    
    print("Generating Heatmap...")
    editor.add_worksheet("Heatmap Example")
    editor.configure_chart(
        "Heatmap Example", 
        mark_type="Heatmap", 
        columns=["Sub-Category"], 
        rows=["Region"],
        color="SUM(Sales)",
        label="SUM(Sales)" # Optional: show values in the heatmap
    )

    print("Generating Tree Map...")
    editor.add_worksheet("Tree Map Example")
    editor.configure_chart(
        "Tree Map Example", 
        mark_type="Tree Map", 
        size="SUM(Sales)", 
        color="SUM(Profit)",
        label="Sub-Category" # Show dimensions on the blocks
    )

    print("Generating Bubble Chart...")
    editor.add_worksheet("Bubble Chart Example")
    editor.configure_chart(
        "Bubble Chart Example", 
        mark_type="Bubble Chart", 
        size="SUM(Sales)", 
        color="Category",
        label="Category"
    )

    # 3. Add to Dashboard
    print("Creating Dashboard...")
    editor.add_dashboard(
        dashboard_name="New Advanced Charts Overview",
        worksheet_names=["Scatterplot Example", "Heatmap Example", "Tree Map Example", "Bubble Chart Example"],
        layout="grid-2x2"
    )

    # 4. Save
    output_path.parent.mkdir(exist_ok=True)
    editor.save(str(output_path))
    print(f"Successfully generated visualization to: {output_path}")
    print("You can open this .twb file with Tableau Desktop to verify the results.")

if __name__ == "__main__":
    main()
