# 🤖 Autonomous Data Scientist Agent

An intelligent, self-healing machine learning agent designed to automate the entire data science lifecycle. Upload any CSV or Excel dataset, chat with the AI to select your target variable, and instantly generate interactive dashboards, notebook templates, and automated ML reports.

The project features a sleek, professional **navy blue and white** UI, high-performance automated ML pipeline evaluation (comparing 5 models), and Gemini-powered business insights.

---

## 🚀 Key Features

*   **Drag & Drop Data Ingestion:** Upload CSV, XLSX, or XLS files up to 50MB.
*   **Automated Data Profiling:** Instantly calculates row/column counts, missing values, duplicates, outliers, class imbalances, and data types.
*   **Predictive Model Preview:** Provides an instant preview of classification performance (estimated accuracy, top 3 feature importances) before running the full pipeline.
*   **Five-Model Pipeline Comparison:** Automatically trains and compares 5 different ML models:
    *   *Random Forest*
    *   *XGBoost*
    *   *Gradient Boosting*
    *   *Decision Trees*
    *   *K-Nearest Neighbors*
*   **Interactive HTML Dashboard:** Generates business-ready dashboards containing:
    *   *Distribution Charts*
    *   *Feature Correlation Heatmaps*
    *   *Interactive 3D Feature Space Scatter & Surface plots*
    *   *Interactive ROC and Precision-Recall Curves*
    *   *Interactive Confusion Matrices (Self-healing & optimized for high-cardinality data)*
*   **AI-Powered Narrative Insights:** Connects with Google Gemini AI to write custom narrative business reports, statistical interpretations, and actionable insights.
*   **Local Session Manager:** Save, load, and export historical analysis sessions directly inside your browser cache.

---

## 🛠️ Technology Stack

*   **Backend API:** FastAPI (Python), Uvicorn, Scikit-Learn, Pandas, NumPy, OpenPyXL, Plotly, Google GenAI SDK
*   **Frontend UI:** React, TailwindCSS, Lucide Icons, HTML5 Drag & Drop

---

## 🏃 Getting Started

### Prerequisites

Ensure you have the following installed locally:
*   [Python 3.9+](https://www.python.org/downloads/)
*   [Node.js 18+](https://nodejs.org/)
*   *Optional:* A Google Gemini API Key (for narrative generation)

---

### 1. Run the Backend (FastAPI Server)

1.  Navigate into the `backend/` directory:
    ```bash
    cd backend
    ```
2.  Install python packages:
    ```bash
    pip install -r requirements.txt
    ```
3.  *(Optional)* Create a `.env` file in the `backend/` root directory and set your API key:
    ```env
    GOOGLE_API_KEY="your-gemini-api-key-here"
    ```
4.  Start the FastAPI server:
    ```bash
    python main.py
    ```
    The API server will run on **`http://localhost:8000`**. You can verify the health check at [http://localhost:8000/docs](http://localhost:8000/docs).

---

### 2. Run the Frontend (React UI)

1.  Open a new terminal and navigate into the `frontend/` directory:
    ```bash
    cd frontend
    ```
2.  Install package dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm start
    ```
    The React application will open automatically in your browser at **`http://localhost:3000`**.

---

## 🛡️ Robustness & Self-Healing Features

This application includes specific optimizations to prevent freezes and memory overflows under complex conditions:
*   **High-Cardinality Target Columns:** If your target variable contains many unique classes (e.g. predicting a `movie` name out of 1,500 rows), the application automatically disables heavy HTML tables and large Plotly text annotations, rendering a clean summaries and preventing the browser and backend from crashing.
*   **Robust Correlation Analysis:** Evaluates correlation matrices safely by encoding text values to numeric integers dynamically, avoiding runtime `ValueErrors`.
*   **Submodule-Free Packaging:** All React components, assets, and dependencies are packed directly into the repository index for simple deployment and code tracking.
