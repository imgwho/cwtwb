"""Connection configuration mixin for TWBEditor.

Handles MySQL and Tableau Server connection setup.
"""

from __future__ import annotations

from lxml import etree

from .config import _generate_uuid


class ConnectionsMixin:
    """Mixin providing database connection methods for TWBEditor."""

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

    def set_hyper_connection(
        self,
        filepath: str,
        table_name: str = "Extract",
    ) -> str:
        """Configure the datasource to use a local Hyper extract connection."""
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

        conn_name = f"hyper.{_generate_uuid().strip('{}').lower()}"

        nc = etree.SubElement(named_conns, "named-connection")
        nc.set("caption", filepath.split("/")[-1].split("\\")[-1])
        nc.set("name", conn_name)

        hyper_conn = etree.SubElement(nc, "connection")
        hyper_conn.set("authentication", "auth-none")
        hyper_conn.set("author-locale", "en_US")
        hyper_conn.set("class", "hyper")
        hyper_conn.set("dbname", filepath)
        hyper_conn.set("default-settings", "yes")
        hyper_conn.set("schema", "Extract")
        hyper_conn.set("sslmode", "")
        hyper_conn.set("tablename", "Extract")
        hyper_conn.set("username", "")

        # 2. Update <relation>
        relation = fed_conn.find("relation")
        if relation is None:
            relation = etree.SubElement(fed_conn, "relation")

        relation.set("connection", conn_name)
        relation.set("name", table_name)
        relation.set("table", f"[Extract].[{table_name}]")
        relation.set("type", "table")
        for cols in relation.findall("columns"):
            relation.remove(cols)

        # 3. Update <object-graph> relation
        for og_rel in self._datasource.findall(".//object-graph//relation"):
            og_rel.set("connection", conn_name)
            og_rel.set("name", table_name)
            og_rel.set("table", f"[Extract].[{table_name}]")
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
        return f"Configured Hyper connection to {filepath} (table: {table_name})"

