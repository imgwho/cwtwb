import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cwtwb.twb_editor import TWBEditor

@pytest.fixture
def superstore_template():
    return Path(__file__).parent.parent / "templates" / "twb" / "superstore.twb"

def test_set_mysql_connection(superstore_template, tmp_path):
    editor = TWBEditor(superstore_template)
    
    msg = editor.set_mysql_connection(
        server="127.0.0.1",
        dbname="superstore",
        username="root",
        table_name="orders",
        port="3306"
    )
    assert "Configured MySQL connection" in msg
    
    out_file = tmp_path / "superstore_mysql.twb"
    editor.save(out_file)
    
    # Verify XML content
    tree = ET.parse(out_file)
    ds = tree.find(".//datasource")
    
    fed_conn = ds.find("connection[@class='federated']")
    assert fed_conn is not None
    
    named_conns = fed_conn.find("named-connections")
    assert named_conns is not None
    
    nc = named_conns.find("named-connection")
    assert nc is not None
    assert nc.get("caption") == "127.0.0.1"
    
    mysql_conn = nc.find("connection")
    assert mysql_conn is not None
    assert mysql_conn.get("class") == "mysql"
    assert mysql_conn.get("dbname") == "superstore"
    assert mysql_conn.get("username") == "root"
    assert mysql_conn.get("port") == "3306"
    assert mysql_conn.get("server") == "127.0.0.1"
    
    relation = fed_conn.find("relation")
    assert relation is not None
    assert relation.get("type") == "table"
    assert relation.get("name") == "orders"
    assert relation.get("table") == "[orders]"
    assert relation.get("connection") == nc.get("name")
    
    # Ensure no old excel connections remain
    assert ds.find("connection[@class='excel-direct']") is None

def test_set_tableauserver_connection(superstore_template, tmp_path):
    editor = TWBEditor(superstore_template)
    
    msg = editor.set_tableauserver_connection(
        server="tbs.fstyun.cn",
        dbname="data16_",
        username="",
        table_name="sqlproxy",
        directory="/dataserver",
        port="82"
    )
    assert "Configured Tableau Server connection" in msg
    
    out_file = tmp_path / "superstore_tbs.twb"
    editor.save(out_file)
    
    # Verify XML content
    tree = ET.parse(out_file)
    ds = tree.find(".//datasource")
    
    repo = ds.find("repository-location")
    assert repo is not None
    assert repo.get("id") == "data16_"
    assert repo.get("derived-from") == "/dataserver/data16_?rev=1.0"
    
    proxy_conn = ds.find("connection[@class='sqlproxy']")
    assert proxy_conn is not None
    assert proxy_conn.get("server") == "tbs.fstyun.cn"
    assert proxy_conn.get("dbname") == "data16_"
    assert proxy_conn.get("directory") == "/dataserver"
    assert proxy_conn.get("port") == "82"
    assert proxy_conn.get("channel") == "https"
    
    relation = proxy_conn.find("relation")
    assert relation is not None
    assert relation.get("type") == "table"
    assert relation.get("name") == "sqlproxy"
    assert relation.get("table") == "[sqlproxy]"
    
    # Ensure no old federated connections remain
    assert ds.find("connection[@class='federated']") is None
    assert ds.find("connection[@class='excel-direct']") is None
