from typing import Dict, Optional
import uvicorn
from pydantic import BaseModel

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

from iscram.domain.model import SystemGraph
from iscram.service_layer import services
from iscram.adapters.repository import FakeRepository

app = FastAPI(
    title="ISCRAM: IoT Supply Chain Risk Analysis and Mitigation Tool (Server)",
    description="Provides analysis and optimization services for systems represented as boolean function graphs.",
    version="0.1.0",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

repo = FakeRepository()


class RequestBody(BaseModel):
    system_graph: SystemGraph
    data: Optional[Dict]
    preferences: Optional[Dict]


@app.post("/risk")
async def risk(rq: RequestBody = Body(...)):
    return {"risk": services.get_risk(rq.system_graph, repo, rq.data)}


@app.post("/birnbaum-structural-importances")
async def birnbaum_structural_importances(rq: RequestBody = Body(...)):
    return {"birnbaum_structural_importances": services.get_birnbaum_structural_importances(rq.system_graph, repo)}


@app.post("/birnbaum-importances")
async def birnbaum_importances(rq: RequestBody = Body(...)):
    return {"birnbaum_importances": services.get_birnbaum_importances(rq.system_graph, repo, rq.data)}


@app.post("/attribute/{att}/{val}/birnbaum-structural-importances")
async def attr_birnbaum_structural_importances(att, val, rq: RequestBody = Body(...)):

    return services.get_birnbaum_structural_importances_select(rq.system_graph, {att: val}, repo, rq.data)


@app.post("/attribute/{att}/{val}/birnbaum-importances")
async def attr_birnbaum_importances(att, val, rq: RequestBody = Body(...)):
    return services.get_birnbaum_importances_select(rq.system_graph, {att: val}, repo, rq.data)


@app.post("/fractional_importance_traits")
async def fractional_importance_traits(rq: RequestBody = Body(...)):
    return {"fractional_importance_traits": services.get_fractional_importance_traits(rq.system_graph, rq.data)}


@app.get("/status")
async def status():
    return {"health": "alive"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
