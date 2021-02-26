from fastapi import FastAPI, Body
import uvicorn

from iscram.domain.model import SystemGraph
from iscram.service_layer import services
from iscram.adapters.repository import FakeRepository

app = FastAPI()
repo = FakeRepository()


@app.post("/risk")
async def risk(sg: SystemGraph = Body(...)):
    return {"risk": services.get_risk(sg, repo)}


@app.post("/birnbaum-structural-importances")
async def birnbaum_structural_importances(sg: SystemGraph = Body(...)):
    return {"birnbaum_structural_importances": services.get_birnbaum_structural_importances(sg, repo)}


@app.post("/birnbaum-importances")
async def birnbaum_importances(sg: SystemGraph = Body(...)):
    return {"birnbaum_importances": services.get_birnbaum_importances(sg, repo)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
