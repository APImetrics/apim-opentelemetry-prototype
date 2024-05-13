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

# Define the service name resource for the tracer.
resource = Resource(attributes={
    SERVICE_NAME: "Axiom-Otel-Prototype"
})

# Create a TracerProvider with the defined resource for creating tracers.
provider = TracerProvider(resource=resource)

# Configure the OTLP/HTTP Span Exporter with Axiom headers and endpoint. Replace `API_TOKEN` with your Axiom API key, and replace `DATASET_NAME` with the name of the Axiom dataset where you want to send data.
otlp_exporter = OTLPSpanExporter(
    endpoint="https://api.axiom.co/v1/traces",
    headers={
        "Authorization": f"Bearer {os.environ['AXIOM_API_TOKEN']}",
        "X-Axiom-Dataset": "exploring-axiom"
    }
)

# Create a BatchSpanProcessor with the OTLP exporter to batch and send trace spans.
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)

# Set the TracerProvider as the global tracer provider.
trace.set_tracer_provider(provider)

# Define a tracer for external use in different parts of the app.
tracer = trace.get_tracer("api_call")

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

    call = tracer.start_span("api_call", start_time=start, attributes={"http.method": method, "http.url": url})
    dns = tracer.start_span("dns_lookup", start_time=dns_start).end(end_time=dns_end)
    connect = tracer.start_span("connect", start_time=connect_start).end(end_time=connect_end)
    handshake = tracer.start_span("tls_handshake", start_time=handshake_start).end(end_time=handshake_end)
    upload = tracer.start_span("upload", start_time=upload_start).end(end_time=upload_end)
    processing = tracer.start_span("processing", start_time=processing_start).end(end_time=processing_end)
    download = tracer.start_span("download", start_time=download_start).end(end_time=download_end)
    call.end(end_time=end)


if __name__ == "__main__":
    instrument_call("GET", "https://api.example.com")
