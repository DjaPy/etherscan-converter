from typing import Callable

from fastapi import HTTPException, Request, Response
from fastapi.routing import APIRoute
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class OpenTelemetryRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            with tracer.start_as_current_span('Logs') as span:
                body = await request.body()
                if body:
                    span.add_event('Request', attributes={'Request': body})
                try:
                    response: Response = await original_route_handler(request)
                    if (b'content-type', b'image/jpeg') in response.raw_headers:
                        return response
                    span.add_event('Response', attributes={'Response': response.body})
                    return response
                except HTTPException as e:
                    span.add_event('Exception', attributes={'Exception': str(e.detail)})
                    raise HTTPException(status_code=e.status_code, detail=e.detail)

        return custom_route_handler
