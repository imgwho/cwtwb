"""TWB XML Editor — manipulate Tableau Workbook XML trees with lxml.

Core capabilities:
- Load and parse fields from a TWB template
- Add/remove calculated fields
- Add/configure worksheets (multiple chart types)
- Create dashboards with layout-flow zone structure
- Serialize and save TWB files
"""

from __future__ import annotations

import copy
import uuid
from pathlib import Path
from typing import Optional

from lxml import etree

from .field_registry import ColumnInstance, FieldRegistry


def _generate_uuid() -> str:
    """Generate an uppercase UUID string: {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}."""
    return "{" + str(uuid.uuid4()).upper() + "}"


class TWBEditor:
    """lxml-based TWB XML editor."""

    def __init__(self, template_path: str | Path):
        template_path = Path(template_path)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        # Parse with XMLParser to preserve original formatting
        parser = etree.XMLParser(remove_blank_text=False)
        self.tree = etree.parse(str(template_path), parser)
        self.root = self.tree.getroot()
        self.template_path = template_path

        # Parse datasource
        self._datasource = self._get_datasource()
        ds_name = self._datasource.get("name", "")
        self.field_registry = FieldRegistry(ds_name)

        # Zone ID counter (used by dashboards)
        self._zone_id_counter = 2

        # Initialize field registry corresponding to metadata
        self._init_fields()

        # Clear out default worksheets/dashboards to avoid ghost fields
        self.clear_worksheets()

    # ================================================================
    # Initialization
    # ================================================================

    def _get_datasource(self) -> etree._Element:
        """Get the first datasource element."""
        ds_list = self.root.findall(".//datasources/datasource")
        if not ds_list:
            raise ValueError("No datasource found in template")
        return ds_list[0]

    def _init_fields(self) -> None:
        """Parse field info from metadata-records and column definitions."""
        ds_name = self._datasource.get("name", "")

        # 1) Read field metadata from metadata-records
        for mr in self._datasource.findall(".//metadata-record[@class='column']"):
            remote_name_el = mr.find("remote-name")
            local_name_el = mr.find("local-name")
            local_type_el = mr.find("local-type")
            aggregation_el = mr.find("aggregation")

            if remote_name_el is None or local_name_el is None or local_type_el is None:
                continue

            display_name = remote_name_el.text or ""
            local_name = local_name_el.text or ""
            datatype = local_type_el.text or "string"

            # Infer role and field_type from datatype
            if datatype in ("real", "integer"):
                role = "measure"
                field_type = "quantitative"
            else:
                role = "dimension"
                field_type = "nominal"

            # Check for explicit column definition overriding role
            col_elem = self._datasource.find(
                f"column[@name='{local_name}']"
            )
            if col_elem is not None:
                explicit_role = col_elem.get("role")
                if explicit_role:
                    role = explicit_role
                explicit_type = col_elem.get("type")
                if explicit_type:
                    field_type = explicit_type

            self.field_registry.register(
                display_name=display_name,
                local_name=local_name,
                datatype=datatype,
                role=role,
                field_type=field_type,
            )

        # 2) Read calculated fields from <column> elements
        for col in self._datasource.findall("column"):
            calc = col.find("calculation")
            if calc is not None:
                caption = col.get("caption", "")
                name = col.get("name", "")
                datatype = col.get("datatype", "real")
                role = col.get("role", "measure")
                ft = col.get("type", "quantitative")
                self.field_registry.register(
                    display_name=caption or name,
                    local_name=name,
                    datatype=datatype,
                    role=role,
                    field_type=ft,
                    is_calculated=True,
                )

    def _reinit_fields(self) -> None:
        """Clear the field registry and re-initialize it."""
        self.field_registry._fields.clear()
        self._init_fields()

    # ================================================================
    # Database Connections
    # ================================================================

    def set_mysql_connection(
        self,
        server: str,
        dbname: str,
        username: str,
        table_name: str,
        port: str = "3306",
    ) -> str:
        """Configure the datasource to use a Local MySQL connection."""
        # 1. Update <connection class='federated'>
        fed_conn = self._datasource.find("connection[@class='federated']")
        if fed_conn is None:
            for old_conn in self._datasource.findall("connection"):
                self._datasource.remove(old_conn)
            fed_conn = etree.Element("connection")
            fed_conn.set("class", "federated")
            self._datasource.insert(0, fed_conn)

        # Update <named-connections>
        named_conns = fed_conn.find("named-connections")
        if named_conns is None:
            named_conns = etree.SubElement(fed_conn, "named-connections")
        else:
            for child in list(named_conns):
                named_conns.remove(child)

        conn_name = f"mysql.{_generate_uuid().strip('{}').lower()}"

        nc = etree.SubElement(named_conns, "named-connection")
        nc.set("caption", server)
        nc.set("name", conn_name)

        mysql_conn = etree.SubElement(nc, "connection")
        mysql_conn.set("class", "mysql")
        mysql_conn.set("dbname", dbname)
        mysql_conn.set("odbc-native-protocol", "")
        mysql_conn.set("one-time-sql", "")
        mysql_conn.set("port", str(port))
        mysql_conn.set("server", server)
        mysql_conn.set("source-charset", "")
        mysql_conn.set("username", username)

        # 2. Update <relation>
        relation = fed_conn.find("relation")
        if relation is None:
            relation = etree.SubElement(fed_conn, "relation")

        relation.set("connection", conn_name)
        relation.set("name", table_name)
        relation.set("table", f"[{table_name}]")
        relation.set("type", "table")
        for cols in relation.findall("columns"):
            relation.remove(cols)

        # 3. Update <object-graph> relation
        for og_rel in self._datasource.findall(".//object-graph//relation"):
            og_rel.set("connection", conn_name)
            og_rel.set("name", table_name)
            og_rel.set("table", f"[{table_name}]")
            og_rel.set("type", "table")
            for cols in og_rel.findall("columns"):
                og_rel.remove(cols)

        # 4. Cleanup old generic/excel connections and leftover fields
        excel_conn = self._datasource.find("connection[@class='excel-direct']")
        if excel_conn is not None:
            self._datasource.remove(excel_conn)
            
        old_cols = fed_conn.find("cols")
        if old_cols is not None:
            fed_conn.remove(old_cols)
            
        for c in self._datasource.findall("column"):
            self._datasource.remove(c)
            
        aliases = self._datasource.find("aliases")
        if aliases is not None:
            self._datasource.remove(aliases)

        # 6. Clean metadata-records
        for mr in self._datasource.findall(".//metadata-record"):
            mr.getparent().remove(mr)

        self._reinit_fields()
        return f"Configured MySQL connection to {server}/{dbname} (table: {table_name})"

    def set_tableauserver_connection(
        self,
        server: str,
        dbname: str,
        username: str,
        table_name: str,
        directory: str = "/dataserver",
        port: str = "82",
    ) -> str:
        """Configure the datasource to use a Tableau Server connection."""
        # 1. Remove all old connections
        for conn in self._datasource.findall("connection"):
            self._datasource.remove(conn)

        # 2. Add <repository-location>
        repo = self._datasource.find("repository-location")
        if repo is None:
            repo = etree.Element("repository-location")
            self._datasource.insert(0, repo)

        repo.set("derived-from", f"{directory}/{dbname}?rev=1.0")
        repo.set("id", dbname)
        repo.set("path", "/datasources")
        repo.set("revision", "1.0")

        # 3. Add <connection class='sqlproxy'>
        sqlproxy_conn = etree.Element("connection")
        channel = "https" if str(port) in ("443", "82") else "http"
        sqlproxy_conn.set("channel", channel)
        sqlproxy_conn.set("class", "sqlproxy")
        sqlproxy_conn.set("dbname", dbname)
        sqlproxy_conn.set("directory", directory)
        sqlproxy_conn.set("port", str(port))
        sqlproxy_conn.set("server", server)
        sqlproxy_conn.set("username", username)

        relation = etree.SubElement(sqlproxy_conn, "relation")
        relation.set("name", table_name)
        relation.set("table", f"[{table_name}]")
        relation.set("type", "table")

        # Insert after repository-location
        idx = list(self._datasource).index(repo)
        self._datasource.insert(idx + 1, sqlproxy_conn)

        # 4. Update <object-graph> relation
        for og_rel in self._datasource.findall(".//object-graph//relation"):
            if "connection" in og_rel.attrib:
                del og_rel.attrib["connection"]
            og_rel.set("name", table_name)
            og_rel.set("table", f"[{table_name}]")
            og_rel.set("type", "table")
            for cols in og_rel.findall("columns"):
                og_rel.remove(cols)
                
        # 5. Cleanup old fields and aliases
        for c in self._datasource.findall("column"):
            self._datasource.remove(c)
            
        aliases = self._datasource.find("aliases")
        if aliases is not None:
            self._datasource.remove(aliases)

        # 6. Clean metadata-records
        for mr in self._datasource.findall(".//metadata-record"):
            mr.getparent().remove(mr)

        self._reinit_fields()
        return f"Configured Tableau Server connection to {server}/{dbname} (table: {table_name})"

    # ================================================================
    # Calculated Fields
    # ================================================================

    def add_calculated_field(
        self,
        field_name: str,
        formula: str,
        datatype: str = "real",
    ) -> str:
        """Add a calculated field to the datasource.

        Args:
            field_name: Display name, e.g. "Profit Ratio"
            formula: Tableau calculation formula, e.g. "SUM([Profit])/SUM([Sales])"
            datatype: Data type: real/string/integer/date/boolean

        Returns:
            Confirmation message.
        """
        # Determine role and type
        if datatype in ("real", "integer"):
            role = "measure"
            field_type = "quantitative"
        else:
            role = "dimension"
            field_type = "nominal"

        internal_name = f"[Calculation_{field_name}]"

        # Create <column> element — must be inserted before <layout>
        # Tableau XSD requires column before layout/style/semantic-values
        col = etree.Element("column")
        col.set("caption", field_name)
        col.set("datatype", datatype)
        col.set("name", internal_name)
        col.set("role", role)
        col.set("type", field_type)

        # Find insertion point (before layout / semantic-values / date-options / object-graph)
        insert_before = None
        for tag in ("layout", "semantic-values", "date-options", "object-graph"):
            el = self._datasource.find(tag)
            if el is not None:
                insert_before = el
                break
        if insert_before is not None:
            insert_before.addprevious(col)
        else:
            self._datasource.append(col)

        # Create <calculation> child element
        calc = etree.SubElement(col, "calculation")
        calc.set("class", "tableau")
        calc.set("formula", formula)

        # Register in FieldRegistry
        self.field_registry.register(
            display_name=field_name,
            local_name=internal_name,
            datatype=datatype,
            role=role,
            field_type=field_type,
            is_calculated=True,
        )

        return f"Added calculated field '{field_name}': {formula}"

    def remove_calculated_field(self, field_name: str) -> str:
        """Remove a calculated field."""
        internal_name = f"[Calculation_{field_name}]"
        col = self._datasource.find(f"column[@name='{internal_name}']")
        if col is not None:
            self._datasource.remove(col)
            self.field_registry.unregister(field_name)
            return f"Removed calculated field '{field_name}'"
        return f"Calculated field '{field_name}' not found"

    # ================================================================
    # Worksheets
    # ================================================================

    def clear_worksheets(self) -> None:
        """Clear all worksheets and dashboards from the template."""
        # Clean worksheets
        worksheets = self.root.find(".//worksheets")
        if worksheets is not None:
            for child in list(worksheets):
                worksheets.remove(child)

        # Clean dashboards
        dashboards = self.root.find(".//dashboards")
        if dashboards is not None:
            for child in list(dashboards):
                dashboards.remove(child)

        # Clean windows to avoid ghost references
        windows = self.root.find(".//windows")
        if windows is not None:
            for child in list(windows):
                windows.remove(child)

        # Clear thumbnails
        thumbnails = self.root.find("thumbnails")
        if thumbnails is not None:
            for t in list(thumbnails):
                thumbnails.remove(t)

    def add_worksheet(self, worksheet_name: str) -> str:
        """Add a new blank worksheet."""
        worksheets = self.root.find("worksheets")
        if worksheets is None:
            worksheets = etree.SubElement(self.root, "worksheets")

        ds_name = self._datasource.get("name", "")
        ds_caption = self._datasource.get("caption", "")

        # Build worksheet XML skeleton
        ws = etree.SubElement(worksheets, "worksheet")
        ws.set("name", worksheet_name)

        table = etree.SubElement(ws, "table")

        # <view>
        view = etree.SubElement(table, "view")
        datasources_el = etree.SubElement(view, "datasources")
        ds_ref = etree.SubElement(datasources_el, "datasource")
        ds_ref.set("caption", ds_caption)
        ds_ref.set("name", ds_name)

        # datasource-dependencies placeholder (populated by configure_chart)
        agg = etree.SubElement(view, "aggregation")
        agg.set("value", "true")

        # <style> (empty)
        etree.SubElement(table, "style")

        # <panes>
        panes = etree.SubElement(table, "panes")
        pane = etree.SubElement(panes, "pane")
        pane.set("selection-relaxation-option", "selection-relaxation-allow")
        pane_view = etree.SubElement(pane, "view")
        breakdown = etree.SubElement(pane_view, "breakdown")
        breakdown.set("value", "auto")
        mark = etree.SubElement(pane, "mark")
        mark.set("class", "Automatic")

        # <rows> <cols> (empty)
        etree.SubElement(table, "rows")
        etree.SubElement(table, "cols")

        # <simple-id>
        simple_id = etree.SubElement(ws, "simple-id")
        simple_id.set("uuid", _generate_uuid())

        # Register window in <windows>
        self._add_window(worksheet_name)

        return f"Added worksheet '{worksheet_name}'"

    def _add_window(
        self,
        name: str,
        window_class: str = "worksheet",
        worksheet_names: Optional[list[str]] = None,
    ) -> None:
        """Add a window entry in <windows>.

        Worksheet windows use <cards> structure.
        Dashboard windows use <viewpoints> + <active> structure (per c.2 (2) reference).
        """
        windows = self.root.find("windows")
        if windows is None:
            windows = etree.SubElement(self.root, "windows")
            windows.set("saved-dpi-scale-factor", "1.25")
            windows.set("source-height", "37")

        window = etree.SubElement(windows, "window")
        window.set("class", window_class)
        window.set("maximized", "true")
        window.set("name", name)

        if window_class == "dashboard":
            # Dashboard window: viewpoints + active
            viewpoints = etree.SubElement(window, "viewpoints")
            if worksheet_names:
                for ws_name in worksheet_names:
                    vp = etree.SubElement(viewpoints, "viewpoint")
                    vp.set("name", ws_name)
                    zoom = etree.SubElement(vp, "zoom")
                    zoom.set("type", "entire-view")
            active = etree.SubElement(window, "active")
            active.set("id", "-1")
        else:
            # Worksheet window: cards
            cards = etree.SubElement(window, "cards")

            # Left edge
            left_edge = etree.SubElement(cards, "edge")
            left_edge.set("name", "left")
            left_strip = etree.SubElement(left_edge, "strip")
            left_strip.set("size", "160")
            for ctype in ("pages", "filters", "marks"):
                card = etree.SubElement(left_strip, "card")
                card.set("type", ctype)

            # Top edge
            top_edge = etree.SubElement(cards, "edge")
            top_edge.set("name", "top")
            for ctype in ("columns", "rows", "title"):
                strip = etree.SubElement(top_edge, "strip")
                strip.set("size", "2147483647")
                card = etree.SubElement(strip, "card")
                card.set("type", ctype)

        # simple-id
        simple_id = etree.SubElement(window, "simple-id")
        simple_id.set("uuid", _generate_uuid())

    # ================================================================
    # Chart Configuration
    # ================================================================

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
    ) -> str:
        """Configure chart type and field mappings for a worksheet.

        Args:
            worksheet_name: Target worksheet name.
            mark_type: Mark type: Bar/Line/Pie/Area/Circle/Automatic.
            columns: Column shelf expressions, e.g. ["SUM(Sales)"].
            rows: Row shelf expressions, e.g. ["Category"].
            color: Color encoding expression.
            size: Size encoding expression.
            label: Label encoding expression.
            detail: Detail encoding expression.
            wedge_size: Pie chart wedge size expression.
            sort_descending: Sort a dimension descending by this measure expression.
                The dimension is auto-detected from rows/columns.
                e.g. sort_descending="SUM(Sales)" sorts the row dimension by Sales DESC.

        Returns:
            Confirmation message.
        """
        columns = columns or []
        rows = rows or []

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

        # Parse all expressions into ColumnInstances
        instances: dict[str, ColumnInstance] = {}
        for expr in all_exprs:
            ci = self.field_registry.parse_expression(expr)
            instances[expr] = ci

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
                col_el = etree.Element("column")
                col_el.set("datatype", fi.datatype)
                col_el.set("name", fi.local_name)
                col_el.set("role", fi.role)
                col_el.set("type", fi.field_type)
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

        # 2) Set mark type
        pane = table.find(".//pane")
        if pane is None:
            raise ValueError("Malformed structure: missing <pane>")

        mark_el = pane.find("mark")
        if mark_el is not None:
            mark_el.set("class", mark_type)
        else:
            mark_el = etree.SubElement(pane, "mark")
            mark_el.set("class", mark_type)

        # 3) Set style (add special styles for Pie charts)
        table_style = table.find("style")
        if table_style is None:
            table_style = etree.SubElement(table, "style")

        if mark_type == "Pie":
            self._apply_pie_style(table_style)

        # 4) Set encodings
        # Remove old encodings
        old_enc = pane.find("encodings")
        if old_enc is not None:
            pane.remove(old_enc)

        has_encodings = any(x is not None for x in (color, size, label, detail, wedge_size))
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

        # 5) Set pane style (mark labels, etc.)
        pane_style = pane.find("style")
        if pane_style is None:
            pane_style = etree.SubElement(pane, "style")
        # Ensure mark style exists
        self._ensure_mark_style(pane_style, mark_type)

        # 6) Set rows and cols
        rows_el = table.find("rows")
        cols_el = table.find("cols")

        if rows_el is not None and rows:
            row_refs = []
            for expr in rows:
                ci = instances[expr]
                row_refs.append(self.field_registry.resolve_full_reference(ci.instance_name))
            rows_el.text = " ".join(row_refs)
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

        return f"Configured worksheet '{worksheet_name}' as {mark_type} chart"

    def _add_shelf_sort(
        self,
        view: etree._Element,
        ds_name: str,
        instances: dict[str, "ColumnInstance"],
        rows: list[str],
        sort_measure_expr: str,
    ) -> None:
        """Add shelf-sort for descending sort on a dimension by a measure.

        Generates <shelf-sorts><shelf-sort-v2 .../></shelf-sorts> in <view>.
        Auto-detects the dimension from rows (first dimension found).
        Also adds required manifest entries (IntuitiveSorting).
        """
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
        """Ensure a <document-format-change-manifest> entry exists."""
        manifest = self.root.find("document-format-change-manifest")
        if manifest is None:
            manifest = etree.SubElement(self.root, "document-format-change-manifest")
        if manifest.find(entry_name) is None:
            etree.SubElement(manifest, entry_name)

    def _apply_pie_style(self, table_style: etree._Element) -> None:
        """Add special style rules for Pie charts."""
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

    def _ensure_mark_style(self, pane_style: etree._Element, mark_type: str) -> None:
        """Ensure mark style rule exists in the pane."""
        # Check if mark style-rule already exists
        for sr in pane_style.findall("style-rule"):
            if sr.get("element") == "mark":
                return  # Already present

        sr = etree.SubElement(pane_style, "style-rule")
        sr.set("element", "mark")

        if mark_type == "Pie":
            # Set pie size
            fmt = etree.SubElement(sr, "format")
            fmt.set("attr", "size")
            fmt.set("value", "1.8")

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
        """Add viewpoint/highlight for Pie chart color encoding.

        The viewpoint is inserted before simple-id, matching Tableau Desktop structure.
        """
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

    def _find_worksheet(self, name: str) -> etree._Element:
        """Find a worksheet element by name."""
        for ws in self.root.findall(".//worksheets/worksheet"):
            if ws.get("name") == name:
                return ws
        raise ValueError(f"Worksheet '{name}' not found")

    # ================================================================
    # Dashboards
    # ================================================================

    def add_dashboard(
        self,
        dashboard_name: str,
        width: int = 1200,
        height: int = 800,
        layout: str | dict = "vertical",
        worksheet_names: Optional[list[str]] = None,
    ) -> str:
        """Create a dashboard and arrange worksheets.

        Uses layout-flow zone structure. The layout parameter can be a simple string
        ('vertical', 'horizontal', 'grid-2x2') or a complex declarative JSON layout dictionary.

        Args:
            dashboard_name: Dashboard name.
            width: Canvas width in pixels.
            height: Canvas height in pixels.
            layout: Layout type: vertical/horizontal/grid-2x2 or nested dict.
            worksheet_names: List of worksheet names to include.

        Returns:
            Confirmation message.
        """
        worksheet_names = worksheet_names or []

        # Validate worksheets exist
        for ws_name in worksheet_names:
            self._find_worksheet(ws_name)

        # Get or create <dashboards>
        dashboards = self.root.find("dashboards")
        if dashboards is None:
            # Insert after worksheets
            ws_el = self.root.find("worksheets")
            if ws_el is not None:
                idx = list(self.root).index(ws_el) + 1
                dashboards = etree.Element("dashboards")
                self.root.insert(idx, dashboards)
            else:
                dashboards = etree.SubElement(self.root, "dashboards")

        # Create dashboard element
        # Structure: style -> size -> zones -> simple-id
        db = etree.SubElement(dashboards, "dashboard")
        db.set("name", dashboard_name)

        # style
        etree.SubElement(db, "style")

        # size
        size_el = etree.SubElement(db, "size")
        size_el.set("maxheight", str(height))
        size_el.set("maxwidth", str(width))
        size_el.set("minheight", str(height))
        size_el.set("minwidth", str(width))

        # zones
        zones = etree.SubElement(db, "zones")

        if worksheet_names or isinstance(layout, dict):
            if isinstance(layout, str):
                if layout == "horizontal":
                    layout_dict = {
                        "type": "container",
                        "direction": "horizontal",
                        "layout_strategy": "distribute-evenly",
                        "children": [{"type": "worksheet", "name": w} for w in worksheet_names]
                    }
                elif layout == "grid-2x2":
                    n = len(worksheet_names)
                    row1_children = [{"type": "worksheet", "name": w} for w in worksheet_names[:2]]
                    row2_children = [{"type": "worksheet", "name": w} for w in worksheet_names[2:4]]
                    layout_dict = {
                        "type": "container",
                        "direction": "vertical",
                        "layout_strategy": "distribute-evenly",
                        "children": [
                            {"type": "container", "direction": "horizontal", "layout_strategy": "distribute-evenly", "children": row1_children},
                        ]
                    }
                    if row2_children:
                        layout_dict["children"].append({"type": "container", "direction": "horizontal", "layout_strategy": "distribute-evenly", "children": row2_children})
                else:  # vertical
                    layout_dict = {
                        "type": "container",
                        "direction": "vertical",
                        "layout_strategy": "distribute-evenly",
                        "children": [{"type": "worksheet", "name": w} for w in worksheet_names]
                    }
            else:
                layout_dict = layout
                
            from cwtwb.layout import generate_dashboard_zones
            generate_dashboard_zones(zones, layout_dict, width, height, self._next_zone_id)

        # simple-id (required)
        db_simple_id = etree.SubElement(db, "simple-id")
        db_simple_id.set("uuid", _generate_uuid())

        # Register dashboard window
        self._add_window(dashboard_name, window_class="dashboard", worksheet_names=(worksheet_names or []))

        return f"Created dashboard '{dashboard_name}'"

    def _next_zone_id(self) -> int:
        self._zone_id_counter += 1
        return self._zone_id_counter

    # ================================================================
    # List Fields
    # ================================================================

    def list_fields(self) -> str:
        """List all fields in the datasource."""
        lines = []
        ds_caption = self._datasource.get("caption", "")
        lines.append(f"Datasource: {ds_caption}")
        lines.append("")

        dims = self.field_registry.dimensions()
        measures = self.field_registry.measures()

        lines.append(f"Dimensions ({len(dims)}):")
        for f in dims:
            calc_tag = " [calculated]" if f.is_calculated else ""
            lines.append(f"  - {f.display_name} [{f.datatype}]{calc_tag}")

        lines.append(f"\nMeasures ({len(measures)}):")
        for f in measures:
            calc_tag = " [calculated]" if f.is_calculated else ""
            lines.append(f"  - {f.display_name} [{f.datatype}]{calc_tag}")

        return "\n".join(lines)

    # ================================================================
    # Save
    # ================================================================

    def save(self, output_path: str | Path) -> str:
        """Save the TWB file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize
        xml_bytes = etree.tostring(
            self.tree,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=True,
        )

        output_path.write_bytes(xml_bytes)
        return f"Saved workbook to {output_path}"
