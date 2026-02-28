"""Demo: Configure Database Connections

This script demonstrates how to configure a Tableau Workbook to connect to 
various database sources (MySQL, Tableau Server) using the cwtwb SDK.

Usage:
    python examples/demo_connections.py
"""

import sys
from pathlib import Path

# Add src to path so we can import local cwtwb
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cwtwb.twb_editor import TWBEditor

def main():
    print("=== Demo: Database Connections ===")
    
    project_root = Path(__file__).parent.parent.parent
    template_path = project_root / "templates" / "twb" / "superstore.twb"
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)
    
    print("1. Loading template...")
    # ---------------------------------------------------------
    # Example 1: MySQL Connection
    # ---------------------------------------------------------
    editor_mysql = TWBEditor(template_path)
    
    msg = editor_mysql.set_mysql_connection(
        server="127.0.0.1",
        dbname="superstore",
        username="root",
        table_name="orders",
        port="3306"
    )
    print(f"\n[MySQL] {msg}")
    
    mysql_out = output_dir / "demo_conn_mysql.twb"
    editor_mysql.save(mysql_out)
    print(f"[MySQL] Saved to {mysql_out}")

    # ---------------------------------------------------------
    # Example 2: Tableau Server Connection (Published Datasource)
    # ---------------------------------------------------------
    editor_tbs = TWBEditor(template_path)
    
    msg = editor_tbs.set_tableauserver_connection(
        server="tbs.fstyun.cn",
        dbname="data16_",
        username="",
        table_name="sqlproxy",
        directory="/dataserver",
        port="82"
    )
    print(f"\n[Tableau Server] {msg}")
    
    tbs_out = output_dir / "demo_conn_tableauserver.twb"
    editor_tbs.save(tbs_out)
    print(f"[Tableau Server] Saved to {tbs_out}")

    print("\nSuccess! You can open the generated .twb files in Tableau Desktop.")
    print("Note: You may be prompted for passwords when opening the workbooks.")

if __name__ == "__main__":
    main()
