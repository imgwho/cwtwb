"""Dashboard action XML helpers for filter and highlight interactions.

This module builds `<action>` blocks and command payloads used by Tableau
dashboards to wire cross-sheet interactions. It keeps action XML assembly
separate from dashboard layout code so MCP tools can expose a focused API.
"""

from __future__ import annotations

from urllib.parse import quote

from lxml import etree


def add_dashboard_action(
    editor,
    dashboard_name: str,
    action_type: str,
    source_sheet: str,
    target_sheet: str,
    fields: list[str],
    event_type: str = "on-select",
    caption: str = "",
) -> str:
    """Add an interaction action to a dashboard."""
    if action_type not in ("filter", "highlight"):
        raise ValueError(
            f"Unsupported action_type '{action_type}'. Use 'filter' or 'highlight'."
        )

    db_el = editor.root.find(f".//dashboards/dashboard[@name='{dashboard_name}']")
    if db_el is None:
        raise ValueError(f"Dashboard '{dashboard_name}' not found.")

    editor._find_worksheet(source_sheet)
    editor._find_worksheet(target_sheet)

    actions_el = editor.root.find("actions")
    if actions_el is None:
        actions_el = etree.Element("actions")
        insert_before = None
        for tag in ("worksheets", "dashboards", "windows"):
            insert_before = editor.root.find(tag)
            if insert_before is not None:
                break

        if insert_before is not None:
            insert_before.addprevious(actions_el)
        else:
            editor.root.append(actions_el)

    action_el = etree.Element(
        "action",
        nsmap={"user": "http://www.tableausoftware.com/xml/user"},
    )
    first_blocker = actions_el.find("datasources")
    if first_blocker is None:
        first_blocker = actions_el.find("datasource-dependencies")
    if first_blocker is not None:
        first_blocker.addprevious(action_el)
    else:
        actions_el.append(action_el)

    action_caption = caption or f"{action_type.capitalize()} Action {len(actions_el)}"
    action_el.set("caption", action_caption)
    action_el.set("name", f"[Action{len(actions_el)}]")

    activation_el = etree.SubElement(action_el, "activation")
    activation_el.set("auto-clear", "true")
    activation_el.set("type", event_type if event_type != "on-select" else "on-select")

    source_el = etree.SubElement(action_el, "source")
    source_el.set("dashboard", dashboard_name)
    source_el.set("type", "sheet")
    if source_sheet:
        source_el.set("worksheet", source_sheet)

    zones_el = db_el.find("zones")
    all_sheets: list[str] = []
    if zones_el is not None:
        for zone in zones_el.findall(".//zone"):
            ws_name = zone.get("name")
            if ws_name and ws_name not in all_sheets:
                all_sheets.append(ws_name)

    exclude_sheets = [sheet for sheet in all_sheets if sheet != target_sheet]

    if action_type == "filter":
        _configure_filter_action(
            editor,
            action_el,
            dashboard_name,
            action_caption,
            fields,
            exclude_sheets,
        )
    else:
        _configure_highlight_action(
            action_el,
            dashboard_name,
            fields,
            exclude_sheets,
        )

    return f"Added {action_type} action '{action_caption}' to '{dashboard_name}'"


def _configure_filter_action(
    editor,
    action_el: etree._Element,
    dashboard_name: str,
    action_caption: str,
    fields: list[str],
    exclude_sheets: list[str],
) -> None:
    """Populate XML for a filter action, including link payload and command params."""
    if fields:
        ds_name = editor._datasource.get("name", "")
        link_el = etree.SubElement(action_el, "link")
        link_el.set("caption", action_caption)
        link_el.set("delimiter", ",")
        link_el.set("escape", "\\")

        field_expressions = []
        for field in fields:
            ci = editor.field_registry.parse_expression(field)
            col_name = ci.column_local_name
            encoded_ds = quote(f"[{ds_name}]")
            encoded_col = quote(col_name)
            field_expressions.append(
                f"{encoded_ds}.{encoded_col}~s0=<{col_name}~na>"
            )

        expr_str = f"tsl:{dashboard_name}?" + "&".join(field_expressions)
        link_el.set("expression", expr_str)
        link_el.set("include-null", "true")
        link_el.set("multi-select", "true")
        link_el.set("url-escape", "true")

    cmd_el = etree.SubElement(action_el, "command")
    cmd_el.set("command", "tsc:tsl-filter")

    if exclude_sheets:
        param_ex = etree.SubElement(cmd_el, "param")
        param_ex.set("name", "exclude")
        param_ex.set("value", ",".join(exclude_sheets))

    if not fields:
        param_sp = etree.SubElement(cmd_el, "param")
        param_sp.set("name", "special-fields")
        param_sp.set("value", "all")

    param_tgt = etree.SubElement(cmd_el, "param")
    param_tgt.set("name", "target")
    param_tgt.set("value", dashboard_name)


def _configure_highlight_action(
    action_el: etree._Element,
    dashboard_name: str,
    fields: list[str],
    exclude_sheets: list[str],
) -> None:
    """Populate XML for a highlight action command block."""
    cmd_el = etree.SubElement(action_el, "command")
    cmd_el.set("command", "tsc:brush")

    if exclude_sheets:
        param_ex = etree.SubElement(cmd_el, "param")
        param_ex.set("name", "exclude")
        param_ex.set("value", ",".join(exclude_sheets))

    if not fields:
        param_sp = etree.SubElement(cmd_el, "param")
        param_sp.set("name", "special-fields")
        param_sp.set("value", "all")
    else:
        param_fields = etree.SubElement(cmd_el, "param")
        param_fields.set("name", "field-captions")
        param_fields.set("value", ",".join(fields))

    param_tgt = etree.SubElement(cmd_el, "param")
    param_tgt.set("name", "target")
    param_tgt.set("value", dashboard_name)
