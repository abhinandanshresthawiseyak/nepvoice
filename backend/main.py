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
app = FastAPI()

# Enable CORS so React can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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