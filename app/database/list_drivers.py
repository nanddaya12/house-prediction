import pyodbc


def list_sql_server_drivers():
    """Return the installed SQL Server ODBC drivers."""
    try:
        return pyodbc.drivers()
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {"error": str(exc)}


if __name__ == "__main__":
    print(list_sql_server_drivers())
