# Genomics Dashboard

A full-stack genomics dashboard built with FastAPI and React for exploring pathogen sequencing metadata and antimicrobial resistance (AMR) results. This provides interactive visualizations, summary statistics, and filtering capabilities through a REST API.

## Features

* Interactive dashboard for genomics sample metadata
* Summary statistics for sequencing datasets
* Organism distribution visualization
* Geographic distribution visualization
* AMR gene and drug class summaries
* Filter AMR results by organism
* REST API built with FastAPI
* Interactive plots using Plotly

## Tech Stack

### Backend

* Python
* FastAPI
* SQLite

### Frontend

* React
* Vite
* Plotly.js

## Project Structure

```text
genomics-dashboard/
├── backend/
├──
└── frontend/
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt

python create_genomics_db.py
uvicorn main:app --reload
```

The backend will be available at:

```
http://localhost:8000
```

and the API documentation by SwaggerUI will be available at:
```
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:

```
http://localhost:5173
```


## License

This project is available under the MIT License.
