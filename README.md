# Real-Time Poll Rooms

A full-stack real-time polling application built using FastAPI, React (Vite), WebSockets, and SQLite.

---

## 🚀 Features

- Create polls with multiple options
- Shareable poll links
- Real-time vote updates using WebSockets
- Live viewer count
- Poll expiry system
- Rate limiting
- Duplicate vote prevention
- Persistent database storage

---

## 🛡 Fairness / Anti-Abuse Mechanisms

1. Duplicate Vote Prevention  
   Each vote generates a unique hash using:
   - IP address
   - User-Agent
   - Poll ID  
   This prevents multiple votes from the same device.

2. Rate Limiting  
   Voting is limited to 5 requests per minute per IP using SlowAPI.

---

## ⚙️ Tech Stack

Backend:
- FastAPI
- SQLAlchemy
- SQLite
- WebSockets
- SlowAPI (rate limiting)

Frontend:
- React (Vite)
- TailwindCSS
- Axios

---

## 🏗 Architecture

Client connects via WebSocket to:
ws://server/ws/{poll_id}

When a vote is cast:
1. Backend validates vote
2. Stores in database
3. Broadcasts updated results to all connected clients

---

## 📌 Known Limitations

- IP-based uniqueness can be bypassed via different networks
- SQLite used for simplicity (can be upgraded to PostgreSQL)
- LocalStorage used for client-side vote memory
