import grpc
from concurrent import futures
import logging
import time
from grpc import StatusCode
import sys
import os
import jwt
from datetime import datetime, timedelta
from jwt import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError

# Add the path to the 'generated' folder to sys.path if not already present
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

# Custom exception for business logic errors
class ValidationError(Exception):
    def __init__(self, message, code=StatusCode.INVALID_ARGUMENT):
        self.message = message
        self.code = code
        super().__init__(self.message)

# Enhanced Authentication interceptor with comprehensive JWT validation
class AuthInterceptor(grpc.ServerInterceptor):
    def __init__(self, secret_key, issuer=None, audience=None):
        def abort(ignored_request, context):
            context.abort(StatusCode.UNAUTHENTICATED, 'Invalid or expired token')
        
        self._abortion = grpc.unary_unary_rpc_method_handler(abort)
        self.secret_key = secret_key
        self.issuer = issuer
        self.audience = audience

    def intercept_service(self, continuation, handler_call_details):
        metadata = dict(handler_call_details.invocation_metadata)
        
        auth_header = metadata.get('authorization', '')
        
        # Check if authorization header is present and has the correct format
        if not auth_header.startswith('Bearer '):
            logging.warning("Missing or malformed authorization header")
            return self._abortion
            
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        try:
            # Try to decode without verification first to see the contents
            unverified = jwt.decode(token, options={"verify_signature": False})
            logging.info(f"Token contents: {unverified}")
            logging.info(f"Current server time: {datetime.utcnow()}")
            
            # Now verify properly
            validation_options = {
                'verify_signature': True,
                'verify_exp': True,
                'verify_nbf': True,
                'verify_iat': True,
                'verify_aud': self.audience is not None,
                'verify_iss': self.issuer is not None,
            }
            
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=['HS256'],
                options=validation_options,
                audience=self.audience,
                issuer=self.issuer,
                leeway=30  # Allow 30 seconds of clock skew
            )
            
            logging.info(f"Successfully authenticated user: {payload.get('sub', 'Unknown')}")
            
            return continuation(handler_call_details)
            
        except ExpiredSignatureError:
            logging.warning("Token has expired")
            return self._abortion
        except InvalidSignatureError:
            logging.warning("Invalid token signature")
            return self._abortion
        except InvalidTokenError as e:
            logging.warning(f"Invalid token: {str(e)}")
            return self._abortion
        except Exception as e:
            logging.error(f"Unexpected error during token validation: {str(e)}")
            return self._abortion

# Logging interceptor
class LoggingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        method_name = handler_call_details.method.split('/')[-1]
        logging.info(f"Received call to {method_name}")
        return continuation(handler_call_details)

class GreeterServicer(greeter_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        return greeter_pb2.HelloReply(message=f'Hello, {request.name}!')

    def SayHelloStream(self, request, context):
        # Server streaming - send multiple responses
        for i in range(5):
            yield greeter_pb2.HelloReply(
                message=f'Hello, {request.name}! Response #{i+1}'
            )
            time.sleep(1)  # Simulate some processing time

    def SayHelloClientStream(self, request_iterator, context):
        # Client streaming - process multiple requests
        names = []
        for request in request_iterator:
            names.append(request.name)
        
        return greeter_pb2.HelloReply(
            message=f'Hello to all: {", ".join(names)}!'
        )

    def SayHelloBidirectional(self, request_iterator, context):
        # Bidirectional streaming
        for request in request_iterator:
            yield greeter_pb2.HelloReply(
                message=f'Hello, {request.name}!'
            )

    def SayHelloWithError(self, request, context):
        # Method that demonstrates error handling
        if request.name == "error":
            raise ValidationError("Name cannot be 'error'")
        
        if request.name == "internal":
            # This will trigger an internal error
            raise RuntimeError("Internal server error")
            
        return greeter_pb2.HelloReply(message=f'Hello, {request.name}!')

def serve():
    # Use the project root we already calculated
    cert_dir = os.path.join(project_root, 'certificates')
    
    # Check if certificate files exist
    server_key_path = os.path.join(cert_dir, 'server.key')
    server_crt_path = os.path.join(cert_dir, 'server.crt')
    
    if not os.path.exists(server_key_path):
        logging.error(f"Server key file not found at {server_key_path}")
        return
    
    if not os.path.exists(server_crt_path):
        logging.error(f"Server certificate file not found at {server_crt_path}")
        return

    # Load TLS credentials using absolute path
    try:
        with open(server_key_path, 'rb') as f:
            private_key = f.read()
        with open(server_crt_path, 'rb') as f:
            certificate_chain = f.read()
        
        server_credentials = grpc.ssl_server_credentials(
            ((private_key, certificate_chain),)
        )
    except Exception as e:
        logging.error(f"Error loading TLS credentials: {e}")
        return
    
    # Create server with interceptors
    # Use a strong secret key in production (not hardcoded)
    secret_key = "your-very-secure-secret-key-change-in-production"
    issuer = "your-grpc-server"  # Optional: validate token issuer
    audience = "your-grpc-clients"  # Optional: validate token audience
    
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[AuthInterceptor(secret_key, issuer, audience), LoggingInterceptor()]
    )
    
    greeter_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    
    # Add secure port
    server.add_secure_port('[::]:50051', server_credentials)
    
    server.start()
    logging.info("Secure server started on port 50051...")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
        server.stop(0)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    serve()