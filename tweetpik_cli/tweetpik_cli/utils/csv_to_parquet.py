# https://stackoverflow.com/questions/26124417/how-to-convert-a-csv-file-to-parquet
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def to_parquet(
    csv_file: str, parquet_file: str, chunksize: int = 100_000, sep: str = "\t"
) -> None:
    # csv_file = '/path/to/my.tsv'
    # parquet_file = '/path/to/my.parquet'
    # chunksize = 100_000

    csv_stream = pd.read_csv(csv_file, sep=sep, chunksize=chunksize, low_memory=False)

    for i, chunk in enumerate(csv_stream):
        print("Chunk", i)
        if i == 0:
            # Guess the schema of the CSV file from the first chunk
            parquet_schema = pa.Table.from_pandas(df=chunk).schema
            # Open a Parquet file for writing
            parquet_writer = pq.ParquetWriter(
                parquet_file, parquet_schema, compression="snappy"
            )
        # Write CSV chunk to the parquet file
        table = pa.Table.from_pandas(chunk, schema=parquet_schema)
        parquet_writer.write_table(table)

    parquet_writer.close()
