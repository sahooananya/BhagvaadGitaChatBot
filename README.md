# 🧠 Bhagavad Gita AI Chatbot

An intelligent, full-stack AI chatbot that provides personalized spiritual guidance from the **Bhagavad Gita** based on the user's emotional state.

> “Whenever you feel lost, let wisdom guide you.” ✨

## 📜 Overview

This project goes beyond traditional search tools—it’s an **empathetic spiritual companion**. Users simply describe how they’re feeling, and the chatbot analyzes the emotion, links it to a deeper **spiritual theme** (e.g., *anger* → *self-control*), and returns a relevant **shloka** from the *Bhagavad Gita*.

---

## 🚀 Key Features

- **🧠 Emotion-Aware Responses**  
  Detects emotions in real-time using Hugging Face Transformers.

- **📚 Intelligent Verse Tagging**  
  A zero-shot classifier maps 700+ verses to spiritual themes.

- **🖥️ Full-Stack Architecture**  
  React frontend + FastAPI backend with MongoDB Atlas.

- **📱 Clean, Responsive UI**  
  Optimized for both desktop and mobile experiences.

- **☁️ Cloud Deployment**  
  Frontend on **Vercel**, backend on **Render**.

---

## 🛠️ Tech Stack

| Layer        | Technology |
|--------------|------------|
| **Frontend** | React.js, Axios |
| **Backend**  | Python, FastAPI |
| **Database** | MongoDB Atlas |
| **AI/NLP**   | Hugging Face Transformers (`roberta-base-go_emotions`, `bart-large-mnli`) |
| **Deployment** | Vercel (frontend), Render (backend) |

---

## 📁 Project Structure

```

bhagavad-gita-ai/
├── backend/         # FastAPI app, NLP models, DB logic
├── frontend/        # React app and chat UI
├── .gitignore       # Git ignore rules
└── README.md        # This file!

````

---

## ⚙️ Setup and Installation (Run Locally)

### 🧰 Prerequisites

- Git  
- Node.js (v16+)  
- Python (v3.9+)  
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account  

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sahooananya/BhagwatGitaChatBot.git
cd BhagwatGitaChatBot
````

---

### 2️⃣ Backend Setup (FastAPI)

```bash
cd backend

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.\.venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

📄 Create a `.env` file inside the `backend/` folder:

```
MONGO_URI="mongodb+srv://<username>:<password>@cluster.mongodb.net/<dbname>?retryWrites=true&w=majority"
```

📥 Populate database (run once):

```bash
python load_data.py
python tag_data.py   # This step is slow; tags verses using AI
```

▶️ Run the backend server:

```bash
uvicorn main:app --reload
```

Backend runs at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 3️⃣ Frontend Setup (React)

Open a **new terminal**:

```bash
cd frontend
npm install
npm start
```

Frontend opens at: [http://localhost:3000](http://localhost:3000)

---

## 📡 API Reference

### `POST /suggest`

Analyzes emotion, maps to a spiritual theme, and returns a matching shloka.

#### 🔸 Request Body

```json
{
  "text": "I am feeling very anxious about my future.",
  "language": "english"
}
```

#### 🔹 Response

```json
{
  "chapter": 2,
  "verse": 47,
  "sanskrit": "कर्मण्येवाधिकारस्ते...",
  "translation": "You have a right to perform your prescribed duties...",
  "spiritual_theme": "surrender"
}
```

---

## 🤝 Contribution Guidelines

1. Fork this repo
2. Create a new branch (`git checkout -b feature-name`)
3. Make your changes
4. Submit a PR 🙌


## 🙏 Acknowledgements

* Bhagavad Gita – Sacred Hindu scripture
* Hugging Face – NLP models
* MongoDB Atlas – Cloud-hosted NoSQL DB
* React, FastAPI – Frontend & backend technologies
* You – For exploring this project ❤️

---

> *"Let the wisdom of ancient scripture meet the intelligence of modern AI."*

```

