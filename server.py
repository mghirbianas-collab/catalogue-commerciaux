import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from uvicorn import run
import os

app = FastAPI(title="Catalogue API pour Commerciaux")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect("catalogue.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            designation TEXT,
            prix REAL,
            stock INTEGER
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM articles")
    if cursor.fetchone()[0] == 0:
        data = [
            ("ART001", "Article Exemple A", 15.500, 120),
            ("ART002", "Article Exemple B", 45.000, 15),
            ("ART003", "Article Exemple C", 8.750, 300)
        ]
        cursor.executemany("INSERT INTO articles (code, designation, prix, stock) VALUES (?, ?, ?, ?)", data)
        conn.commit()
    conn.close()

# Nouvelle route : Distribue l'interface HTML directement depuis le même port
@app.get("/")
async def read_index():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"erreur": f"Fichier index.html introuvable. Dossier actuel : {BASE_DIR}"}
@app.get("/api/articles")
def get_articles():
    try:
        conn = sqlite3.connect("catalogue.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT code, designation, prix, stock FROM articles")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    init_db()
    run(app, host="0.0.0.0", port=8000)
