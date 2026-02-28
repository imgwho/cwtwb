import xml.etree.ElementTree as ET

files = ['superstore.twb', 'superstore - localmysql.twb', 'superstore - tableauserver.twb']
for f in files:
    tree = ET.parse('templates/twb/' + f)
    print(f'\n=== {f} ===')
    ds = tree.find('.//datasource')
    connections = ds.findall('.//connection')
    for c in connections:
        if c.get('class') in ['federated', 'excel-direct', 'mysql', 'sqlproxy']:
            print(f'<{c.tag} class="{c.get("class")}" ' + ' '.join([f'{k}="{v}"' for k,v in c.attrib.items() if k != 'class']) + '>')
            for child in c:
                if child.tag != 'metadata-records':
                    print(f'  <{child.tag} ' + ' '.join([f'{k}="{v}"' for k,v in child.attrib.items()]) + '/>')
            print(f'</{c.tag}>')
