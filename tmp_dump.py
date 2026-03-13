import xml.etree.ElementTree as ET

def analyze_dashboard(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    dashboards_xml = root.find('dashboards')
    if dashboards_xml is not None:
        for zone in dashboards_xml.iter('zone'):
            name = zone.get('name', '')
            type_v2 = zone.get('type-v2', '')
            w = zone.get('w', '')
            h = zone.get('h', '')
            is_fixed = zone.get('is-fixed', '')
            fixed_size = zone.get('fixed-size', '')
            
            print(f"id={zone.get('id')} type={type_v2} name='{name}' w={w} fixed={is_fixed} fixed_size={fixed_size} param={zone.get('param', '')}")
            
            # Print children <layout-cache> if present
            cache = zone.find('layout-cache')
            if cache is not None:
                print(f"  -> layout-cache: type-h={cache.get('type-h')} type-w={cache.get('type-w')}")

if __name__ == '__main__':
    analyze_dashboard(r'examples/superstore_recreated/Exec Overview Recreated 2204.twb')
