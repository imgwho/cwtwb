"""Dashboard creation mixin for TWBEditor."""

from __future__ import annotations

from typing import Optional

from lxml import etree

from .config import _generate_uuid
from .dashboard_actions import add_dashboard_action as _add_dashboard_action
from .dashboard_dependencies import add_dashboard_dependencies
from .dashboard_layouts import (
    render_dashboard_layout,
    resolve_dashboard_layout,
    validate_layout_worksheets,
)


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
        """Create a dashboard and arrange worksheets."""
        worksheet_names = worksheet_names or []

        for ws_name in worksheet_names:
            self._find_worksheet(ws_name)

        dashboards = self.root.find("dashboards")
        if dashboards is None:
            insert_before = None
            for tag in ("windows", "external"):
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

        db = etree.SubElement(dashboards, "dashboard")
        db.set("name", dashboard_name)

        etree.SubElement(db, "style")

        size_el = etree.SubElement(db, "size")
        size_el.set("maxheight", str(height))
        size_el.set("maxwidth", str(width))
        size_el.set("minheight", str(height))
        size_el.set("minwidth", str(width))
        size_el.set("sizing-mode", "fixed")

        zones = etree.SubElement(db, "zones")

        if worksheet_names or isinstance(layout, dict) or isinstance(layout, str):
            layout_dict = resolve_dashboard_layout(layout, worksheet_names)
            validate_layout_worksheets(layout_dict)
            render_dashboard_layout(
                zones,
                layout_dict,
                width,
                height,
                self._next_zone_id,
                field_registry=self.field_registry,
                parameters=self._parameters,
                editor=self,
            )
            self._add_dashboard_deps(db, layout_dict)

        db_simple_id = etree.SubElement(db, "simple-id")
        db_simple_id.set("uuid", _generate_uuid())

        self._add_window(
            dashboard_name,
            window_class="dashboard",
            worksheet_names=(worksheet_names or []),
        )
        return f"Created dashboard '{dashboard_name}'"

    def _next_zone_id(self) -> int:
        self._zone_id_counter += 1
        return self._zone_id_counter

    def _add_dashboard_deps(self, db: etree._Element, layout_dict: dict) -> None:
        """Compatibility wrapper for dashboard dependency generation."""
        add_dashboard_dependencies(self, db, layout_dict)

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
        """Compatibility wrapper for dashboard action creation."""
        return _add_dashboard_action(
            self,
            dashboard_name,
            action_type,
            source_sheet,
            target_sheet,
            fields,
            event_type,
            caption,
        )
