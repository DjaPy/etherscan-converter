from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from starlette.middleware.cors import CORSMiddleware

from etherscan_converter.config import Config, config
from etherscan_converter.entrypoints.api_v1.api import api_router

resource = Resource(attributes={
    "service.name": config.jaeger_name
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name=config.jaeger_host,
    agent_port=config.jaeger_port,
)
trace.get_tracer_provider().add_span_processor(  # type: ignore
    BatchSpanProcessor(jaeger_exporter, max_export_batch_size=10)
)


def get_application(app_config: Config) -> FastAPI:

    app = FastAPI(
        title='Etherscan converter',
        description='Service for converting data from Etherscan',
        docs_url='/doc',
    )

    app.state.config = app_config

    allow_origins = [str(origin) for origin in app_config.origins]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins or ['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(api_router)

    if app_config.jaeger_enable:
        FastAPIInstrumentor.instrument_app(app, excluded_urls='/openapi.json|/doc')
        AioHttpClientInstrumentor().instrument()

    return app


app_server = get_application(config)
