"""Declarative JSON layout engine for Tableau dashboards.

This module provides a FlexBox-like layout engine that translates nested
JSON/dict definitions into Tableau's complex <zone> hierarchy with absolute
and proportional coordinate math geometry applied.
"""

from typing import Any, Callable
from lxml import etree


class FlexNode:
    """A node in the declarative dashboard layout tree."""
    
    def __init__(self, d: dict[str, Any]):
        self.type = d.get("type", "container")  # container, worksheet, text
        self.direction = d.get("direction", "vertical")  # vertical, horizontal
        self.children = [FlexNode(c) for c in d.get("children", [])]
        self.fixed_size = d.get("fixed_size")
        self.weight = d.get("weight", 1)
        self.style = d.get("style", {})
        
        self.name = d.get("name")  # For worksheet
        self.text_content = d.get("text", "")  # For text
        self.font_size = d.get("font_size", "12")
        self.font_color = d.get("font_color", "#111e29")
        self.bold = d.get("bold", False)
        self.layout_strategy = d.get("layout_strategy")
        
        # Computed bounds (in Tableau's 100000 coordinate system)
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        
        # Computed pixel bounds
        self.px_x = 0.0
        self.px_y = 0.0
        self.px_w = 0.0
        self.px_h = 0.0

    def compute_layout(self, px_x: float, px_y: float, px_w: float, px_h: float, dash_w: float, dash_h: float) -> None:
        """Recursively compute the pixel bounds and Tableau percentage coordinates."""
        self.px_x = px_x
        self.px_y = px_y
        self.px_w = px_w
        self.px_h = px_h
        
        # Guard against zero-division
        if dash_w == 0 or dash_h == 0:
            dash_w = 1200
            dash_h = 800

        # Convert to Tableau's 100000 scale
        self.x = int(round((px_x / dash_w) * 100000))
        self.y = int(round((px_y / dash_h) * 100000))
        self.w = int(round((px_w / dash_w) * 100000))
        self.h = int(round((px_h / dash_h) * 100000))
        
        if self.type == "container" and self.children:
            if self.direction == "horizontal":
                total_fixed = sum(c.fixed_size for c in self.children if c.fixed_size is not None)
                total_weight = sum(c.weight for c in self.children if c.fixed_size is None)
                remaining_px = max(0, px_w - total_fixed)
                
                curr_x = px_x
                for c in self.children:
                    c_px_w = float(c.fixed_size) if c.fixed_size is not None else (remaining_px * c.weight / total_weight if total_weight else 0.0)
                    c.compute_layout(curr_x, px_y, c_px_w, px_h, dash_w, dash_h)
                    curr_x += c_px_w
            else:  # vertical
                total_fixed = sum(c.fixed_size for c in self.children if c.fixed_size is not None)
                total_weight = sum(c.weight for c in self.children if c.fixed_size is None)
                remaining_px = max(0, px_h - total_fixed)
                
                curr_y = px_y
                for c in self.children:
                    c_px_h = float(c.fixed_size) if c.fixed_size is not None else (remaining_px * c.weight / total_weight if total_weight else 0.0)
                    c.compute_layout(px_x, curr_y, px_w, c_px_h, dash_w, dash_h)
                    curr_y += c_px_h

    def render_to_xml(self, parent_el: etree._Element, get_id_fn: Callable[[], str]) -> etree._Element:
        """Render the computed node directly to lxml tree."""
        zone = etree.SubElement(parent_el, "zone")
        zone.set("id", str(get_id_fn()))
        zone.set("x", str(self.x))
        zone.set("y", str(self.y))
        zone.set("w", str(self.w))
        zone.set("h", str(self.h))
        
        if self.fixed_size is not None:
            zone.set("fixed-size", str(self.fixed_size))
            zone.set("is-fixed", "true")
            
        if self.type == "container":
            zone.set("type-v2", "layout-flow")
            zone.set("param", "horz" if self.direction == "horizontal" else "vert")
            if self.layout_strategy:
                zone.set("layout-strategy-id", self.layout_strategy)
            for c in self.children:
                c.render_to_xml(zone, get_id_fn)
                
        elif self.type == "worksheet":
            if self.name:
                zone.set("name", self.name)
                
        elif self.type == "text":
            zone.set("type-v2", "text")
            zone.set("forceUpdate", "true")
            ft = etree.SubElement(zone, "formatted-text")
            run = etree.SubElement(ft, "run")
            if self.bold:
                run.set("bold", "true")
            run.set("fontalignment", "1")
            run.set("fontcolor", self.font_color)
            run.set("fontsize", str(self.font_size))
            run.text = self.text_content
            
        # Apply standard or custom styles
        self._apply_style(zone, self.style)
        return zone
            
    def _apply_style(self, zone: etree._Element, style_dict: dict[str, Any]) -> None:
        zs = etree.SubElement(zone, "zone-style")
        
        # default border removal for modern flat design
        defaults = {
            "border-color": "#000000",
            "border-style": "none",
            "border-width": "0"
        }
        
        # merge in defaults if missing
        merged = {}
        for k, v in defaults.items():
            if k not in style_dict and k.replace("-", "_") not in style_dict:
                merged[k] = str(v)
                
        for k, v in style_dict.items():
            attr_name = k.replace("_", "-")
            if v is None:
                continue
            merged[attr_name] = str(v)
            
        for k, v in merged.items():
            fmt = etree.SubElement(zs, "format")
            fmt.set("attr", k)
            fmt.set("value", str(v))


def generate_dashboard_zones(parent_zones_el: etree._Element, layout_config: dict[str, Any], width: int, height: int, get_id_fn: Callable[[], str]) -> None:
    """Helper to compute and render the full layout tree."""
    root_node = FlexNode(layout_config)
    
    # Optional outer wrapper for the dashboard itself to set size correctly in Tableau
    wrapper_node = FlexNode({
        "type": "container",
        "direction": "vertical",
        "children": [layout_config]
    })
    
    wrapper_node.compute_layout(0.0, 0.0, float(width), float(height), float(width), float(height))
    
    # We strip the artificial wrapper since Tableau uses "zones" as the top level, 
    # instead we render the single actual layout root child which inherited dimensions
    if wrapper_node.children:
        wrapper_node.children[0].render_to_xml(parent_zones_el, get_id_fn)

