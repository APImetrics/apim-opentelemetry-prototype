from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from dotenv import load_dotenv
from random import randint
from time import time_ns
import os

load_dotenv()

resource = Resource(attributes={
    SERVICE_NAME: "APIContext-OpenTelemetry-Prototype"
})

provider = TracerProvider(resource=resource)

otel_headers = { "Authorization": f"Bearer {os.environ['OTEL_API_TOKEN']}" }
for h in os.environ["OTEL_HEADERS"].split(","):
    if "=" in h:
        k,v = h.split("=")
        if k and v:
            otel_headers[k] = v

otlp_exporter = OTLPSpanExporter(
    endpoint=os.environ["OTEL_ENDPOINT"],
    headers=otel_headers
)

processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)

def instrument_call(method: str, url: str):
    start = time_ns()
    dns_start = start
    dns_end = start + randint(100_000, 500_000)
    connect_start = dns_end + randint(1_000, 5_000)
    connect_end = connect_start + randint(100_000, 500_000)
    handshake_start = connect_end + randint(1_000, 5_000)
    handshake_end = handshake_start + randint(1_000_000, 5_000_000)
    upload_start = handshake_end + randint(1_000, 5_000)
    upload_end = upload_start + randint(1_000_000, 1_500_000)
    processing_start = upload_end
    processing_end = processing_start + randint(10_000_000, 20_000_000)
    download_start = processing_end
    download_end = download_start + randint(1_000_000, 2_000_000)
    end = download_end

    tracer = provider.get_tracer("api_call")
    with tracer.start_as_current_span("api_call", start_time=start, end_on_exit=False) as call:
        def span(name: str, start_time: int, end_time: int):
            return tracer.start_span(name, start_time=start_time).end(end_time=end_time)

        call.set_attribute("http.method", method)
        call.set_attribute("http.url", url)
        span("dns", dns_start, dns_end)
        span("connect", connect_start, connect_end)
        span("tls_handshake", handshake_start, handshake_end)
        span("upload", upload_start, upload_end)
        span("processing", processing_start, processing_end)
        span("download", download_start, download_end)
        call.end(end_time=end)


if __name__ == "__main__":
    instrument_call("GET", "https://api.example.com")
