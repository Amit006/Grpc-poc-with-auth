import grpc
import logging
import sys
import os
import jwt
import time
from datetime import datetime, timedelta

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

# JWT token generation function
def generate_jwt_token(secret_key, user_id="test-user", expires_in=3600):
    """Generate a JWT token for authentication"""
    now = datetime.utcnow()
    payload = {
        'sub': user_id,
        'iat': now,
        'exp': now + timedelta(seconds=expires_in),
        'iss': 'your-grpc-server',  # Add issuer claim
        'aud': 'your-grpc-clients'  # Add audience claim
    }
    print(f"Token generation time: {now}")
    print(f"Token expiration time: {payload['exp']}")
    return jwt.encode(payload, secret_key, algorithm='HS256')

# Add this to your client_enhanced.py after generating the token
def debug_token(token, secret_key):
    """Debug function to check token contents"""
    try:
        # Decode without verification to see the contents
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"Token contents: {decoded}")
        
        # Now verify it
        jwt.decode(token, secret_key, algorithms=['HS256'])
        print("Token is valid when self-verified")
    except Exception as e:
        print(f"Token self-validation failed: {e}")


def run():
    # Secret key must match the server's secret key
    secret_key = "your-very-secure-secret-key-change-in-production"
    
    # Generate JWT token
    try:
        token = generate_jwt_token(secret_key)
        print(f"Generated JWT token: {token}")
        # Call this after generating the token
        debug_token(token, secret_key)
    except Exception as e:
        print(f"Failed to generate token: {e}")
        return
    
    # exit(1)  # Exit after token generation and debugging for demonstration purposes
    
    # Load TLS credentials using proper path
    cert_path = os.path.join(project_root, 'certificates', 'server.crt')
    try:
        with open(cert_path, 'rb') as f:
            trusted_certs = f.read()
        credentials = grpc.ssl_channel_credentials(trusted_certs)
        print(f"Loaded TLS certificate from: {cert_path}")
    except FileNotFoundError:
        print(f"Server certificate not found at: {cert_path}")
        print("Using insecure channel (not recommended for production).")
        # For testing purposes, we'll use insecure channel
        channel = grpc.insecure_channel('localhost:50051')
        run_tests(channel, token)
        return
    
    # Create secure channel
    try:
        with grpc.secure_channel('localhost:50051', credentials) as channel:
            run_tests(channel, token)
    except Exception as e:
        print(f"Secure channel creation failed: {e}")
        print("Trying insecure channel...")
        try:
            with grpc.insecure_channel('localhost:50051') as channel:
                run_tests(channel, token)
        except Exception as e2:
            print(f"Insecure channel also failed: {e2}")

def run_tests(channel, token):
    """Run all the gRPC tests"""
    # Add authentication metadata
    metadata = [('authorization', f'Bearer {token}')]
    stub = greeter_pb2_grpc.GreeterStub(channel)
    
    print("\n1. Testing Unary RPC...")
    # 1. Test unary call
    try:
        response = stub.SayHello(
            greeter_pb2.HelloRequest(name='Alice'),
            metadata=metadata
        )
        print(f"✓ Unary response: {response.message}")
    except grpc.RpcError as e:
        print(f"✗ Unary call failed: {e.code()} - {e.details()}")
    
    print("\n2. Testing Server Streaming RPC...")
    # 2. Test server streaming
    try:
        responses = stub.SayHelloStream(
            greeter_pb2.HelloRequest(name='Bob'),
            metadata=metadata
        )
        print("✓ Server streaming responses:")
        for i, response in enumerate(responses):
            print(f"  - {response.message}")
    except grpc.RpcError as e:
        print(f"✗ Server streaming failed: {e.code()} - {e.details()}")
    
    print("\n3. Testing Client Streaming RPC...")
    # 3. Test client streaming
    try:
        def generate_requests():
            names = ["Charlie", "David", "Eve"]
            for name in names:
                yield greeter_pb2.HelloRequest(name=name)
                time.sleep(0.5)  # Simulate delay between requests
        
        response = stub.SayHelloClientStream(
            generate_requests(),
            metadata=metadata,
            timeout=10  # Longer timeout for streaming
        )
        print(f"✓ Client streaming response: {response.message}")
    except grpc.RpcError as e:
        print(f"✗ Client streaming failed: {e.code()} - {e.details()}")
    
    print("\n4. Testing Bidirectional Streaming RPC...")
    # 4. Test bidirectional streaming
    try:
        def generate_requests():
            names = ["Frank", "Grace", "Heidi"]
            for name in names:
                yield greeter_pb2.HelloRequest(name=name)
                time.sleep(0.5)  # Simulate delay between requests
        
        responses = stub.SayHelloBidirectional(
            generate_requests(),
            metadata=metadata,
            timeout=10  # Longer timeout for streaming
        )
        print("✓ Bidirectional streaming responses:")
        for response in responses:
            print(f"  - {response.message}")
    except grpc.RpcError as e:
        print(f"✗ Bidirectional streaming failed: {e.code()} - {e.details()}")
    
    print("\n5. Testing Error Handling...")
    # 5. Test error handling
    try:
        response = stub.SayHelloWithError(
            greeter_pb2.HelloRequest(name='error'),
            metadata=metadata
        )
        print(f"✓ Error test response: {response.message}")
    except grpc.RpcError as e:
        print(f"✗ Error test failed as expected: {e.code()} - {e.details()}")
    
    print("\n6. Testing with Expired Token...")
    # 6. Test with expired token
    try:
        secret_key = "your-very-secure-secret-key-change-in-production"
        expired_token = generate_jwt_token(secret_key, expires_in=-1)  # Expired token
        expired_metadata = [('authorization', f'Bearer {expired_token}')]
        
        response = stub.SayHello(
            greeter_pb2.HelloRequest(name='Alice'),
            metadata=expired_metadata
        )
        print(f"✓ Unexpected success with expired token: {response.message}")
    except grpc.RpcError as e:
        print(f"✗ Expired token correctly rejected: {e.code()} - {e.details()}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()