"""测试脚本：从 template.twb 生成饼图 TWB。

用法：python tests/test_generate_pie.py
生成：output/pie_test.twb

验证方式：用 Tableau Desktop 打开 output/pie_test.twb，
应显示按 Segment 分色、以 SUM(Sales) 为扇区大小的饼图。
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cwtwb.twb_editor import TWBEditor


def main():
    project_root = Path(__file__).parent.parent
    template_path = project_root / "templates" / "superstore.twb"
    output_path = project_root / "output" / "pie_test.twb"

    print(f"template: {template_path}")
    print(f"output:   {output_path}")
    print()

    # 1. 从模板创建编辑器
    editor = TWBEditor(template_path)
    print("[OK] loaded template")

    # 2. 列出字段
    fields_info = editor.list_fields()
    print(fields_info)
    print()

    # 3. 清空模板中的工作表
    editor.clear_worksheets()
    print("[OK] cleared worksheets")

    # 4. 添加饼图工作表
    result = editor.add_worksheet("pie_test")
    print(f"[OK] {result}")

    # 5. 配置饼图
    result = editor.configure_chart(
        worksheet_name="pie_test",
        mark_type="Pie",
        color="Segment",
        wedge_size="SUM(Sales)",
    )
    print(f"[OK] {result}")

    # 6. 保存
    result = editor.save(output_path)
    print(f"[OK] {result}")

    print()
    print("DONE! Open output/pie_test.twb with Tableau Desktop to verify.")


if __name__ == "__main__":
    main()
