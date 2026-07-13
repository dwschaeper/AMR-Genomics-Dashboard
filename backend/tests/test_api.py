from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_overview():
    """
    Test the /overview endpoint
    """
    response = client.get("/overview")

    assert response.status_code == 200

    data = response.json()

    assert "organisms" in data
    assert "locations" in data
    assert data["num_samples"] >= 0
    assert data["num_organisms"] >= 0
    assert data["num_locations"] >= 0
    assert data["num_amr_calls"] >= 0
    assert data["num_amr_genes"] >= 0


def test_amr():
    """
    Test the /amr endpoint
    """
    response = client.get("/amr")

    assert response.status_code == 200

    data = response.json()

    assert "drug_class_counts" in data
    assert "organisms" in data


def test_amr_organism():
    """
    Test the /amr endpoint with organism parameter
    """
    response = client.get("/amr/?organism=Escherichia%20coli")

    assert response.status_code == 200

    data = response.json()

    assert "drug_class_counts" in data


def test_amr_location():
    """
    Test the /amr endpoint with the location parameter
    """
    response = client.get("/amr/?location=Indianapolis,Indiana")

    assert response.status_code == 200

    data = response.json()

    assert "drug_class_counts" in data
    assert "location_gene_counts" in data
    

def test_add_isolate():
    """
    Test the /add_isolate endpoint
    """
    payload = {
        "sample_id": "api_test",
        "city": "test",
        "state": "test",
        "latitude": 1,
        "longitude": 1,
        "organism": "test",
        "collection_date": "test",
        "num_contigs": 500,
        "amr_gene": "test",
        "drug_class": "test",
        "phenotype": "test",
    }

    response = client.post("/add_isolate", json=payload)

    assert response.status_code == 200
