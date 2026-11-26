import httpx
from fastapi import Request, Response
from fastapi.responses import JSONResponse


async def forward_request(service_url: str, request: Request, service_path: str):
    """Forward the request to a backend service and return its response."""
    url = f"{service_url}/{service_path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    headers = {
        name: value
        for name, value in request.headers.items()
        if name.lower() not in {"host", "content-length"}
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body(),
            )
    except httpx.RequestError as error:
        return JSONResponse(
            status_code=503,
            content={
                "detail": f"Service unavailable: {error}",
                "code": "SERVICE_UNAVAILABLE",
            },
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.headers.get("content-type"),
    )
