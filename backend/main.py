"""
FastAPI application for the AMR Genomics Dashboard backend.

The service exposes read endpoints for dashboard summaries and a write
endpoint for adding isolate records to the SQLite database.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import create_engine, text

from pydantic import BaseModel, Field

import pandas as pd


# create request body model
class AddIsolateRequest(BaseModel):
    """
    Request body for creating a new isolate record.

    The frontend submits this model to the ``/add_isolate`` endpoint to append a new isolate record to the database.
    """
    sample_id: str = Field(description='User-facing sample identifier supplied by the client.')
    city: str = Field(description='City where the isolate was collected.')
    state: str = Field(description='State where the isolate was collected.')
    latitude: float = Field(description='Latitude of the collection location.')
    longitude: float = Field(description='Longitude of the collection location.')
    organism: str = Field(description='Organism associated with the isolate.')
    collection_date: str = Field(description='Collection date in ``YYYY-MM-DD`` format.')
    num_contigs: int = Field(description='Number of contigs in the isolate assembly.')
    amr_gene: str = Field(description='AMR gene annotation reported by the client.')
    drug_class: str = Field(description='Antimicrobial drug class associated with the gene.')
    phenotype: str = Field(description='Phenotype associated with the gene.')


# initialize
print(os.getcwd())
DATABASE_URL = "sqlite:///genomics.db"
engine = create_engine(DATABASE_URL)
app = FastAPI()


# allow access from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# build endpoints
@app.get("/overview")
def get_overview():
    """
    Return summary counts for the dashboard overview.

    The response aggregates the current database contents into a compact JSON
    object for the overview cards and charts on the frontend.

    Returns:
        dict: A JSON-serializable mapping containing:

        - ``num_samples``: Total number of rows in ``Metadata``.
        - ``num_organisms``: Number of unique organisms.
        - ``organisms``: Mapping of organism name to sample count.
        - ``locations``: Mapping of ``"City, State"`` to sample count.
        - ``num_locations``: Number of unique location pairs.
        - ``num_amr_calls``: Total number of AMR annotations.
        - ``num_amr_genes``: Number of unique AMR genes.
    """
    result = {}

    # grab data from metadata table
    metadata_query = text("SELECT * FROM Metadata")
    metadata = pd.read_sql_query(metadata_query, con=engine)
    orgs = metadata.groupby("Organism").size().to_dict()
    num_orgs = len(orgs)
    locations = metadata.groupby(["City", "State"]).size().to_dict()
    num_locations = len(locations)
    formatted_locations = {
        f"{city}, {state}": count for (city, state), count in locations.items()
    }

    # grab data from the AMR table
    amr_query = text("SELECT * FROM AMR")
    amr_data = pd.read_sql_query(amr_query, con=engine)
    amr_calls = len(amr_data)
    amr_genes = amr_data["Gene"].unique()

    result["num_samples"] = len(metadata)
    result["num_organisms"] = num_orgs
    result["organisms"] = orgs
    result["locations"] = formatted_locations
    result["num_locations"] = num_locations
    result["num_amr_calls"] = amr_calls
    result["num_amr_genes"] = len(amr_genes)

    return result


@app.get("/amr")
def get_amr(organism: str = "All Organisms", location: str = None):
    """
    Return AMR drug-class counts, optionally filtered by organism.

    The endpoint joins ``AMR`` and ``Metadata`` so the frontend can display
    a compact summary of AMR activity across all organisms or within a single
    organism filter.

    Args:
        organism: Organism name to filter by. Use ``"All Organisms"`` to
            return unfiltered results (default).
        location: Location name to filter by. Returns first entry location if not provided.

    Returns:
        dict: A JSON-serializable mapping containing:

        - ``drug_class_counts``: Mapping of drug class to annotation count.
        - ``organisms``: List of distinct organism names in the database.
        - ''location_gene_counts'': Mapping of gene name to annotation count for the specified location, first location entry if not provided.
    """
    result = {}

    # grab AMR data for the selected orgnanism, or all
    if organism == "All Organisms":
        query = text("""SELECT DrugClass, Organism
                     FROM AMR
                     INNER JOIN Metadata ON AMR.RecordID = Metadata.RecordID
                     """)
        amr_data = pd.read_sql_query(query, con=engine)
    else:
        query = text("""
                    SELECT DrugClass, Organism
                    FROM AMR
                    INNER JOIN Metadata ON AMR.RecordID = Metadata.RecordID
                    WHERE Organism = :organism
                """)
        amr_data = pd.read_sql_query(query, con=engine, params={"organism": organism})
    
    drug_class_counts = amr_data.groupby("DrugClass").size().to_dict()

    # grab genes present by location
    if location:
        query = text("""
                     SELECT Gene
                     FROM AMR
                     INNER JOIN Metadata ON AMR.RecordID = Metadata.RecordID
                     WHERE City || ',' || State in (:location)
                 """)
        location_data = pd.read_sql_query(query, con=engine, params={"location": location})
    else:
        first_entry = pd.read_sql_query(text("SELECT City || ',' || State as location FROM Metadata LIMIT 1"), con=engine)
        query = text("""
                     SELECT Gene
                     FROM AMR
                     INNER JOIN Metadata ON AMR.RecordID = Metadata.RecordID
                     WHERE City || ',' || State in (:location)
                 """)
        location_data = pd.read_sql_query(query, con=engine, params={"location": first_entry["location"].iloc[0]})

    location_gene_counts = location_data.groupby("Gene").size().to_dict()


    # will need to do a separate query to get the organisms, since the amr_data may be filtered by organism
    org_query = text("SELECT DISTINCT Organism FROM Metadata")
    organisms = pd.read_sql_query(org_query, con=engine)
    organisms = sorted(organisms["Organism"].unique().tolist())

    result["drug_class_counts"] = drug_class_counts
    result["location_gene_counts"] = location_gene_counts
    result["organisms"] = organisms

    return result


@app.post("/add_isolate")
async def add_isolate(request: AddIsolateRequest):
    """
    Append a new isolate and its related records.

    The endpoint writes the submitted isolate into ``Metadata`` first, then uses
    the generated internal ``RecordID`` to insert the related assembly and AMR
    rows into ``IsolateData`` and ``AMR``.

    Args:
        request: AddIsolateRequest request body containing metadata, assembly, and AMR
            annotation fields.

    Returns:
        dict: A confirmation payload with a human-readable ``message`` field.
    """
    # add to metadata table
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO Metadata (SampleID, City, State, Latitude, Longitude, Organism, CollectionDate)
                VALUES (:sample_id, :city, :state, :latitude, :longitude, :organism, :collection_date)
            """),
            {
                "sample_id": request.sample_id,
                "city": request.city,
                "state": request.state,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "organism": request.organism,
                "collection_date": request.collection_date,
            },
        )

        record_id = conn.execute(text("SELECT last_insert_rowid()")).scalar_one()

        # add to isolate data table
        conn.execute(
            text("""
                INSERT INTO IsolateData (RecordID, Contigs)
                VALUES (:record_id, :num_contigs)
            """),
            {"record_id": record_id, "num_contigs": request.num_contigs},
        )

        # add to AMR table
        conn.execute(
            text("""
                INSERT INTO AMR (RecordID, Gene, DrugClass, Phenotype)
                VALUES (:record_id, :amr_gene, :drug_class, :phenotype)
            """),
            {
                "record_id": record_id,
                "amr_gene": request.amr_gene,
                "drug_class": request.drug_class,
                "phenotype": request.phenotype,
            },
        )
    
    return {"message": "Isolate added successfully."}
