import grpc
from concurrent import futures
import logging
import time
from grpc import StatusCode
import greeter_pb2
import greeter_pb2_grpc
import jwt
from datetime import datetime, timedelta
from jwt import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError

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

    # def intercept_service(self, continuation, handler_call_details):
    #     metadata = dict(handler_call_details.invocation_metadata)
        
    #     auth_header = metadata.get('authorization', '')
        
    #     # Check if authorization header is present and has the correct format
    #     if not auth_header.startswith('Bearer '):
    #         logging.warning("Missing or malformed authorization header")
    #         return self._abortion
            
    #     token = auth_header[7:]  # Remove 'Bearer ' prefix
        
    #     try:
    #         # Comprehensive JWT token validation
    #         validation_options = {
    #             'verify_signature': True,
    #             'verify_exp': True,      # Verify expiration time
    #             'verify_nbf': True,      # Verify not before time
    #             'verify_iat': True,      # Verify issued at time
    #             'verify_aud': self.audience is not None,  # Verify audience if provided
    #             'verify_iss': self.issuer is not None,    # Verify issuer if provided

    #         }
            
    #         payload = jwt.decode(
    #             token, 
    #             self.secret_key, 
    #             algorithms=['HS256'],
    #             options=validation_options,
    #             audience=self.audience,
    #             issuer=self.issuer,
    #             leeway=30  # Allow 30 seconds of clock skew
    #         )
            
    #         # Additional custom validations can be added here
    #         # For example, check if the token has been revoked
    #         # or if the user still exists in the system
            
    #         logging.info(f"Successfully authenticated user: {payload.get('sub', 'Unknown')}")
            
    #         return continuation(handler_call_details)
            
    #     except ExpiredSignatureError:
    #         logging.warning("Token has expired")
    #         return self._abortion
    #     except InvalidSignatureError:
    #         logging.warning("Invalid token signature")
    #         return self._abortion
    #     except InvalidTokenError as e:
    #         logging.warning(f"Invalid token: {str(e)}")
    #         return self._abortion
    #     except Exception as e:
    #         logging.error(f"Unexpected error during token validation: {str(e)}")
    #         return self._abortion
    # In AuthInterceptor's intercept_service method
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
    # Load TLS credentials
    with open('server.key', 'rb') as f:
        private_key = f.read()
    with open('server.crt', 'rb') as f:
        certificate_chain = f.read()
    
    server_credentials = grpc.ssl_server_credentials(
        ((private_key, certificate_chain),)
    )
    
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
    print("Secure server started on port 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()