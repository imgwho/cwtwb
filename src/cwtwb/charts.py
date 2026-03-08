"""Chart configuration mixin for TWBEditor.

Handles configure_chart and all chart-related helper methods:
filters, measure values, pie styles, shelf sorts, etc.
"""

from __future__ import annotations

import copy
import logging
import re
from dataclasses import replace as dataclass_replace
from typing import Optional, Union

from lxml import etree

from .field_registry import ColumnInstance

logger = logging.getLogger(__name__)


class ChartsMixin:
    """Mixin providing chart configuration methods for TWBEditor."""

    def configure_chart(
        self,
        worksheet_name: str,
        mark_type: str = "Automatic",
        columns: Optional[list[str]] = None,
        rows: Optional[list[str]] = None,
        color: Optional[str] = None,
        size: Optional[str] = None,
        label: Optional[str] = None,
        detail: Optional[str] = None,
        wedge_size: Optional[str] = None,
        sort_descending: Optional[str] = None,
        tooltip: Optional[Union[str, list[str]]] = None,
        filters: Optional[list[dict]] = None,
        geographic_field: Optional[str] = None,
        measure_values: Optional[list[str]] = None,
        map_fields: Optional[list[str]] = None,
    ) -> str:
        # Configure chart type and field mappings for a worksheet.
        #
        # Args:
        #     worksheet_name: Target worksheet name.
        #     mark_type: Mark type: Bar/Line/Pie/Area/Circle/Map/Automatic.
        #     columns: Column shelf expressions, e.g. ["SUM(Sales)"].
        #     rows: Row shelf expressions, e.g. ["Category"].
        #     color: Color encoding expression.
        #     size: Size encoding expression.
        #     label: Label encoding expression.
        #     detail: Detail encoding expression.
        #     wedge_size: Pie chart wedge size expression.
        #     sort_descending: Sort a dimension descending by this measure expression.
        #     tooltip: Tooltip encoding expression(s). Can be a single string or list of strings.
        #     filters: List of filter dictionaries.
        #     geographic_field: Geographic dimension for Map charts (e.g. "State/Province").
        #
        # Returns:
        #     Confirmation message.
        columns = columns or []
        rows = rows or []

        original_mark_type = mark_type
        
        # Apply simplified mark type macros
        if mark_type == "Scatterplot":
            mark_type = "Circle"
        elif mark_type == "Heatmap":
            mark_type = "Square"
            if not color and len(columns) == 0 and len(rows) == 0:
                pass # Heatmap needs color to be meaningful, but we won't strictly validate here to allow partial builds
        elif mark_type == "Tree Map":
            mark_type = "Square"
            columns = [] # Tree maps do not use columns/rows
            rows = []
        elif mark_type == "Bubble Chart":
            mark_type = "Circle"
            columns = [] # Bubble charts do not use columns/rows
            rows = []

        is_map = mark_type == "Map"
        is_mnv = bool(measure_values)  # Measure Names/Values mode

        # Find worksheet
        ws = self._find_worksheet(worksheet_name)
        table = ws.find("table")
        if table is None:
            raise ValueError(f"Worksheet '{worksheet_name}' is malformed: missing <table>")

        ds_name = self._datasource.get("name", "")

        # Collect all field expressions
        all_exprs: list[str] = []
        all_exprs.extend(columns)
        all_exprs.extend(rows)
        for enc in (color, size, label, detail, wedge_size, sort_descending):
            if enc:
                all_exprs.append(enc)
        
        if tooltip:
            if isinstance(tooltip, str):
                all_exprs.append(tooltip)
            else:
                all_exprs.extend(tooltip)
                
        if filters:
            for f in filters:
                if "column" in f:
                    all_exprs.append(f["column"])

        # For Map charts, add geographic_field to expressions
        if is_map and geographic_field:
            all_exprs.append(geographic_field)

        # For Measure Names/Values, add all measure expressions
        if is_mnv:
            for mv_expr in measure_values:
                if mv_expr not in all_exprs:
                    all_exprs.append(mv_expr)

        # Parse all expressions into ColumnInstances
        instances: dict[str, ColumnInstance] = {}
        for expr in all_exprs:
            ci = self.field_registry.parse_expression(expr)
            instances[expr] = ci
            
        # If any filter is quantitative, force its instances to use 'qk'
        if filters:
            for f in filters:
                if f.get("type") == "quantitative" and f["column"] in instances:
                    expr = f["column"]
                    ci = instances[expr]
                    # Update instance name to use 'qk' suffix if it was 'nk'
                    new_inst_name = ci.instance_name
                    if new_inst_name.endswith(":nk]"):
                        new_inst_name = new_inst_name[:-4] + ":qk]"
                    instances[expr] = dataclass_replace(ci, ci_type="quantitative", instance_name=new_inst_name)

        # 1) Set datasource-dependencies
        view = table.find("view")
        if view is None:
            raise ValueError("Malformed structure: missing <view>")

        # Remove old datasource-dependencies
        for old_dep in view.findall("datasource-dependencies"):
            view.remove(old_dep)

        deps = etree.Element("datasource-dependencies")
        deps.set("datasource", ds_name)

        # Insert deps into view (before aggregation)
        agg = view.find("aggregation")
        if agg is not None:
            agg.addprevious(deps)
        else:
            view.append(deps)

        # Collect unique columns and column-instances separately
        # Tableau expects all <column> elements before <column-instance> elements
        seen_columns: set[str] = set()
        seen_instances: set[str] = set()
        column_elements: list[etree._Element] = []
        instance_elements: list[etree._Element] = []

        for expr, ci in instances.items():
            # Collect column definitions
            if ci.column_local_name not in seen_columns:
                seen_columns.add(ci.column_local_name)
                fi = self.field_registry._find_field(
                    expr.split("(")[-1].rstrip(")").strip()
                    if "(" in expr else expr.strip()
                )
                # For calculated fields, use full column from datasource (with caption + formula)
                if fi.is_calculated:
                    # copy already imported at module level
                    src_col = self._datasource.find(f"column[@name='{fi.local_name}']")
                    if src_col is not None:
                        col_el = copy.deepcopy(src_col)
                    else:
                        col_el = etree.Element("column")
                        col_el.set("datatype", fi.datatype)
                        col_el.set("name", fi.local_name)
                        col_el.set("role", fi.role)
                        col_el.set("type", fi.field_type)
                else:
                    col_el = etree.Element("column")
                    col_el.set("datatype", fi.datatype)
                    col_el.set("name", fi.local_name)
                    col_el.set("role", fi.role)
                    col_el.set("type", fi.field_type)
                    # Copy semantic-role if present in datasource
                    src_col = self._datasource.find(f"column[@name='{fi.local_name}']")
                    if src_col is not None and src_col.get("semantic-role"):
                        col_el.set("semantic-role", src_col.get("semantic-role"))
                column_elements.append(col_el)

            # Collect column-instance definitions
            if ci.instance_name not in seen_instances:
                seen_instances.add(ci.instance_name)
                ci_el = etree.Element("column-instance")
                ci_el.set("column", ci.column_local_name)
                ci_el.set("derivation", ci.derivation)
                ci_el.set("name", ci.instance_name)
                ci_el.set("pivot", ci.pivot)
                ci_el.set("type", ci.ci_type)
                instance_elements.append(ci_el)

        # Append in order: all columns first, then all column-instances
        for el in sorted(column_elements, key=lambda e: e.get("name", "")):
            deps.append(el)
        for el in sorted(instance_elements, key=lambda e: e.get("name", "")):
            deps.append(el)

        # Fix 3: ensure raw columns referenced inside calculated-field formulas
        # are also declared in datasource-dependencies.
        # Example: {FIXED [Order ID]:SUM([Profit])}>0  →  needs [Order ID]
        #          SUM([Profit])/COUNTD([Customer Name])  →  needs [Customer Name]
        _re = re
        for col_el in list(column_elements):
            calc_el = col_el.find("calculation")
            if calc_el is None:
                continue
            formula = calc_el.get("formula", "")
            # Extract every [FieldName] token from the formula
            for ref_name in _re.findall(r"\[([^\]]+)\]", formula):
                local_ref = f"[{ref_name}]"
                # Skip if already in deps or if it looks like a parameter ref
                if local_ref in seen_columns:
                    continue
                if ref_name.startswith("Parameter ") or ref_name == "Parameters":
                    continue
                # Look up in datasource
                raw_col = self._datasource.find(f"column[@name='{local_ref}']")
                if raw_col is None:
                    # Try matching by remote-name in metadata
                    for mr in self._datasource.findall(".//metadata-record[@class='column']"):
                        rn = mr.findtext("remote-name", "")
                        if rn == ref_name:
                            ln = mr.findtext("local-name", "")
                            raw_col = self._datasource.find(f"column[@name='{ln}']")
                            if raw_col is not None:
                                local_ref = ln
                            break
                if raw_col is not None and local_ref not in seen_columns:
                    # copy already imported at module level
                    seen_columns.add(local_ref)
                    dep_col = etree.Element("column")
                    dep_col.set("datatype", raw_col.get("datatype", "string"))
                    dep_col.set("name", local_ref)
                    dep_col.set("role", raw_col.get("role", "dimension"))
                    dep_col.set("type", raw_col.get("type", "nominal"))
                    # Insert before first column-instance to maintain schema order
                    first_ci = deps.find("column-instance")
                    if first_ci is not None:
                        first_ci.addprevious(dep_col)
                    else:
                        deps.append(dep_col)

        # 2) Set mark type (Map uses Multipolygon for filled maps)
        actual_mark_type = "Multipolygon" if is_map else mark_type
        pane = table.find(".//pane")
        if pane is None:
            raise ValueError("Malformed structure: missing <pane>")

        mark_el = pane.find("mark")
        if mark_el is not None:
            mark_el.set("class", actual_mark_type)
        else:
            mark_el = etree.SubElement(pane, "mark")
            mark_el.set("class", actual_mark_type)

        # 2b) For Map charts, add mapsources to view and Parameters datasource
        if is_map:
            # Remove old mapsources if any
            for old_ms in view.findall("mapsources"):
                view.remove(old_ms)
            # Schema order: datasources → mapsources → datasource-dependencies
            mapsources = etree.Element("mapsources")
            ms = etree.SubElement(mapsources, "mapsource")
            ms.set("name", "Tableau")
            # Insert mapsources right after <datasources> in <view>
            view_ds = view.find("datasources")
            if view_ds is not None:
                view_ds.addnext(mapsources)
            else:
                view.insert(0, mapsources)

            # Add Parameters datasource reference in view if parameters exist
            if self._parameters and view_ds is not None:
                params_ds_ref = view_ds.find("datasource[@name='Parameters']")
                if params_ds_ref is None:
                    pds = etree.SubElement(view_ds, "datasource")
                    pds.set("caption", "参数")
                    pds.set("name", "Parameters")
                # Add Parameters datasource-dependencies
                self._add_parameter_deps(view)

            # Also add mapsources at workbook root if not present
            root_ms = self.root.find("mapsources")
            if root_ms is None:
                root_ms = etree.Element("mapsources")
                # Insert after datasources
                ds_el = self.root.find("datasources")
                if ds_el is not None:
                    ds_el.addnext(root_ms)
                else:
                    self.root.append(root_ms)
                rms = etree.SubElement(root_ms, "mapsource")
                rms.set("name", "Tableau")

        # 3) Set style (add special styles for Pie charts)
        table_style = table.find("style")
        if table_style is None:
            table_style = etree.SubElement(table, "style")

        if mark_type == "Pie":
            self._apply_pie_style(table_style)
        elif original_mark_type in ("Tree Map", "Bubble Chart"):
            self._apply_no_axis_style(table_style)

        # 4) Set encodings
        # Remove old encodings
        old_enc = pane.find("encodings")
        if old_enc is not None:
            pane.remove(old_enc)

        has_encodings = any(x is not None for x in (color, size, label, detail, wedge_size, tooltip, geographic_field if is_map else None))
        if has_encodings:
            encodings_el = etree.SubElement(pane, "encodings")

            if color:
                ci = instances[color]
                color_el = etree.SubElement(encodings_el, "color")
                color_el.set("column", self.field_registry.resolve_full_reference(ci.instance_name))

            if wedge_size:
                ci = instances[wedge_size]
                ws_el = etree.SubElement(encodings_el, "wedge-size")
                ws_el.set("column", self.field_registry.resolve_full_reference(ci.instance_name))

            if size:
                ci = instances[size]
                size_el = etree.SubElement(encodings_el, "size")
                size_el.set("column", self.field_registry.resolve_full_reference(ci.instance_name))

            if label:
                ci = instances[label]
                label_el = etree.SubElement(encodings_el, "text")
                label_el.set("column", self.field_registry.resolve_full_reference(ci.instance_name))

            if detail:
                ci = instances[detail]
                detail_el = etree.SubElement(encodings_el, "lod")
                detail_el.set("column", self.field_registry.resolve_full_reference(ci.instance_name))

            # For Map charts, add geographic_field as lod (detail) encoding
            if is_map and geographic_field and geographic_field != detail:
                ci = instances[geographic_field]
                geo_lod = etree.SubElement(encodings_el, "lod")
                geo_lod.set("column", self.field_registry.resolve_full_reference(ci.instance_name))

            # For Map charts, add user-specified map_fields as lod encodings
            if is_map and map_fields:
                for mf_name in map_fields:
                    try:
                        mf_ci = self.field_registry.parse_expression(mf_name)
                        mf_lod = etree.SubElement(encodings_el, "lod")
                        mf_lod.set("column", self.field_registry.resolve_full_reference(mf_ci.instance_name))
                        # Also add to deps if not already there
                        if mf_ci.column_local_name not in seen_columns:
                            seen_columns.add(mf_ci.column_local_name)
                            fi = self.field_registry._find_field(mf_name)
                            col_el = etree.Element("column")
                            col_el.set("datatype", fi.datatype)
                            col_el.set("name", fi.local_name)
                            col_el.set("role", fi.role)
                            col_el.set("type", fi.field_type)
                            deps.append(col_el)
                        if mf_ci.instance_name not in seen_instances:
                            seen_instances.add(mf_ci.instance_name)
                            ci_el = etree.Element("column-instance")
                            ci_el.set("column", mf_ci.column_local_name)
                            ci_el.set("derivation", mf_ci.derivation)
                            ci_el.set("name", mf_ci.instance_name)
                            ci_el.set("pivot", mf_ci.pivot)
                            ci_el.set("type", mf_ci.ci_type)
                            deps.append(ci_el)
                    except (KeyError, ValueError) as e:
                        logger.warning("Map field '%s' not found in registry, skipping: %s", mf_name, e)

            # For Map charts, always add Geometry encoding
            if is_map:
                geom = etree.SubElement(encodings_el, "geometry")
                geom.set("column", f"[{ds_name}].[Geometry (generated)]")

            if tooltip:
                tooltip_list = [tooltip] if isinstance(tooltip, str) else tooltip
                for tt in tooltip_list:
                    ci = instances[tt]
                    tt_el = etree.SubElement(encodings_el, "tooltip")
                    tt_el.set("column", self.field_registry.resolve_full_reference(ci.instance_name))

        # 5) Set pane style (mark labels, etc.)
        pane_style = pane.find("style")
        if pane_style is None:
            pane_style = etree.SubElement(pane, "style")
        # Ensure mark style exists
        self._ensure_mark_style(pane_style, mark_type, original_mark_type)

        # 6) Set rows and cols
        rows_el = table.find("rows")
        cols_el = table.find("cols")

        if is_map:
            # Map charts use generated Latitude/Longitude fields
            if rows_el is not None:
                rows_el.text = f"[{ds_name}].[Latitude (generated)]"
            if cols_el is not None:
                cols_el.text = f"[{ds_name}].[Longitude (generated)]"

            # Also add calculated field deps that reference parameters
            self._add_calculated_field_deps(view, ds_name, all_exprs)
        else:
            if rows_el is not None and rows:
                row_refs = []
                for expr in rows:
                    ci = instances[expr]
                    row_refs.append(self.field_registry.resolve_full_reference(ci.instance_name))
                # Tableau requires multiple row fields to use product notation:
                # (field1 * field2) — a plain space-join causes a parse error
                # ("cannot associate operator with operand").
                if len(row_refs) > 1:
                    rows_el.text = "(" + " * ".join(row_refs) + ")"
                else:
                    rows_el.text = row_refs[0]
            elif rows_el is not None:
                rows_el.text = None

            if cols_el is not None and columns:
                col_refs = []
                for expr in columns:
                    ci = instances[expr]
                    col_refs.append(self.field_registry.resolve_full_reference(ci.instance_name))
                cols_el.text = " ".join(col_refs)
            elif cols_el is not None:
                cols_el.text = None

        # 7) For Pie charts, add viewpoint/highlight in window
        if mark_type == "Pie" and color:
            self._add_viewpoint_highlight(worksheet_name, instances[color])

        # 8) Add shelf-sort if sort_descending is specified
        if sort_descending:
            self._add_shelf_sort(view, ds_name, instances, rows, sort_descending)

        # 9) Add filters if specified
        if filters:
            self._add_filters(view, instances, filters)

        # 10) Measure Names/Values mode
        if is_mnv:
            self._apply_measure_values(view, table, pane, ds_name, instances, measure_values)

        return f"Configured worksheet '{worksheet_name}' as {mark_type} chart"

    def _add_filters(
        self,
        view: etree._Element,
        instances: dict[str, "ColumnInstance"],
        filters: list[dict],
    ) -> None:
        # Add categorical filters to the worksheet view.
        #
        # Args:
        #    view: The <view> xml element.
        #    instances: Parsed column instances mapping.
        #    filters: List of filter dictionaries.
        for f in filters:
            expr = f.get("column")
            if not expr:
                continue
            values = f.get("values", [])
            ci = instances.get(expr)
            if not ci:
                continue
            
            filter_el = etree.Element("filter")
            
            # Auto-detect filter type if not explicitly provided
            filter_type = f.get("type")
            if not filter_type:
                # Based on the column instance type (qualitative vs quantitative)
                if ci.ci_type == "quantitative" or ci.instance_name.endswith(":qk]"):
                    filter_type = "quantitative"
                else:
                    filter_type = "categorical"
            
            USER_NS = "{http://www.tableausoftware.com/xml/user}"
            
            if filter_type == "quantitative":
                filter_el.set("class", "quantitative")
                filter_el.set("column", self.field_registry.resolve_full_reference(ci.instance_name))
                filter_el.set("included-values", "in-range")
                
                if "min" in f:
                    min_el = etree.SubElement(filter_el, "min")
                    min_el.text = f["min"]
                if "max" in f:
                    max_el = etree.SubElement(filter_el, "max")
                    max_el.text = f["max"]
                    
                # If neither min nor max provided for quantitative, provide a placeholder or skip min/max 
                # to represent an open/unbound range filter.
            else:
                filter_el.set("class", "categorical")
                filter_el.set("column", self.field_registry.resolve_full_reference(ci.instance_name))
                if len(values) == 1:
                    gf = etree.SubElement(filter_el, "groupfilter")
                    gf.set("function", "member")
                    gf.set("level", ci.instance_name)
                    gf.set("member", f'"{values[0]}"')
                    gf.set(f"{USER_NS}ui-domain", "database")
                    gf.set(f"{USER_NS}ui-enumeration", "inclusive")
                    gf.set(f"{USER_NS}ui-marker", "enumerate")
                elif len(values) > 1:
                    gf = etree.SubElement(filter_el, "groupfilter")
                    gf.set("function", "union")
                    gf.set(f"{USER_NS}ui-domain", "database")
                    gf.set(f"{USER_NS}ui-enumeration", "inclusive")
                    gf.set(f"{USER_NS}ui-marker", "enumerate")
                    for v in values:
                        member_el = etree.SubElement(gf, "groupfilter")
                        member_el.set("function", "member")
                        member_el.set("level", ci.instance_name)
                        member_el.set("member", f'"{v}"')
                else:
                    # Provide an empty (All values) filter with valid ui markers
                    gf = etree.SubElement(filter_el, "groupfilter")
                    gf.set("function", "level-members")
                    gf.set("level", ci.instance_name)
                    gf.set(f"{USER_NS}ui-domain", "database")
                    gf.set(f"{USER_NS}ui-enumeration", "inclusive")
                    gf.set(f"{USER_NS}ui-marker", "enumerate")
            
            # Find insertion point (must be before sort, perspectives, slices, aggregation)
            insert_before = None
            for tag in ("sort", "perspectives", "slices", "aggregation"):
                insert_before = view.find(tag)
                if insert_before is not None:
                    break
                    
            if insert_before is not None:
                insert_before.addprevious(filter_el)
            else:
                view.append(filter_el)

    def _apply_measure_values(
        self,
        view: etree._Element,
        table: etree._Element,
        pane: etree._Element,
        ds_name: str,
        instances: dict[str, "ColumnInstance"],
        measure_values: list[str],
    ) -> None:
        # Apply Measure Names/Values mode to a worksheet.
        # 
        # This enables the special Tableau pattern for KPI cards where
        # multiple measures are shown in a single text table.
        # 
        # Structure:
        #   - cols = [ds].[:Measure Names]
        #   - encoding: text = [ds].[Multiple Values] 
        #   - filter on [:Measure Names] to select which measures to show
        #   - KPI card styling (centered, bold, no grid lines)
        # 1) Set cols to [:Measure Names]
        cols_el = table.find("cols")
        if cols_el is not None:
            cols_el.text = f"[{ds_name}].[:Measure Names]"
        
        # Clear rows (KPI cards don't use rows)
        rows_el = table.find("rows")
        if rows_el is not None:
            rows_el.text = None
        
        # 2) Set text encoding to [Multiple Values]
        # Remove existing encodings and replace
        old_enc = pane.find("encodings")
        if old_enc is not None:
            pane.remove(old_enc)
        
        enc_el = etree.Element("encodings")
        text_el = etree.SubElement(enc_el, "text")
        text_el.set("column", f"[{ds_name}].[Multiple Values]")
        
        style_el = pane.find("style")
        if style_el is not None:
            style_el.addprevious(enc_el)
        else:
            pane.append(enc_el)
        
        # 3) Add [:Measure Names] filter to select specific measures
        USER_NS = "{http://www.tableausoftware.com/xml/user}"
        measure_refs = []
        for mv_expr in measure_values:
            if mv_expr in instances:
                ci = instances[mv_expr]
                full_ref = self.field_registry.resolve_full_reference(ci.instance_name)
                measure_refs.append(full_ref)
        
        if measure_refs:
            filter_el = etree.Element("filter")
            filter_el.set("class", "categorical")
            filter_el.set("column", f"[{ds_name}].[:Measure Names]")
            
            gf = etree.SubElement(filter_el, "groupfilter")
            gf.set("function", "union")
            gf.set(f"{USER_NS}ui-domain", "database")
            gf.set(f"{USER_NS}ui-enumeration", "inclusive")
            gf.set(f"{USER_NS}ui-marker", "enumerate")
            
            for ref in measure_refs:
                member = etree.SubElement(gf, "groupfilter")
                member.set("function", "member")
                member.set("level", "[:Measure Names]")
                member.set("member", f'"{ref}"')
            
            # Insert filter before sort/perspectives/slices/aggregation
            insert_before = None
            for tag in ("sort", "perspectives", "slices", "aggregation"):
                insert_before = view.find(tag)
                if insert_before is not None:
                    break
            if insert_before is not None:
                insert_before.addprevious(filter_el)
            else:
                view.append(filter_el)
        
        # 4) Apply KPI card styling
        table_style = table.find("style")
        if table_style is None:
            table_style = etree.SubElement(table, "style")
        
        # Cell style: centered, bold, larger font
        cell_rule = etree.SubElement(table_style, "style-rule")
        cell_rule.set("element", "cell")
        for attr, val in [("text-align", "center"), ("font-weight", "bold"), ("font-size", "12")]:
            fmt = etree.SubElement(cell_rule, "format")
            fmt.set("attr", attr)
            fmt.set("value", val)
        
        # Label style: centered
        label_rule = etree.SubElement(table_style, "style-rule")
        label_rule.set("element", "label")
        for attr, val in [("text-align", "center"), ("font-size", "10")]:
            fmt = etree.SubElement(label_rule, "format")
            fmt.set("attr", attr)
            fmt.set("value", val)
        
        # Table divider: hide grid lines
        div_rule = etree.SubElement(table_style, "style-rule")
        div_rule.set("element", "table-div")
        for scope in ("rows", "cols"):
            fmt = etree.SubElement(div_rule, "format")
            fmt.set("attr", "line-visibility")
            fmt.set("scope", scope)
            fmt.set("value", "off")

    def _add_calculated_field_deps(
        self,
        view: etree._Element,
        ds_name: str,
        all_exprs: list[str],
    ) -> None:
        # Add calculated field columns to datasource-dependencies when used.
        #
        # If any encoding or field expression references a calculated field,
        # that calculated field's full column definition (including formula)
        # should be included in the worksheet's datasource-dependencies.
        deps = view.find(f"datasource-dependencies[@datasource='{ds_name}']")
        if deps is None:
            return
        
        # Check each calculated field in the registry
        for fi_name, fi in self.field_registry._fields.items():
            if not fi.is_calculated:
                continue
            # Check if any expression uses this calculated field
            # by checking if its column-instance already exists in deps
            existing = deps.find(f"column-instance[@column='{fi.local_name}']")
            if existing is not None:
                # Column-instance exists; make sure column definition is also there
                existing_col = deps.find(f"column[@name='{fi.local_name}']")
                if existing_col is None:
                    # Need to add the calculated column with its formula
                    src_col = self._datasource.find(f"column[@name='{fi.local_name}']")
                    if src_col is not None:
                        import copy
                        col_copy = copy.deepcopy(src_col)
                        # Insert before column-instances
                        first_ci = deps.find("column-instance")
                        if first_ci is not None:
                            first_ci.addprevious(col_copy)
                        else:
                            deps.append(col_copy)

    def _add_shelf_sort(
        self,
        view: etree._Element,
        ds_name: str,
        instances: dict[str, "ColumnInstance"],
        rows: list[str],
        sort_measure_expr: str,
    ) -> None:
        # Add shelf-sort for descending sort on a dimension by a measure.
        #
        # Generates <shelf-sorts><shelf-sort-v2 .../></shelf-sorts> in <view>.
        # Auto-detects the dimension from rows (first dimension found).
        # Also adds required manifest entries (IntuitiveSorting).
        # Find the dimension to sort (first dimension in rows)
        dim_ci = None
        for expr in rows:
            ci = instances.get(expr)
            if ci and ci.ci_type == "nominal":
                dim_ci = ci
                break
        if dim_ci is None:
            return

        measure_ci = instances.get(sort_measure_expr)
        if measure_ci is None:
            return

        # Ensure manifest entries exist for shelf-sorts support
        self._ensure_manifest_entry("IntuitiveSorting")
        self._ensure_manifest_entry("IntuitiveSorting_SP2")

        # Remove old shelf-sorts
        for old_ss in view.findall("shelf-sorts"):
            view.remove(old_ss)

        shelf_sorts = etree.Element("shelf-sorts")

        sort_v2 = etree.SubElement(shelf_sorts, "shelf-sort-v2")
        sort_v2.set("dimension-to-sort",
                     self.field_registry.resolve_full_reference(dim_ci.instance_name))
        sort_v2.set("direction", "DESC")
        sort_v2.set("is-on-innermost-dimension", "true")
        sort_v2.set("measure-to-sort-by",
                     self.field_registry.resolve_full_reference(measure_ci.instance_name))
        sort_v2.set("shelf", "rows")

        # Insert before <aggregation> (schema: ...shelf-sorts, slices?, aggregation)
        agg = view.find("aggregation")
        if agg is not None:
            agg.addprevious(shelf_sorts)
        else:
            view.append(shelf_sorts)

    def _ensure_manifest_entry(self, entry_name: str) -> None:
        # Ensure a <document-format-change-manifest> entry exists.
        manifest = self.root.find("document-format-change-manifest")
        if manifest is None:
            manifest = etree.SubElement(self.root, "document-format-change-manifest")
        if manifest.find(entry_name) is None:
            etree.SubElement(manifest, entry_name)

    def _apply_pie_style(self, table_style: etree._Element) -> None:
        # Add special style rules for Pie charts.
        # Axis line-visibility off
        axis_rule = etree.SubElement(table_style, "style-rule")
        axis_rule.set("element", "axis")
        fmt = etree.SubElement(axis_rule, "format")
        fmt.set("attr", "line-visibility")
        fmt.set("value", "off")

        # Worksheet: hide field labels
        ws_rule = etree.SubElement(table_style, "style-rule")
        ws_rule.set("element", "worksheet")
        for scope in ("cols", "rows"):
            fmt = etree.SubElement(ws_rule, "format")
            fmt.set("attr", "display-field-labels")
            fmt.set("scope", scope)
            fmt.set("value", "false")

        # Zeroline off
        zl_rule = etree.SubElement(table_style, "style-rule")
        zl_rule.set("element", "zeroline")
        fmt = etree.SubElement(zl_rule, "format")
        fmt.set("attr", "line-visibility")
        fmt.set("value", "off")

    def _apply_no_axis_style(self, table_style: etree._Element) -> None:
        # Add special style rules for charts that shouldn't show axes (e.g. Tree Map, Bubble Chart).
        # Worksheet: hide field labels
        ws_rule = etree.SubElement(table_style, "style-rule")
        ws_rule.set("element", "worksheet")
        for scope in ("cols", "rows"):
            fmt = etree.SubElement(ws_rule, "format")
            fmt.set("attr", "display-field-labels")
            fmt.set("scope", scope)
            fmt.set("value", "false")

    def _ensure_mark_style(self, pane_style: etree._Element, mark_type: str, original_mark_type: str = None) -> None:
        # Ensure mark style rule exists in the pane.
        # Check if mark style-rule already exists
        for sr in pane_style.findall("style-rule"):
            if sr.get("element") == "mark":
                return  # Already present

        sr = etree.SubElement(pane_style, "style-rule")
        sr.set("element", "mark")

        # Use original_mark_type for styling logic if provided, otherwise mark_type
        style_mark_type = original_mark_type or mark_type

        if style_mark_type == "Pie":
            # Set pie size
            fmt = etree.SubElement(sr, "format")
            fmt.set("attr", "size")
            fmt.set("value", "1.8")
        elif style_mark_type in ("Tree Map", "Bubble Chart"):
            fmt = etree.SubElement(sr, "format")
            fmt.set("attr", "size")
            fmt.set("value", "2")

        # Show labels
        fmt = etree.SubElement(sr, "format")
        fmt.set("attr", "mark-labels-show")
        fmt.set("value", "true")

        fmt = etree.SubElement(sr, "format")
        fmt.set("attr", "mark-labels-cull")
        fmt.set("value", "true")

    def _add_viewpoint_highlight(
        self, worksheet_name: str, color_ci: ColumnInstance
    ) -> None:
        # Add viewpoint/highlight for Pie chart color encoding.
        #
        # The viewpoint is inserted before simple-id, matching Tableau Desktop structure.
        windows = self.root.find("windows")
        if windows is None:
            return

        for window in windows.findall("window"):
            if window.get("name") == worksheet_name:
                # Remove old viewpoint
                old_vp = window.find("viewpoint")
                if old_vp is not None:
                    window.remove(old_vp)

                vp = etree.Element("viewpoint")
                highlight = etree.SubElement(vp, "highlight")
                cow = etree.SubElement(highlight, "color-one-way")
                field_el = etree.SubElement(cow, "field")
                field_el.text = self.field_registry.resolve_full_reference(
                    color_ci.instance_name
                )

                # Insert before simple-id
                simple_id = window.find("simple-id")
                if simple_id is not None:
                    simple_id.addprevious(vp)
                else:
                    window.append(vp)
                break

