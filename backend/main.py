from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import create_engine, text

from pydantic import BaseModel

import pandas as pd


# create request body model
class AddIsolateRequest(BaseModel):
    sample_id: str
    city: str
    state: str
    latitude: float
    longitude: float
    organism: str
    collection_date: str
    num_contigs: int
    amr_gene: str
    drug_class: str
    phenotype: str


# initialize
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
    Get an overview of the database. Used to generate the initial overview in the dashboard.

    Returns json of num_samples, num_organisms, organisms (dict of organism: count), and locations (dict of "City, State": count)
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
def get_amr(organism: str = "All Organisms"):
    """
    Get the AMR data. Used to generate the AMR table in the dashboard.

    Returns json of AMR data.
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

    # will need to do a separate query to get the organisms, since the amr_data may be filtered by organism
    org_query = text("SELECT DISTINCT Organism FROM Metadata")
    organisms = pd.read_sql_query(org_query, con=engine)
    organisms = sorted(organisms["Organism"].unique().tolist())

    result["drug_class_counts"] = drug_class_counts
    result["organisms"] = organisms

    return result


@app.post("/add_isolate")
async def add_isolate(request: AddIsolateRequest):
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
