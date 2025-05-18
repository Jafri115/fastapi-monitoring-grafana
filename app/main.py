from fastapi import FastAPI, HTTPException, Depends
from prometheus_fastapi_instrumentator import Instrumentator
import time
import random
import asyncio
import aiosqlite

# --- Database Setup (Simple In-Memory for Demo) ---
DATABASE_URL = ":memory:" # Using in-memory SQLite

async def get_db():
    # The connection string for aiosqlite in-memory is just ":memory:"
    # or you can use a named in-memory db like "file:memdb1?mode=memory&cache=shared" if sharing across connections is needed (not here)
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL
            )
        """)
        await db.commit()
        yield db

app = FastAPI(
    title="Demo API for Monitoring",
    description="A simple API to demonstrate FastAPI, Prometheus, and Grafana.",
    version="0.1.0",
)

# --- Metrics ---
Instrumentator().instrument(app).expose(app)

# --- API Endpoints ---
@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, db: aiosqlite.Connection = Depends(get_db)):
    latency = random.uniform(0.05, 0.3)
    await asyncio.sleep(latency)

    if random.random() < 0.1:
        raise HTTPException(status_code=500, detail="Internal Server Error Simulation")
    if item_id == 99:
        raise HTTPException(status_code=404, detail="Item 99 not found (Simulated)")

    cursor = await db.execute("SELECT id, name, value FROM items WHERE id = ?", (item_id,))
    item = await cursor.fetchone()
    await cursor.close()

    if item:
        return {"item_id": item[0], "name": item[1], "value": item[2]}
    else:
        # For demo, create if not found to ensure DB interaction
        await db.execute("INSERT INTO items (name, value) VALUES (?, ?)", (f"Item {item_id}", random.uniform(1,100)))
        await db.commit()
        return {"item_id": item_id, "name": f"Item {item_id}", "value": "Newly Created (was not found)"}


@app.post("/items/")
async def create_item(name: str, value: float, db: aiosqlite.Connection = Depends(get_db)):
    latency = random.uniform(0.1, 0.4)
    await asyncio.sleep(latency)

    cursor = await db.execute("INSERT INTO items (name, value) VALUES (?, ?)", (name, value))
    await db.commit()
    item_id = cursor.lastrowid
    await cursor.close()
    return {"id": item_id, "name": name, "value": value, "message": "Item created successfully"}


@app.get("/heavy-task")
async def heavy_task():
    duration = random.uniform(0.5, 1.5)
    await asyncio.sleep(duration)
    return {"message": f"Heavy task completed in {duration:.2f} seconds."}

@app.get("/error-prone")
async def error_prone_endpoint():
    if random.random() < 0.75:
        raise HTTPException(status_code=503, detail="Service Temporarily Unavailable (Simulated)")
    return {"message": "Sometimes I work!"}

# No need for if __name__ == "__main__": block when running with Docker CMD