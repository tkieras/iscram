from typing import Dict, Optional

import uvicorn
from pydantic import BaseModel

from fastapi import FastAPI, Body, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from iscram.domain.model import SystemGraph, DataValidationError
from iscram.domain.optimization import OptimizationError
from iscram.service_layer import services
from iscram.adapters.repository import LRUCacheRepository, RepositoryLookupError

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

repo = LRUCacheRepository()


class SystemGraphRequest(BaseModel):
    system_graph: SystemGraph


class RequestBody(BaseModel):
    data: Optional[Dict]
    preferences: Optional[Dict]


class AnalysisResponseBody(BaseModel):
    name: str
    payload: Dict
    data_source: Optional[str]
    node_id: Optional[str]
    attribute: Optional[str]
    value: Optional[str]


class OptimizationResponseBody(BaseModel):
    sg_id: str
    system_graph: Dict


@app.exception_handler(DataValidationError)
async def data_validation_error_handler(request: Request, exc: DataValidationError):
    error = dict(msg=exc.message, type="Data Validation Error")
    return JSONResponse(
        status_code=400,
        content=dict(error=error)
    )


@app.exception_handler(OptimizationError)
async def optimization_error_handler(request: Request, exc: OptimizationError):
    error = dict(msg=exc.message, type="Optimization Error")
    return JSONResponse(
        status_code=400,
        content=dict(error=error)
    )


@app.exception_handler(RepositoryLookupError)
async def repository_lookup_error_handler(request: Request, exc: RepositoryLookupError):
    error = dict(msg=exc.message, type="RepositoryLookupError")
    return JSONResponse(
        status_code=400,
        content=dict(error=error)
    )


@app.post("/id")
async def get_id(rq: SystemGraphRequest = Body(...)):
    services.put_system_graph(rq.system_graph, repo)
    return {"id": rq.system_graph.get_id()}


@app.post("/id/{sg_id}/analyze/system/risk", response_model=AnalysisResponseBody)
async def system_risk(sg_id: str, data_source: Optional[str] = None, rq: RequestBody = Body(...)):
    # add various risk source options
    sg = services.get_system_graph(sg_id, repo)
    return dict(name="system_risk", payload=services.get_risk(sg, rq.data), data_source=data_source)


@app.post("/id/{sg_id}/analyze/node/risk")
async def node_risk(sg_id: str, data_source: str,  node_id: str, rq: RequestBody = Body(...)):
    # service for risk at this node (e.g., not at indicator, new bdd, etc).
    return {"message": "Not implemented."}


@app.post("/id/{sg_id}/analyze/node/importance/sensitivity", response_model=AnalysisResponseBody)
async def node_importance_sensitivity(sg_id: str, data_source: str, rq: RequestBody = Body(...), node_id: Optional[str] = None):
    sg = services.get_system_graph(sg_id, repo)
    result = services.get_birnbaum_importances(sg, rq.data, data_source)
    if node_id is None:
        return dict(name="node_importance_sensitivity", payload=result, node_id=node_id, data_source=data_source)
    else:
        return dict(name="node_importance_sensitivity", payload={node_id: result[node_id]}, node_id=node_id, data_source=data_source)


@app.post("/id/{sg_id}/analyze/node/importance/improvement_potential")
async def node_importance_improvement_potential(sg_id: str, data_source: str, rq: RequestBody = Body(...), node_id: Optional[str] = None):
    # service for improvement potential
    return {"message": "Not implemented."}


@app.post("/id/{sg_id}/analyze/attribute/importance/sensitivity", response_model=AnalysisResponseBody)
async def attribute_importance_sensitivity(sg_id: str, data_source: str, rq: RequestBody = Body(...), attribute: Optional[str] = None, value: Optional[bool] = None):
    sg = services.get_system_graph(sg_id, repo)
    if attribute is not None:
        payload = services.get_birnbaum_importances_select(sg, rq.data, {attribute: value}, data_source)
        return dict(name="attribute_importance_sensitivity", payload=payload, data_source=data_source, attribute=attribute, value=value)
    else:
        payload = services.get_attribute_sensitivity(sg, rq.data, data_source)
        return dict(name="attribute_importance_sensitivity", payload=payload, data_source=data_source, attribute=attribute, value=value)


@app.post("/id/{sg_id}/analyze/attribute/importance/fractional", response_model=AnalysisResponseBody)
async def attribute_importance_fractional(sg_id: str, rq: RequestBody = Body(...), attribute: Optional[str] = None, value: Optional[bool] = None):
    sg = services.get_system_graph(sg_id, repo)
    if attribute is not None:
        return {"name": "attribute_importance_fractional", "payload": {"message": "Not Implemented"}}
    else:
        return dict(name="attribute_importance_fractional", payload=services.get_fractional_importance_traits(sg, rq.data), attribute=attribute, value=value)


@app.post("/id/{sg_id}/recommend/component/supplier", response_model=OptimizationResponseBody)
async def recommend_node_supplier(sg_id: str, alpha: float, budget: int, rq: RequestBody = Body(...)):
    sg = services.get_system_graph(sg_id, repo)
    updated = services.get_system_graph_optimized_suppliers(sg, rq.data, {"alpha": alpha, "budget": budget})
    services.put_system_graph(updated, repo)
    return dict(sg_id=updated.get_id(), system_graph=updated.dict())


@app.get("/status")
async def status():
    return {"status": "alive"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
