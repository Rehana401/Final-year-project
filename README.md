# SecurBank: Fraud Detection in Online Banking System

![SecurBank Banner](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-19.0-61DAFB.svg)
![Flask](https://img.shields.io/badge/Flask-API-black.svg)

SecurBank is a robust, full-stack machine learning web application designed to detect and prevent fraudulent transactions in online banking environments. It leverages state-of-the-art ensemble models (Random Forest and XGBoost) connected to a sleek React 19 frontend and a Flask backend.

## 🌟 Key Features

* **Real-time Fraud Detection**: Instantly evaluates transactions using trained ML models to assign risk scores and confidence intervals.
* **Model Training Wizard**: An integrated dashboard to tune, cross-validate, and deploy machine learning pipelines directly from the UI.
* **Dataset Insights**: Explore the transaction dataset through interactive charts and correlation matrices.
* **Interactive Dashboard**: Track total analyses, average risk scores, and system history.
* **Role-Based Access Control**: Secure JWT-based authentication distinguishing between standard Users and Administrators.

## 🛠️ Technology Stack

* **Frontend**: React 19, Vite, Framer Motion, Lucide Icons, Vanilla CSS (Glassmorphism UI)
* **Backend**: Flask, Flask-JWT-Extended, Flask-CORS
* **Database**: SQLite (SQLAlchemy / raw SQL)
* **Machine Learning**: Scikit-Learn, XGBoost, Imbalanced-Learn (SMOTE), Pandas, Numpy

---

## 🚀 How to Run the Project

The application is split into two parts: the Flask API backend and the Vite React frontend. You will need **two separate terminal windows** to run the complete stack.

### Part 1: Backend Setup (Python)

1. **Open a terminal** and navigate to the root directory of the project.
2. **Create a virtual environment** (optional but highly recommended):
   ```bash
   python -m venv .venv
   ```
3. **Activate the virtual environment**:
   * On **Windows**:
     ```bash
     .\.venv\Scripts\activate
     ```
   * On **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```
4. **Install the required Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the Flask server**:
   ```bash
   python app.py
   ```
   *The backend will start running at `http://localhost:5000`.*

### Part 2: Frontend Setup (Node.js/React)

1. **Open a SECOND terminal** and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. **Install Node modules**:
   ```bash
   npm install
   ```
3. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   *The frontend will start running at `http://localhost:5173`.*

---

## 🔑 Default Accounts

If the database is initialized for the first time, you can register a new account through the `/signup` page.

To access **Admin-only** pages (like Model Training, Dataset Insights, and Manage Users), you will need to register an account and elevate its privileges via the SQLite database, or use the pre-configured admin account if one exists in the dataset.

## 📂 Project Structure

* `/core`: Core system logic including prediction engine, feature extraction, and database management.
* `/ml`: Machine learning pipelines including preprocessors, data managers, and model trainers.
* `/models`: Pickled (.pkl) files of the trained models and scalers.
* `/routes`: Flask API blueprints for authentication, user management, and admin controls.
* `/frontend`: The complete Vite + React 19 frontend application.
