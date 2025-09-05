from concurrent import futures
import grpc
import sys
import os

# Add the path to the 'generated' folder to sys.path
# From src/server, we need to go up two levels to reach project root, then into generated
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

class GreeterServicer(greeter_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        return greeter_pb2.HelloReply(message=f'Hello, {request.name}!')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greeter_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051...")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop(0)

if __name__ == '__main__':
    serve()