# 🏥 AI-CareMesh: AI-Powered Healthcare Recommendation System

## 📌 Project Overview

AI-CareMesh is an intelligent healthcare web application that leverages Artificial Intelligence to recommend suitable doctors and hospitals based on patient symptoms. It analyzes user input using machine learning algorithms and provides accurate, real-time recommendations along with seamless appointment booking.

---

## 🚀 Key Features

### 🤖 AI Capabilities

* Symptom analysis using **TF-IDF** and **Cosine Similarity**
* Smart recommendation engine for hospitals and doctors
* Case-based learning approach

### 👤 User Features

* Secure user registration & login (JWT Authentication)
* Search doctors by specialization
* Book appointments instantly
* View appointment history
* Upload medical cases for AI analysis

### 🛠 Admin Features

* Manage hospitals and doctors
* Monitor users and appointments
* View analytics dashboard

---

## 🛠️ Tech Stack

| Layer             | Technology            |
| ----------------- | --------------------- |
| 🎨 Frontend       | HTML, CSS, JavaScript |
| ⚙️ Backend        | Python (Flask)        |
| 🗄 Database       | MySQL                 |
| 🤖 AI/ML          | scikit-learn          |
| 🔐 Authentication | JWT, bcrypt           |
| 🔗 ORM            | SQLAlchemy            |

---

## 📸 Screenshots

<!-- Add your screenshots inside a folder named 'screenshots' -->

<!-- Example:
![Home](screenshots/home.png)
![Dashboard](screenshots/dashboard.png)
-->

---

## 📋 Prerequisites

* Python 3.8 or above
* MySQL Server
* pip (Python package manager)
* Virtual Environment (recommended)

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

git clone https://github.com/yourusername/ai-caremesh.git
cd ai-caremesh

### 2️⃣ Install Dependencies

pip install -r requirements.txt

### 3️⃣ Setup Environment Variables

Create a `.env` file in the root directory:

SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URL=mysql+pymysql://username:password@localhost/dbname

### 4️⃣ Configure Database

* Create a MySQL database
* Import required tables
* Update credentials in `.env`

### 5️⃣ Run the Application

python app.py

---

## 📂 Project Structure

ai-caremesh/
│── templates/        # HTML files
│── static/           # CSS, JavaScript
│── models/           # AI models
│── uploads/          # Uploaded files
│── app.py            # Main Flask app
│── requirements.txt

---

## 🔐 Security Practices

* Password hashing using **bcrypt**
* JWT-based authentication
* Secrets stored in `.env` file
* `.env` excluded using `.gitignore`

---

## 🌐 Future Improvements

* Cloud deployment (AWS / Render)
* Mobile app integration
* Advanced AI model
* Real-time chat system

---

## 👨‍💻 Author

Sanjee Vani

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
