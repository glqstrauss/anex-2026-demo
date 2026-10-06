import base64
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import duckdb
import typer

DEFAULT_SNAPSHOT_DIR = Path(__file__).parent.parent / "data/snapshots"


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
    snapshot_dir: Path = typer.Option(default=DEFAULT_SNAPSHOT_DIR, envvar="SNAPSHOT_DIR"),
):
    """Snapshot NYC Open Data sources to Parquet files, one per dataset.

    The snapshots are committed to the repo so that dbt builds (local, CI and
    prod) all run against identical source data without network access.
    """
    if not http_proxy:
        typer.echo(
            "HTTP_PROXY is not set. If running from a City network, this may cause connectivity issues.",
            color="yellow",
        )

    snapshot_dir.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect()
    conn.execute("INSTALL httpfs")
    conn.execute("LOAD httpfs")

    prepare_http(conn, api_key, api_key_secret, http_proxy)

    for dataset in DATASETS:
        path = snapshot_dir / f"{dataset.name}.parquet"
        typer.echo(f"Exporting {dataset.name} from {dataset.url} to {path}")
        conn.execute(
            f"""
            COPY (SELECT * FROM read_csv('{dataset.url}', normalize_names=true))
            TO '{path}' (
                FORMAT parquet,
                COMPRESSION zstd,
                KV_METADATA {{source_url: '{dataset.url}', exported_at: '{datetime.now().isoformat()}'}}
            )
            """
        )

    typer.echo("Export complete.")
    typer.echo(
        str(
            conn.query(
                f"""
                select
                    parse_filename(filename, true) as dataset,
                    count(*) as row_count
                from read_parquet('{snapshot_dir}/*.parquet', filename=true, union_by_name=true)
                group by all
                order by dataset
                """
            )
        )
    )


if __name__ == "__main__":
    typer.run(main)
