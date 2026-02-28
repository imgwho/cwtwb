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

    print("=== 测试 1: 生成 Local MySQL 连接的 TWB ===")
    editor_mysql = TWBEditor(template_path)
    
    # 设置连接信息
    msg1 = editor_mysql.set_mysql_connection(
        server="127.0.0.1",
        dbname="superstore",
        username="root",
        table_name="orders",
        port="3306"
    )
    print(msg1)
    
    # 添加一个简单的工作表以验证连接是否真的被绑定到了图表
    editor_mysql.add_worksheet("Test Sheet")
    editor_mysql.configure_chart("Test Sheet", mark_type="Bar", rows=["Category"], columns=["SUM(Sales)"])
    
    out_mysql = output_dir / "demo_mysql.twb"
    print(editor_mysql.save(out_mysql))


    print("\n=== 测试 2: 生成 Tableau Server 连接的 TWB ===")
    editor_tbs = TWBEditor(template_path)
    
    # 设置连接信息
    msg2 = editor_tbs.set_tableauserver_connection(
        server="tbs.fstyun.cn",
        dbname="data16_",
        username="",
        table_name="sqlproxy",
        directory="/dataserver",
        port="82"
    )
    print(msg2)
    
    out_tbs = output_dir / "demo_tableauserver.twb"
    print(editor_tbs.save(out_tbs))
    
    print("\n=== 验证指引 ===")
    print(f"1. 请使用 Tableau Desktop 打开 {out_mysql}")
    print("   -> 预期表现：Tableau 会尝试连接到你的本地 127.0.0.1:3306 数据库 (如果是密码错误，会弹出输入密码的提示框，说明连接参数已生效)。")
    print(f"2. 请使用 Tableau Desktop 打开 {out_tbs}")
    print("   -> 预期表现：Tableau 会尝试登录到 tbs.fstyun.cn 验证数据源。")

if __name__ == "__main__":
    main()
