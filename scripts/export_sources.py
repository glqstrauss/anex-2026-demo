import base64
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import duckdb
import typer

DEFAULT_DB_PATH = Path(__file__).parent.parent / "data/civil_service.duckdb"


@dataclass
class OpenDataExportConfig:
    name: str
    fourfour: str
    query: str | None = None
    format: str = "csv"

    @property
    def url(self):
        url = f"https://data.cityofnewyork.us/api/v3/views/{self.fourfour}/query.{self.format}"
        if self.query is not None:
            url += f"?query={quote_plus(self.query)}"
        return url


DATASETS = [
    OpenDataExportConfig(name="civil_service_titles", fourfour="nzjr-3966"),
    OpenDataExportConfig(
        name="civil_list",
        fourfour="ye3c-m4ga",
        query="select * where calendar_year = '2024'",  # about 300k rows
    ),
    OpenDataExportConfig(name="job_postings", fourfour="kpav-sd4t"),
]


def prepare_http(
    conn: duckdb.DuckDBPyConnection,
    api_key: str,
    api_key_secret: str,
    http_proxy: str | None,
):
    """Prepare HTTP authentication and proxy for DuckDB connection.

    DuckDB secrets are temporary (unless specified as 'PERSISTENT'), so no need
    to manually clean them up.
    """
    auth = f"Basic {base64.b64encode(f'{api_key}:{api_key_secret}'.encode()).decode()}"
    conn.execute(
        f"CREATE SECRET http_auth (TYPE http, EXTRA_HTTP_HEADERS MAP {{'Authorization': '{auth}'}})",
    )

    if http_proxy:
        conn.execute(f"CREATE SECRET http_proxy (TYPE http, HTTP_PROXY '{http_proxy}')")


def main(
    api_key: str = typer.Option(envvar="OPEN_DATA_API_KEY"),
    api_key_secret: str = typer.Option(envvar="OPEN_DATA_API_KEY_SECRET"),
    http_proxy: str | None = typer.Option(default=None, envvar="HTTP_PROXY"),
    db_path: Path = typer.Option(default=DEFAULT_DB_PATH, envvar="DB_PATH"),
):
    if not http_proxy:
        typer.echo(
            "HTTP_PROXY is not set. If running from a City network, this may cause connectivity issues.",
            color="yellow",
        )

    conn = duckdb.connect(db_path)
    conn.execute("INSTALL httpfs")
    conn.execute("LOAD httpfs")

    auth = f"Basic {base64.b64encode(f'{api_key}:{api_key_secret}'.encode()).decode()}"
    conn.execute(
        f"CREATE SECRET http_auth (TYPE http, EXTRA_HTTP_HEADERS MAP {{'Authorization': '{auth}'}})",
    )

    if http_proxy:
        conn.execute(f"CREATE SECRET http_proxy (TYPE http, HTTP_PROXY '{http_proxy}')")

    for dataset in DATASETS:
        typer.echo(f"Exporting {dataset.name} from {dataset.url}")
        conn.execute(
            f"CREATE OR REPLACE TABLE {dataset.name} AS SELECT * FROM read_csv('{dataset.url}', normalize_names=true)",
        )
        conn.execute(
            f"COMMENT ON TABLE {dataset.name} IS 'Exported from {dataset.url} at {datetime.now()}'"
        )

    typer.echo("Export complete.")
    typer.echo(
        str(
            conn.query(
                "from duckdb_tables() select table_name, estimated_size as row_count, column_count"
            )
        )
    )


if __name__ == "__main__":
    typer.run(main)
