"""Dashboard-level datasource dependency builders.

This module inserts `<datasources>` and `<datasource-dependencies>` blocks
required by dashboard controls (filter zones and parameter controls), ensuring
dashboard XML has the same field/parameter context expected by Tableau.
"""

from __future__ import annotations

import copy
import logging

from lxml import etree

logger = logging.getLogger(__name__)


def add_dashboard_dependencies(editor, db: etree._Element, layout_dict: dict) -> None:
    """Add dashboard-level datasources and datasource-dependencies."""
    filter_zones: list[dict] = []
    paramctrl_zones: list[dict] = []

    def _extract_zones(node: dict) -> None:
        """Collect filter/parameter-control nodes from nested layout config."""
        if node.get("type") == "filter":
            filter_zones.append(node)
        elif node.get("type") == "paramctrl":
            paramctrl_zones.append(node)
        for child in node.get("children", []):
            _extract_zones(child)

    _extract_zones(layout_dict)

    if not filter_zones and not paramctrl_zones:
        return

    ds_name = editor._datasource.get("name", "")
    db_datasources = etree.Element("datasources")

    has_params = bool(paramctrl_zones or editor._parameters)
    if has_params:
        pds = etree.SubElement(db_datasources, "datasource")
        pds.set("caption", "鍙傛暟")
        pds.set("name", "Parameters")

    if filter_zones:
        fds = etree.SubElement(db_datasources, "datasource")
        caption = editor._datasource.get("caption", ds_name)
        fds.set("caption", caption)
        fds.set("name", ds_name)

    size_el = db.find("size")
    if size_el is not None:
        size_el.addnext(db_datasources)

    if has_params:
        params_ds = None
        for ds in editor.root.findall(".//datasource"):
            if ds.get("name") == "Parameters":
                params_ds = ds
                break
        if params_ds is not None:
            param_deps = etree.Element("datasource-dependencies")
            param_deps.set("datasource", "Parameters")
            for col in params_ds.findall("column"):
                param_deps.append(copy.deepcopy(col))
            db_datasources.addnext(param_deps)

    if not filter_zones:
        return

    filter_deps = etree.Element("datasource-dependencies")
    filter_deps.set("datasource", ds_name)

    seen_cols: set[str] = set()
    seen_ci: set[str] = set()
    col_elements: list[etree._Element] = []
    ci_elements: list[etree._Element] = []

    for filter_zone in filter_zones:
        field = filter_zone.get("field")
        if not field:
            continue
        try:
            ci = editor.field_registry.parse_expression(field)
            fi = editor.field_registry._find_field(field)

            if ci.column_local_name not in seen_cols:
                seen_cols.add(ci.column_local_name)
                col_el = etree.Element("column")
                col_el.set("datatype", fi.datatype)
                col_el.set("name", fi.local_name)
                col_el.set("role", fi.role)
                col_el.set("type", fi.field_type)
                src_col = editor._datasource.find(f"column[@name='{fi.local_name}']")
                if src_col is not None and src_col.get("semantic-role"):
                    col_el.set("semantic-role", src_col.get("semantic-role"))
                col_elements.append(col_el)

            if ci.instance_name not in seen_ci:
                seen_ci.add(ci.instance_name)
                ci_el = etree.Element("column-instance")
                ci_el.set("column", ci.column_local_name)
                ci_el.set("derivation", ci.derivation)
                ci_el.set("name", ci.instance_name)
                ci_el.set("pivot", ci.pivot)
                ci_el.set("type", ci.ci_type)
                ci_elements.append(ci_el)
        except (KeyError, ValueError) as exc:
            logger.warning(
                "Failed to resolve filter field '%s' in dashboard deps: %s",
                field,
                exc,
            )

    for el in sorted(col_elements, key=lambda e: e.get("name", "")):
        filter_deps.append(el)
    for el in sorted(ci_elements, key=lambda e: e.get("name", "")):
        filter_deps.append(el)

    zones_el = db.find("zones")
    if zones_el is not None:
        zones_el.addprevious(filter_deps)
    else:
        db.append(filter_deps)
