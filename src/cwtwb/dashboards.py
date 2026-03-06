"""Dashboard creation mixin for TWBEditor.

Handles add_dashboard, dashboard dependencies, and dashboard actions.
"""

from __future__ import annotations

import copy
import json
import logging
from pathlib import Path
from typing import Optional

from lxml import etree

from .config import _generate_uuid
from .layout import generate_dashboard_zones

logger = logging.getLogger(__name__)


class DashboardsMixin:
    """Mixin providing dashboard creation and action methods for TWBEditor."""

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
            insert_before = None
            for tag in ("windows", "thumbnails", "external"):
                el = self.root.find(tag)
                if el is not None:
                    insert_before = el
                    break
            if insert_before is not None:
                dashboards = etree.Element("dashboards")
                insert_before.addprevious(dashboards)
            else:
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
        size_el.set("sizing-mode", "fixed")

        # zones
        zones = etree.SubElement(db, "zones")

        if worksheet_names or isinstance(layout, dict) or isinstance(layout, str):
            if isinstance(layout, str):
                import json
                
                # Check if layout is a file path
                layout_path = Path(layout)
                if layout_path.exists() and layout_path.is_file():
                    with open(layout_path, 'r', encoding='utf-8') as f:
                        loaded_json = json.load(f)
                        if isinstance(loaded_json, dict) and "layout_schema" in loaded_json:
                            layout_dict = loaded_json["layout_schema"]
                        else:
                            layout_dict = loaded_json
                elif layout == "horizontal":
                    layout_dict = {
                        "type": "container",
                        "direction": "horizontal",
                        "layout_strategy": "distribute-evenly",
                        "children": [{"type": "worksheet", "name": w} for w in worksheet_names]
                    }
                elif layout == "grid-2x2":
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
            
            # Extract and validate all worksheets in the layout tree
            def _extract_worksheets(node: dict) -> list[str]:
                sheets = []
                if node.get("type") == "worksheet":
                    sheets.append(node.get("name"))
                elif "children" in node:
                    for child in node["children"]:
                        sheets.extend(_extract_worksheets(child))
                return sheets
            
            used_sheets = _extract_worksheets(layout_dict)
            seen_sheets = set()
            for sheet in used_sheets:
                if sheet in seen_sheets:
                    raise ValueError(f"A worksheet can only be used once per dashboard. Found duplicate: '{sheet}'. Please add and configure a duplicate worksheet instead.")
                seen_sheets.add(sheet)
                
            # generate_dashboard_zones imported at module level
            context = {
                "field_registry": self.field_registry,
                "parameters": self._parameters,
                "editor": self
            }
            generate_dashboard_zones(zones, layout_dict, width, height, self._next_zone_id, context)

            # Add dashboard-level datasources and datasource-dependencies
            # for filter zones and paramctrl zones
            self._add_dashboard_deps(db, layout_dict)

        # simple-id (required)
        db_simple_id = etree.SubElement(db, "simple-id")
        db_simple_id.set("uuid", _generate_uuid())

        # Register dashboard window
        self._add_window(dashboard_name, window_class="dashboard", worksheet_names=(worksheet_names or []))

        return f"Created dashboard '{dashboard_name}'"

    def _next_zone_id(self) -> int:
        self._zone_id_counter += 1
        return self._zone_id_counter
    def _add_dashboard_deps(self, db: etree._Element, layout_dict: dict) -> None:
        """Add dashboard-level datasources and datasource-dependencies.
        
        Scans the layout tree for filter and paramctrl zones, and generates
        the necessary datasource references and field dependencies.
        """
        import copy
        
        # Extract filter and paramctrl zones from layout tree
        filters_zones = []
        paramctrl_zones = []
        
        def _extract_zones(node: dict) -> None:
            if node.get("type") == "filter":
                filters_zones.append(node)
            elif node.get("type") == "paramctrl":
                paramctrl_zones.append(node)
            for child in node.get("children", []):
                _extract_zones(child)
        
        _extract_zones(layout_dict)
        
        if not filters_zones and not paramctrl_zones:
            return
        
        ds_name = self._datasource.get("name", "")
        
        # Create <datasources> in dashboard
        db_datasources = etree.Element("datasources")
        
        has_params = bool(paramctrl_zones or self._parameters)
        if has_params:
            pds = etree.SubElement(db_datasources, "datasource")
            pds.set("caption", "参数")
            pds.set("name", "Parameters")
        
        if filters_zones:
            fds = etree.SubElement(db_datasources, "datasource")
            caption = self._datasource.get("caption", ds_name)
            fds.set("caption", caption)
            fds.set("name", ds_name)
        
        # Insert datasources after <size> element
        size_el = db.find("size")
        if size_el is not None:
            size_el.addnext(db_datasources)
        
        # Add Parameters datasource-dependencies  
        if has_params:
            params_ds = None
            for ds in self.root.findall(".//datasource"):
                if ds.get("name") == "Parameters":
                    params_ds = ds
                    break
            if params_ds is not None:
                param_deps = etree.Element("datasource-dependencies")
                param_deps.set("datasource", "Parameters")
                for col in params_ds.findall("column"):
                    param_deps.append(copy.deepcopy(col))
                db_datasources.addnext(param_deps)
        
        # Add federated datasource-dependencies for filter fields
        if filters_zones:
            filter_deps = etree.Element("datasource-dependencies")
            filter_deps.set("datasource", ds_name)
            
            seen_cols = set()
            seen_ci = set()
            col_elements = []
            ci_elements = []
            
            for fz in filters_zones:
                field = fz.get("field")
                if not field:
                    continue
                try:
                    ci = self.field_registry.parse_expression(field)
                    fi = self.field_registry._find_field(field)
                    
                    if ci.column_local_name not in seen_cols:
                        seen_cols.add(ci.column_local_name)
                        col_el = etree.Element("column")
                        col_el.set("datatype", fi.datatype)
                        col_el.set("name", fi.local_name)
                        col_el.set("role", fi.role)
                        col_el.set("type", fi.field_type)
                        # Copy semantic-role if present
                        src_col = self._datasource.find(f"column[@name='{fi.local_name}']")
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
                except (KeyError, ValueError) as e:
                    logger.warning("Failed to resolve filter field '%s' in dashboard deps: %s", field, e)
            
            for el in sorted(col_elements, key=lambda e: e.get("name", "")):
                filter_deps.append(el)
            for el in sorted(ci_elements, key=lambda e: e.get("name", "")):
                filter_deps.append(el)
            
            # Insert after param deps or after datasources
            zones_el = db.find("zones")
            if zones_el is not None:
                zones_el.addprevious(filter_deps)
            else:
                db.append(filter_deps)
    def add_dashboard_action(
        self,
        dashboard_name: str,
        action_type: str,
        source_sheet: str,
        target_sheet: str,
        fields: list[str],
        event_type: str = "on-select",
        caption: str = "",
    ) -> str:
        """Add an interaction action to a dashboard.

        Supports 'filter' or 'highlight' actions between two worksheets on the dashboard.

        Args:
            dashboard_name: The name of the dashboard containing the source worksheet.
            action_type: Type of action ('filter' or 'highlight').
            source_sheet: The worksheet triggering the action.
            target_sheet: The worksheet being affected by the action.
            fields: List of fields to match on (e.g., ["Region", "State"]).
            event_type: Trigger event ('on-select', 'on-hover', 'on-menu'). Default is 'on-select'.
            caption: Optional caption for the action.

        Returns:
            Confirmation message.
            
        Raises:
            ValueError: If dashboard or worksheets not found, or unsupported action type.
        """
        if action_type not in ("filter", "highlight"):
            raise ValueError(f"Unsupported action_type '{action_type}'. Use 'filter' or 'highlight'.")

        db_el = self.root.find(f".//dashboards/dashboard[@name='{dashboard_name}']")
        if db_el is None:
            raise ValueError(f"Dashboard '{dashboard_name}' not found.")

        self._find_worksheet(source_sheet)
        self._find_worksheet(target_sheet)

        actions_el = self.root.find("actions")
        if actions_el is None:
            actions_el = etree.Element("actions")
            insert_before = None
            for tag in ("worksheets", "dashboards", "windows", "thumbnails"):
                insert_before = self.root.find(tag)
                if insert_before is not None:
                    break
            
            if insert_before is not None:
                insert_before.addprevious(actions_el)
            else:
                self.root.append(actions_el)

        USER_NS = "http://www.tableausoftware.com/xml/user"
        
        # We need to set the xmlns:user via a workaround in lxml or just use nsmap
        action_el = etree.Element("action", nsmap={"user": USER_NS})
        # Tableau XSD requires <action>* before <datasources>/<datasource-dependencies>
        # inside <actions>.  When loading a template the <actions> block may already
        # contain <datasources> or <datasource-dependencies> children; appending blindly
        # would place the new action after them and produce a schema error.
        # Find the first blocker element and insert before it.
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

        act_el = etree.SubElement(action_el, "activation")
        act_el.set("auto-clear", "true")
        if event_type != "on-select":
            act_el.set("type", event_type)
        elif event_type == "on-select":
             act_el.set("type", "on-select")

        source_el = etree.SubElement(action_el, "source")
        source_el.set("dashboard", dashboard_name)
        source_el.set("type", "sheet")
        if source_sheet:
            source_el.set("worksheet", source_sheet)
            
        # Get all worksheets in this dashboard to build the 'exclude' list
        zones_el = db_el.find("zones")
        all_sheets = []
        if zones_el is not None:
            for z in zones_el.findall(".//zone"):
                ws_name = z.get("name")
                if ws_name and ws_name not in all_sheets:
                    all_sheets.append(ws_name)
                    
        # Calculate excluded sheets (everything except target)
        # Note: According to Tableau, standard interactions target the Dashboard,
        # but exclude all sheets EXCEPT the target.
        exclude_sheets = [s for s in all_sheets if s != target_sheet]

        if action_type == "filter":
            if fields:
                # Use link for specific fields filter
                from urllib.parse import quote
                ds_name = self._datasource.get("name", "")
                link_el = etree.SubElement(action_el, "link")
                link_el.set("caption", action_caption)
                link_el.set("delimiter", ",")
                link_el.set("escape", "\\")
                
                field_expressions = []
                for f in fields:
                    ci = self.field_registry.parse_expression(f)
                    col_name = ci.column_local_name # already has brackets, e.g. "[State/Province]"
                    encoded_ds = quote(f"[{ds_name}]")
                    encoded_col = quote(col_name) # Remove extra brackets
                    field_expressions.append(f"{encoded_ds}.{encoded_col}~s0=<{col_name}~na>")
                
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

        elif action_type == "highlight":
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
                 # Note: in Correct Action we see special-fields=all
                 # If user provides fields, we map them as field-captions maybe?
                 # But in correct XML it used special-fields="all" even with highlight.
                 # Let's trust field-captions for specific fields if provided.
                 param_fields = etree.SubElement(cmd_el, "param")
                 param_fields.set("name", "field-captions")
                 param_fields.set("value", ",".join(fields))
                
            param_tgt = etree.SubElement(cmd_el, "param")
            param_tgt.set("name", "target")
            param_tgt.set("value", dashboard_name)

        return f"Added {action_type} action '{action_caption}' to '{dashboard_name}'"
