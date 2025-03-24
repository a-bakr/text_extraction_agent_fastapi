from app.main import app

# For Vercel serverless deployment
app = app

# ASGI handler
handler = app 