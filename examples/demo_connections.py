import sys
from pathlib import Path

# Add src to sys.path so we can import cwtwb without installing it
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cwtwb.twb_editor import TWBEditor

def main():
    project_root = Path(__file__).parent.parent
    template_path = project_root / "templates" / "twb" / "superstore.twb"
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    print("=== Test 1: Generate TWB with Local MySQL Connection ===")
    editor_mysql = TWBEditor(template_path)
    
    # Set connection information
    msg1 = editor_mysql.set_mysql_connection(
        server="127.0.0.1",
        dbname="superstore",
        username="root",
        table_name="orders",
        port="3306"
    )
    print(msg1)
    
    # Add a simple worksheet to verify if the connection correctly binds to the chart
    editor_mysql.add_worksheet("Test Sheet")
    editor_mysql.configure_chart("Test Sheet", mark_type="Bar", rows=["ship_mode"], columns=["SUM(sales)"])
    
    out_mysql = output_dir / "demo_mysql.twb"
    print(editor_mysql.save(out_mysql))


    print("\n=== Test 2: Generate TWB with Tableau Server Connection ===")
    editor_tbs = TWBEditor(template_path)
    
    # Set connection information
    msg2 = editor_tbs.set_tableauserver_connection(
        server="tbs.fstyun.cn",
        dbname="data16_",
        username="",
        table_name="sqlproxy",
        directory="/dataserver",
        port="82"
    )
    print(msg2)
    
    # Add a simple worksheet to verify if the connection correctly binds to the chart
    editor_tbs.add_worksheet("Test Server Sheet")
    editor_tbs.configure_chart("Test Server Sheet", mark_type="Bar", rows=["省"], columns=["SUM(订单营业额)"])
    
    out_tbs = output_dir / "demo_tableauserver.twb"
    print(editor_tbs.save(out_tbs))
    
    print("\n=== Verification Guide ===")
    print(f"1. Open {out_mysql} with Tableau Desktop")
    print("   -> Expected behavior: Tableau will attempt to connect to your local 127.0.0.1:3306 database.")
    print(f"2. Open {out_tbs} with Tableau Desktop")
    print("   -> Expected behavior: Tableau will attempt to authenticate with tbs.fstyun.cn server datasource.")

if __name__ == "__main__":
    main()
