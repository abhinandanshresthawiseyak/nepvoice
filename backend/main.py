# from app.database.database import init_db

# def main():
#     print("Initializing database...")
#     init_db()
#     print("Database initialized successfully!")

# if __name__ == "__main__":
#     main()


################################################################################above commented code works for database creation

# from fastapi import FastAPI
# from fastapi.responses import HTMLResponse
# from app.database.database import init_db
# from app.api.v1.endpoints import oauth

# app = FastAPI()

# @app.on_event("startup")
# def startup_event():
#     init_db()  # Ensure tables exist on startup

# # ✅ Root-level homepage
# @app.get("/")
# async def root():
#     return HTMLResponse('<a href="/auth/login">Login with Google</a>')

# # ✅ OAuth router under /auth
# app.include_router(oauth.router, prefix="/auth")


#############################above code works for database creation and oauth login


# from fastapi import FastAPI
# from fastapi.responses import HTMLResponse
# from app.database.database import init_db
# from app.api.v1.endpoints import oauth, credit

# app = FastAPI()

# @app.on_event("startup")
# def startup_event():
#     init_db()

# @app.get("/")
# async def root():
#     return HTMLResponse('<a href="/auth/login">Login with Google</a>')

# # Include routers
# app.include_router(oauth.router, prefix="/auth")
# app.include_router(credit.router, prefix="/credits")


###############################above code works for database creation and oauth login and credit purchase simulation


from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.database.database import init_db
from app.api.v1.endpoints import oauth, credit, features, admin
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import SECRET_KEY
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1.endpoints.feature import chatbot, callbot, asr, tts

app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
async def root():
    return HTMLResponse('<a href="/auth/login">Login with Google</a>')

# Include routers
app.include_router(oauth.router, prefix="/auth")
app.include_router(credit.router, prefix="/credits")
app.include_router(features.router, prefix="")
app.include_router(admin.router, prefix="")
app.include_router(chatbot.router, prefix="/feature/chatbot")
app.include_router(callbot.router, prefix="/feature/callbot")
app.include_router(asr.router, prefix="/feature/asr")
app.include_router(tts.router, prefix="/feature/tts")