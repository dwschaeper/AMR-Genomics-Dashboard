import sqlite3
import random
from datetime import datetime, timedelta
import argparse


def parse() -> int:
    """
    Parse arguments for the script.

    Returns:
        int: Number of samples to generate (default: 1000)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--samples", type=int, default=1000, help="Number of samples to generate"
    )

    args = parser.parse_args()

    return args.samples


if __name__ == "__main__":
    """
    This script creates an SQLite database called "genomics.db" with three tables: Metadata, IsolateData, and AMR. 
    It populates the tables with random data for the specified number of samples, including locations, organisms, collection dates, contig counts, and antimicrobial resistance (AMR) genes.
    """
    # get number of samples
    samples = parse()

    # initalialize variables for locations, organisms, and AMR catalog
    locations = [
        ("Indianapolis", "Indiana", 39.7684, -86.1581),
        ("Fort Wayne", "Indiana", 41.0793, -85.1394),
        ("Chicago", "Illinois", 41.8781, -87.6298),
        ("Springfield", "Illinois", 39.7817, -89.6501),
        ("Milwaukee", "Wisconsin", 43.0389, -87.9065),
        ("Madison", "Wisconsin", 43.0731, -89.4012),
        ("Detroit", "Michigan", 42.3314, -83.0458),
        ("Lansing", "Michigan", 42.7325, -84.5555),
        ("Minneapolis", "Minnesota", 44.9778, -93.2650),
        ("Saint Paul", "Minnesota", 44.9537, -93.0900),
        ("Des Moines", "Iowa", 41.5868, -93.6250),
        ("Cedar Rapids", "Iowa", 41.9779, -91.6656),
        ("Columbus", "Ohio", 39.9612, -82.9988),
        ("Cleveland", "Ohio", 41.4993, -81.6944),
        ("Kansas City", "Missouri", 39.0997, -94.5786),
        ("St. Louis", "Missouri", 38.6270, -90.1994),
    ]
    organisms = [
        "Escherichia coli",
        "Salmonella enterica",
        "Listeria monocytogenes",
        "Campylobacter jejuni",
        "Staphylococcus aureus",
        "Klebsiella pneumoniae",
    ]
    amr_catalog = [
        ("blaCTX-M-15", "Beta-lactam", "Resistant"),
        ("blaKPC-2", "Carbapenem", "Resistant"),
        ("tetA", "Tetracycline", "Resistant"),
        ("ermB", "Macrolide", "Resistant"),
        ("aac(6')-Ib", "Aminoglycoside", "Resistant"),
        ("qnrS1", "Fluoroquinolone", "Resistant"),
        ("mcr-1", "Colistin", "Resistant"),
        ("vanA", "Glycopeptide", "Resistant"),
    ]

    # make database and tables
    conn = sqlite3.connect("genomics.db")
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS AMR;
    DROP TABLE IF EXISTS IsolateData;
    DROP TABLE IF EXISTS Metadata;

    CREATE TABLE Metadata (
        ID TEXT PRIMARY KEY,
        City TEXT,
        State TEXT,
        Latitude REAL,
        Longitude REAL,
        Organism TEXT,
        CollectionDate TEXT
    );

    CREATE TABLE IsolateData (
        ID TEXT PRIMARY KEY,
        Contigs INTEGER,
        FOREIGN KEY(ID) REFERENCES Metadata(ID)
    );

    CREATE TABLE AMR (
        AMR_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID TEXT,
        Gene TEXT,
        DrugClass TEXT,
        Phenotype TEXT,
        FOREIGN KEY(ID) REFERENCES Metadata(ID)
    );
    """)

    # fill in random data
    start = datetime(2020, 1, 1)

    for i in range(samples):
        sample_id = f"S{i + 1:04d}"

        city, state, lat, lon = random.choice(locations)

        organism = random.choice(organisms)

        collection_date = (start + timedelta(days=random.randint(0, 2000))).strftime(
            "%Y-%m-%d"
        )

        contigs = random.randint(20, 450)

        cur.execute(
            """
            INSERT INTO Metadata
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (sample_id, city, state, lat, lon, organism, collection_date),
        )

        cur.execute(
            """
            INSERT INTO IsolateData
            VALUES (?, ?)
        """,
            (sample_id, contigs),
        )

        # Give each isolate 0–4 AMR genes
        for gene, drug_class, phenotype in random.sample(
            amr_catalog, random.randint(0, 4)
        ):
            cur.execute(
                """
                INSERT INTO AMR (
                    ID,
                    Gene,
                    DrugClass,
                    Phenotype
                )
                VALUES (?, ?, ?, ?)
            """,
                (sample_id, gene, drug_class, phenotype),
            )

    conn.commit()
    conn.close()

    print("Created genomics.db")
