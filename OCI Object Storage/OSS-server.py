from argparse import Action
from typing import Required
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json
import os
import tempfile

app = FastAPI(title="OCI Object Storage Server", version="0.1.0")

class MCPRequest(BaseModel):
    action: str
    parameters: dict


@app.post("/mcp/oci-bucket")
def handle_mcp_request(req: MCPRequest):
    try: 
        if req.action == "list_objects":
            return list_objects(req.parameters)
        elif req.action == "read_object"    :
            return read_object(req.parameters)
        else:
            return HTTPException(status_code=400, detail="Invalid action")
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
        
def list_objects(params: dict):
    Required = ["namespace-name", "bucket-name"]
    for key in Required:
        if key not in params:
            return HTTPException(status_code=400, detail=f"Missing required parameter: {key}")
        
    cmd = ["oci", "os", "object", "list", "--namespace-name", params["namespace-name"], "--bucket-name", params["bucket-name"], "--output", "json"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        return HTTPException(status_code=500, detail=result.stderr)
    
    return json.loads(result.stdout)

def read_object(params: dict):
    Required = ["namespace-name", "bucket-name", "object-name"]
    for key in Required:
        if key not in params:
            return HTTPException(status_code=400, detail=f"Missing required parameter: {key}")
        
    cmd = ["oci", "os", "object", "get", "--namespace-name", params["namespace-name"], "--bucket-name", params["bucket-name"], "--object-name", params["object-name"], "--output", "json"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        return HTTPException(status_code=500, detail=result.stderr)
    
    return json.loads(result.stdout)
    
            