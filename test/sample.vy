from pydantic import BaseModel
from typing import Dict, Any

class MyExperiment(BaseModel):
    """foo"""
    
    network: Network@spk_vih[
        foo = 20
        shape[1] = 500
        layers[1].populations.e.kind = adaptive_LIF
    ]
    loss: Loss@mse
    optimizer: Optimizer@adam
    dataset: Dataset@default
