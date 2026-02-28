import xml.etree.ElementTree as ET
files = ['superstore.twb', 'superstore - localmysql.twb', 'superstore - tableauserver.twb']
for f in files:
    tree = ET.parse('templates/twb/' + f)
    ds = tree.find('.//datasource')
    print(f'\n=== {f} ===')
    cols = ds.findall('column')
    print(f'Count of <column> under datasource: {len(cols)}')
    for c in cols[:5]:
        print(f'  {c.get("name")}: {c.get("caption", "")}  role={c.get("role")} type={c.get("type")}')
    
    aliases = ds.find('aliases')
    if aliases is not None:
        print(f'<aliases> found, enabled={aliases.get("enabled", "")}')
        
    cols_node = ds.find('connection/cols')
    if cols_node is not None:
        print(f'<connection><cols> found with {len(list(cols_node))} children')
    
    # Check simple-id in worksheet
    ws = tree.find('.//worksheets/worksheet')
    if ws is not None:
        view = ws.find('.//view')
        deps = view.findall('datasource-dependencies')
        print(f'Count of datasource-dependencies in view: {len(deps)}')
