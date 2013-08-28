def get_tables_for_query(query):
# from johnny-cache
# https://github.com/jmoiron/johnny-cache/blob/master/johnny/cache.py

    """
Takes a Django 'query' object and returns all tables that will be used in
that query as a list. Note that where clauses can have their own
querysets with their own dependent queries, etc.
"""
    from django.db.models.sql.where import WhereNode
    from django.db.models.query import QuerySet

    tables = [v[0] for v in getattr(query, 'alias_map', {}).values()]

    def get_tables(node, tables):
        for child in node.children:
            if isinstance(child, WhereNode):  # and child.children:
                tables = get_tables(child, tables)
            elif not hasattr(child, '__iter__'):
                continue
            else:
                for item in (c for c in child if isinstance(c, QuerySet)):
                    tables += get_tables_for_query(item.query)
        return tables

    if query.where and query.where.children:
        where_nodes = [c for c in query.where.children if isinstance(c, WhereNode)]
        for node in where_nodes:
            tables += get_tables(node, tables)

    return list(set(tables))
