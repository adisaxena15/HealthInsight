# Health Insight

**Database Health Insight** is a secure, cloud-integrated web application that connects to a structured medical database hosted on Google Cloud Platform (GCP). It provides authenticated access to patient diagnosis records and question-answer pairs for clinical use, combining deep query capabilities with intuitive data visualization to surface meaningful patterns from large datasets.
![image](https://github.com/user-attachments/assets/9c0caf99-f624-4e72-b65c-e68d5856dada)

## 🔍 What It Does

The system is designed to assist in understanding large-scale medical datasets by enabling:

- **Secure access** to patient and QA records using **OAuth2.0 authentication**
- **Fast and flexible search** across diagnosis notes and question-answer data using **Elasticsearch** indexing
- **Interactive data exploration** through a **word graph visualization** of relationships between diagnoses, symptoms, and medical keywords
- **Advanced SQL queries** over the GCP-hosted database to extract insights like frequently co-occurring conditions or most asked medical questions

The backend handles API routing, search processing, and user sessions, while the frontend focuses on delivering an interactive and insightful user experience for clinical researchers or data analysts.

## ⚙️ How to Run

1. **Clone and install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2.**Set up environment variables (credentials, GCP configs, and OAuth keys)**
  ```bash
DB_URI=...
GCP_PROJECT_ID=...
OAUTH_CLIENT_ID=...
OAUTH_CLIENT_SECRET=...
  ```
3.**Start the Backend and Frontend**
  ```bash
npm run start
python app.py
  ```
## 🧠 Technologies Used

- **Google Cloud SQL** – Stores diagnosis and QA data
- **Elasticsearch** – Enables high-speed, full-text search capabilities
- **OAuth2.0** – Secures user login and session management
- **Flask / FastAPI** – Backend server and API routing
- **D3.js / Plotly / NetworkX** – For generating dynamic word graph visualizations

## 🧪 Example Use Cases

- Identify symptom clusters that frequently appear together in patient records
- Search all past patient cases involving a specific condition or treatment
- Explore how different terms are semantically connected via graph relationships
- Enable medical students or researchers to query QA pairs by keyword or topic
