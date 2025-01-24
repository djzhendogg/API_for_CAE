from fastapi import FastAPI, Query, HTTPException
from starlette.requests import Request

from src.service import SeqQuantKernel
from src.schemas import (
    PolymerType,
    EncodingStrategy,
    NewMonomers,
    SeqQuantKernelModel
)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.post("/encode_sequence")
@limiter.limit("60/minute")
async def generate_latent_representations(
        request: Request,
        sequences: str = Query(default=""),
        polymer_type: PolymerType = 'protein',
        encoding_strategy: EncodingStrategy ='protein',
        new_monomers: NewMonomers = None,
        skip_unprocessable: bool = True,

):
    if encoding_strategy == 'protein':
        new_monomers = None

    sequence_list = sequences.replace(" ", "").split(",")

    if len(sequence_list) > 100:
        error_text = "The number of sequences in the query exceeds 100"
        raise HTTPException(status_code=429, detail=error_text)

    sqk = SeqQuantKernel(
        polymer_type=polymer_type,
        new_monomers=new_monomers
    )
    return sqk.generate_latent_representations(
        sequence_list=sequence_list,
        skip_unprocessable=skip_unprocessable,
        encoding_strategy=encoding_strategy
    )


@app.get("/monomers/{polymer_type}")
@limiter.limit("30/minute")
async def get_existing_monomers(request: Request, polymer_type: PolymerType = 'protein'):
    sqk = SeqQuantKernel(
        polymer_type=polymer_type
    )
    return sqk.known_monomers


@app.post("/kernel_info/{polymer_type}")
@limiter.limit("30/minute")
async def get_kernel_info(
        request: Request,
        polymer_type: PolymerType = 'protein',
        new_monomers: NewMonomers = None
    ):
    sqk = SeqQuantKernel(
        polymer_type=polymer_type,
        new_monomers=new_monomers
    )
    return SeqQuantKernelModel(
        max_sequence_length=sqk.max_sequence_length,
        num_of_descriptors=sqk.num_of_descriptors,
        known_monomers=sqk.known_monomers,
        polymer_type=sqk.polymer_type
    )

