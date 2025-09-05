import grpc
import sys
import os

# Add the path to the 'generated' folder to sys.path
# From src/client, we need to go up two levels to reach project root, then into generated
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
generated_path = os.path.join(project_root, 'generated')

if generated_path not in sys.path:
    sys.path.insert(0, generated_path)

try:
    # Import the actual files (note: gretter with double 't')
    import gretter_pb2 as greeter_pb2
    import gretter_pb2_grpc as greeter_pb2_grpc
    print("Successfully imported protobuf modules")
except ImportError as e:
    print(f"Failed to import protobuf modules: {e}")
    print("Available files in generated directory:")
    if os.path.exists(generated_path):
        print(os.listdir(generated_path))
    else:
        print("Generated directory does not exist!")
    sys.exit(1)

def run():
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = greeter_pb2_grpc.GreeterStub(channel)
            response = stub.SayHello(greeter_pb2.HelloRequest(name='Alice'))
            print("Response received:", response.message)
    except grpc.RpcError as e:
        print(f"gRPC error: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    run()