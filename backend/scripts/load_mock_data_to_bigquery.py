from __future__ import annotations

import argparse
import json
from pathlib import Path


TABLES = [
    "incidents",
    "weather_conditions",
    "hospitals",
    "hospital_capacity",
    "hospital_inventory",
    "hospital_staffing",
    "suppliers",
    "supplier_inventory",
    "traffic_routes",
    "transport_options",
    "emergency_contacts",
    "datasource_status",
]


def load_table(client, project: str, dataset: str, table_name: str, records: list[dict]) -> None:
    table_id = f"{project}.{dataset}.{table_name}"
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    ndjson = "\n".join(json.dumps(record) for record in records).encode("utf-8")
    job = client.load_table_from_file(
        file_obj=BytesIO(ndjson),
        destination=table_id,
        job_config=job_config,
    )
    job.result()
    print(f"Loaded {len(records)} rows into {table_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load CrisisFlow mock JSON data into BigQuery.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--dataset", default="crisisflow_demo")
    parser.add_argument("--data-dir", default=str(Path(__file__).resolve().parents[1] / "app" / "data"))
    parser.add_argument(
        "--exclude-table",
        action="append",
        default=[],
        help=(
            "Table to skip. Can be passed more than once. "
            "Use --exclude-table supplier_inventory when Fivetran owns that table."
        ),
    )
    args = parser.parse_args()

    client = bigquery.Client(project=args.project)
    dataset_ref = bigquery.Dataset(f"{args.project}.{args.dataset}")
    dataset_ref.location = "US"
    client.create_dataset(dataset_ref, exists_ok=True)

    data_dir = Path(args.data_dir)
    excluded = set(args.exclude_table)
    for table_name in TABLES:
        if table_name in excluded:
            print(f"Skipped {table_name}")
            continue
        path = data_dir / f"{table_name}.json"
        with path.open("r", encoding="utf-8") as handle:
            records = json.load(handle)
        load_table(client, args.project, args.dataset, table_name, records)


if __name__ == "__main__":
    from io import BytesIO

    from google.cloud import bigquery

    main()
