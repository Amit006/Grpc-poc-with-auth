# gRPC Python Project

A comprehensive gRPC-based communication system demonstrating modern microservice architecture with enterprise-grade security features including JWT authentication, TLS encryption, and multiple RPC patterns.

## 🚀 Features

- **Multiple RPC Patterns**: Unary, Server Streaming, Client Streaming, and Bidirectional Streaming
- **Enterprise Security**: JWT-based authentication with TLS encryption
- **Interceptor Architecture**: Modular authentication and logging interceptors
- **Comprehensive Error Handling**: Robust error management and graceful degradation
- **Development Tools**: Automated setup scripts and protobuf generation
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📋 Prerequisites

- **Python 3.7+**
- **pip3** (Python package installer)
- **OpenSSL** (for certificate generation)

## 🛠️ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Amit006/Grpc-poc-with-auth.git
cd Grpc-poc-with-auth
```

### 2. Set Up Environment
```bash
# Make scripts executable (Linux/macOS)
chmod +x scripts/*.sh
chmod +x run_script.sh

# Set up virtual environment and install dependencies
./scripts/setup_env.sh

# For Windows, use the PowerShell script:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# .\setup_env.ps1
```

### 3. Generate Protobuf Files
```bash
# Generate Python gRPC code from .proto files
./scripts/generate_proto.sh
```

### 4. Generate TLS Certificates
```bash
# Create certificates directory
mkdir -p certificates

# Generate self-signed certificates for development
openssl req -x509 -newkey rsa:4096 -keyout certificates/server.key -out certificates/server.crt -days 365 -nodes -subj "/CN=localhost"
```

### 5. Run the Application
**Start the Server**
```bash
# Basic server (insecure)
./run_script.sh run_server

# Enhanced server (with TLS and JWT auth)
./run_script.sh run_server_en
```

**Run the Client**
```bash
# In a new terminal
# Basic client
./run_script.sh run_client

# Enhanced client (with authentication)
./run_script.sh run_client_en
```

## 📁 Project Structure

```
Grpc-poc-with-auth/
├── certificates/           # TLS certificates
│   ├── server.crt         # Server certificate
│   └── server.key         # Server private key
├── docs/                  # Documentation
│   └── architecture.md    # Detailed architecture guide
├── generated/             # Auto-generated protobuf files
│   ├── greeter_pb2.py     # Message classes
│   ├── greeter_pb2_grpc.py # Service stubs
│   └── __init__.py        # Package marker
├── protos/                # Protocol buffer definitions
│   └── greeter.proto      # Service definitions
├── scripts/               # Utility scripts
│   ├── generate_certificates.sh  # Certificate generation
│   ├── generate_proto.sh  # Protobuf generation
│   ├── setup_env.sh       # Environment setup (Linux/macOS)
│   └── setup_env.ps1      # Environment setup (Windows)
├── src/
│   ├── client/            # Client implementations
│   │   ├── client.py      # Basic client
│   │   └── client_enhanced.py # Enhanced client
│   └── server/            # Server implementations
│       ├── server.py      # Basic server
│       └── server_enhanced.py # Enhanced server
├── requirements.txt       # Dependencies
├── run_script.sh         # Main execution script
└── README.md             # This file
```

## 🔧 Available Commands

The `run_script.sh` provides several commands:

```bash
# Server commands
./run_script.sh run_server      # Start basic server
./run_script.sh run_server_en   # Start enhanced server with security

# Client commands
./run_script.sh run_client      # Run basic client
./run_script.sh run_client_en   # Run enhanced client with auth

# Utility commands
./run_script.sh setup          # Set up environment
./run_script.sh generate       # Generate protobuf files
./run_script.sh help           # Show help message
```

## 🔐 Security Features

### JWT Authentication
The enhanced server uses JWT tokens for authentication:

```json
{
  "sub": "user-id",
  "iat": 1234567890,
  "exp": 1234571490,
  "iss": "your-grpc-server",
  "aud": "your-grpc-clients"
}
```

### TLS Encryption
- All communication encrypted using TLS 1.2+
- Server certificate validation
- Secure channel establishment

### Interceptors
- **Authentication Interceptor**: Validates JWT tokens
- **Logging Interceptor**: Logs all requests and responses

## 🌐 RPC Patterns Demonstrated

### 1. Unary RPC
```python
# Single request → Single response
response = stub.SayHello(HelloRequest(name='Alice'))
```

### 2. Server Streaming RPC
```python
# Single request → Multiple responses
for response in stub.SayHelloStream(HelloRequest(name='Bob')):
    print(response.message)
```

### 3. Client Streaming RPC
```python
# Multiple requests → Single response
def generate_requests():
    for name in ['Charlie', 'David']:
        yield HelloRequest(name=name)

response = stub.SayHelloClientStream(generate_requests())
```

### 4. Bidirectional Streaming RPC
```python
# Multiple requests ↔ Multiple responses
def generate_requests():
    for name in ['Eve', 'Frank']:
        yield HelloRequest(name=name)

for response in stub.SayHelloBidirectional(generate_requests()):
    print(response.message)
```

## 🧪 Testing

### Manual Testing
```bash
# Test all RPC patterns with the enhanced client
./run_script.sh run_client_en
```

### Expected Output
```
Successfully imported protobuf modules
Generated JWT token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

1. Testing Unary RPC...
✓ Unary response: Hello, Alice!

2. Testing Server Streaming RPC...
✓ Server streaming responses:
  - Hello, Bob! Response #1
  - Hello, Bob! Response #2
  ...

3. Testing Client Streaming RPC...
✓ Client streaming response: Hello to all: Charlie, David, Eve!

4. Testing Bidirectional Streaming RPC...
✓ Bidirectional streaming responses:
  - Hello, Frank!
  - Hello, Grace!
  ...
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```
ModuleNotFoundError: No module named 'greeter_pb2'
```

**Solution:** Generate protobuf files
```bash
./scripts/generate_proto.sh
```

#### 2. Certificate Errors
```
Server certificate not found
```

**Solution:** Generate certificates
```bash
openssl req -x509 -newkey rsa:4096 -keyout certificates/server.key -out certificates/server.crt -days 365 -nodes -subj "/CN=localhost"
```

#### 3. Permission Errors
```
Permission denied: ./run_script.sh
```

**Solution:** Make scripts executable
```bash
chmod +x run_script.sh scripts/*.sh
```

#### 4. Port Already in Use
```
Address already in use
```

**Solution:** Kill existing processes
```bash
# Find process using port 50051
lsof -i :50051
# Kill the process
kill -9 <PID>
```

### Debug Mode
Enable debug output by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Development Workflow

### 1. Modify Protocol Buffer
```bash
# Edit protos/greeter.proto
# Regenerate code
./scripts/generate_proto.sh
```

### 2. Update Server Logic
```bash
# Edit src/server/server_enhanced.py
# Restart server
./run_script.sh run_server_en
```

### 3. Test Changes
```bash
# Run client to test
./run_script.sh run_client_en
```

## 📊 Performance Considerations

- **Connection Pooling**: gRPC automatically manages connections
- **Threading**: Server uses ThreadPoolExecutor (configurable)
- **Streaming**: Non-blocking I/O for optimal performance
- **Serialization**: Efficient protobuf binary format

## 🚀 Production Deployment

### Environment Variables
```bash
export GRPC_SECRET_KEY="your-production-secret-key"
export GRPC_SERVER_PORT="50051"
export GRPC_TLS_CERT_PATH="/path/to/cert.pem"
export GRPC_TLS_KEY_PATH="/path/to/key.pem"
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 50051
CMD ["python", "src/server/server_enhanced.py"]
```

### Load Balancing
Consider using:
- Nginx for HTTP/2 load balancing
- Envoy Proxy for advanced gRPC features
- Kubernetes for container orchestration

## 📚 Documentation

- **Architecture Guide**: [docs/architecture.md](docs/architecture.md)
- **Protocol Buffer Reference**: [protos/greeter.proto](protos/greeter.proto)
- **gRPC Documentation**: [Official gRPC docs](https://grpc.io/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions and classes
- Include error handling

### Testing Guidelines
- Test all RPC patterns
- Verify security features
- Check error scenarios
- Validate performance

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- gRPC Team for the excellent framework
- Protocol Buffers for efficient serialization
- JWT.io for authentication standards
- OpenSSL for cryptographic tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Amit006/Grpc-poc-with-auth/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Amit006/Grpc-poc-with-auth/discussions)
- **Email**: amit@example.com

## 🔮 Roadmap

- **Database Integration**: Add persistent storage
- **Service Mesh**: Istio/Envoy integration
- **Monitoring**: Prometheus metrics
- **Tracing**: Distributed tracing support
- **OAuth2**: Advanced authentication
- **GraphQL Gateway**: API gateway integration

---

Happy gRPC Development! 🎉