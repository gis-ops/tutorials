import morecantile
from buildpg import asyncpg
from fastapi import FastAPI, Path, HTTPException, Depends
from morecantile import Tile
from sqlalchemy import func
from sqlmodel import Session, select
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware


from auth import Authorizer
from engine import DATABASE_URL, engine
from models import Users, UsersReq
from jwtoken import create_token

origins = [
    "http://localhost",
    "http://localhost:5173",
]


vectortile_app = FastAPI()

vectortile_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@vectortile_app.on_event("startup")
async def startup_event():
    vectortile_app.state.pool = await asyncpg.create_pool_b(
        DATABASE_URL,
    )

TILE_RESPONSE_PARAMS = {
    "responses": {200: {"content": {"application/x-protobuf": {}}}},
    "response_class": Response,
}


def tile_params(
    z: int = Path(..., ge=0, le=25,),
    x: int = Path(...),
    y: int = Path(...),
) -> Tile:
    """Tile parameters."""
    return Tile(x, y, z)


@vectortile_app.post("/login")
def login(data: UsersReq):
    with Session(engine) as session:
        result = session.exec(
            select(Users).where(
                Users.username == data.username,
                Users.password == func.public.crypt(data.password, Users.password),
            )
        ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong username or password.",
        )

    return {"token": create_token(result.username)}


@vectortile_app.get("/adresses/{z}/{x}/{y}/")
async def get_tile(
        request: Request,
        auth_info: Authorizer = Depends(Authorizer()),
        tile: Tile = Depends(tile_params),  # FastAPI magic: receives x/y/z
):
    tms = morecantile.tms.get("WebMercatorQuad")
    bbox = tms.xy_bounds(tile)
    p = {
        "xmin": bbox.left,
        "ymin": bbox.bottom,
        "xmax": bbox.right,
        "ymax": bbox.top,
        "epsg": tms.crs.to_epsg(),
    }

    plz = auth_info.get_user_info()

    q = """
    SELECT ST_AsMVT(mvtgeom.*) FROM (
        SELECT ST_asmvtgeom(ST_Transform(t.geom, 3857), bounds.geom) AS geom, t.objectid
        FROM ( SELECT objectid, wkb_geometry as geom FROM public.adressen WHERE plz = '{plz}') t,
        (SELECT ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, :epsg) as geom) bounds
         WHERE ST_Intersects(t.geom, ST_Transform(bounds.geom, 4326))
         ) mvtgeom;  
    """.format(plz=plz)

    pool = request.app.state.pool
    async with pool.acquire() as conn:
        content = await conn.fetchval_b(q, **p)

    return Response(bytes(content), media_type="application/x-protobuf")
