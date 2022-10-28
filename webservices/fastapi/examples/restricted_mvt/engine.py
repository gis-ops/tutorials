from sqlmodel import create_engine

DATABASE_URL = "postgresql://<user>:<password>@localhost:5452/gis"

engine = create_engine(DATABASE_URL, echo=True)
