# GRPC Proof of Concept with JWT Authentication

A comprehensive Proof of Concept (PoC) demonstrating gRPC communication with JWT-based authentication, TLS encryption, and various RPC patterns.

## Features

- **Secure Communication**: TLS/SSL encryption for all gRPC communications
- **JWT Authentication**: Token-based authentication with proper validation
- **Multiple RPC Patterns**:
  - Unary RPC (request-response)
  - Server streaming RPC
  - Client streaming RPC
  - Bidirectional streaming RPC
- **Error Handling**: Comprehensive error handling with proper gRPC status codes
- **Interceptors**: Authentication and logging interceptors for enhanced security and observability
- **Automated Setup**: Scripts for environment setup and certificate generation (Linux/macOS/Windows)

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- OpenSSL (for certificate generation)

## Installation

### Automated Setup (Linux/macOS)

1. Clone the repository:
```bash
git clone https://github.com/Amit006/Grpc-poc-with-auth.git
cd Grpc-poc-with-auth
```

2. Make the setup scripts executable:
```bash
chmod +x setup_env.sh generate_certificates.sh
```

3. Run the setup script to create virtual environment and install dependencies:
```bash
./setup_env.sh
```

4. Generate TLS certificates:
```bash
./generate_certificates.sh
```

5. Activate the virtual environment:
```bash
source grpc_env/bin/activate
```

### Automated Setup (Windows)

1. Clone the repository:
```bash
git clone https://github.com/Amit006/Grpc-poc-with-auth.git
cd Grpc-poc-with-auth
```

2. Run the PowerShell setup script (in PowerShell with execution policy allowing scripts):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_env.ps1
```

3. Generate TLS certificates (run in PowerShell):
```powershell
# Run these commands manually in PowerShell
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
Remove-Item server.csr  # Remove the CSR file
```

### Manual Setup (All Platforms)

1. Clone the repository:
```bash
git clone https://github.com/Amit006/Grpc-poc-with-auth.git
cd Grpc-poc-with-auth
```

2. Create a virtual environment:
```bash
# Linux/macOS
python -m venv grpc_env
source grpc_env/bin/activate

# Windows
python -m venv grpc_env
grpc_env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Generate TLS certificates:
```bash
# Run these commands manually
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

# Clean up
rm server.csr  # Linux/macOS
# or
del server.csr  # Windows
```

## Scripts Overview

### setup_env.sh (Linux/macOS)
This script automates the environment setup process:
- Creates a Python virtual environment
- Activates the virtual environment
- Installs all required dependencies from requirements.txt

### setup_env.ps1 (Windows)
This PowerShell script automates the environment setup process for Windows:
- Creates a Python virtual environment
- Activates the virtual environment
- Installs all required dependencies from requirements.txt

### generate_certificates.sh (Linux/macOS)
This script generates the necessary TLS certificates for secure communication:
- Creates a private key (server.key)
- Generates a certificate signing request (CSR)
- Creates a self-signed certificate (server.crt) valid for 365 days
- Cleans up temporary files

## Usage

1. Start the gRPC server:
```bash
python server_enhanced.py
```

2. In a separate terminal, run the client:
```bash
python client_enhanced.py
```

The client will demonstrate all RPC patterns and authentication mechanisms.

## Project Structure

```
Grpc-poc-with-auth/
├── greeter.proto           # Protocol Buffer definition
├── greeter_pb2.py          # Generated message classes
├── greeter_pb2_grpc.py     # Generated server and client classes
├── server_enhanced.py      # Enhanced gRPC server implementation
├── client_enhanced.py      # Enhanced gRPC client implementation
├── generate_certificates.sh # Script to generate TLS certificates (Linux/macOS)
├── setup_env.sh            # Script to set up the environment (Linux/macOS)
├── setup_env.ps1           # Script to set up the environment (Windows)
├── requirements.txt        # Python dependencies
├── server.key             # TLS private key (generated)
├── server.crt             # TLS certificate (generated)
└── README.md              # This file
```

## API Overview

The service defines the following RPC methods:

1. **SayHello** - Unary RPC: Simple request-response pattern
2. **SayHelloStream** - Server streaming: Server sends multiple responses
3. **SayHelloClientStream** - Client streaming: Client sends multiple requests
4. **SayHelloBidirectional** - Bidirectional streaming: Both client and server stream messages
5. **SayHelloWithError** - Demonstrates error handling patterns

## Configuration

### JWT Secret Key

The server and client use a shared secret key for JWT validation. By default, this is set to:
```
your-very-secure-secret-key-change-in-production
```

For production use, you should:
1. Change this to a strong, randomly generated key
2. Consider using environment variables or a secure secrets management system

### TLS Certificates

The project includes scripts to generate self-signed certificates for development. For production:
1. Use certificates from a trusted Certificate Authority (CA)
2. Ensure proper certificate validation on both client and server

## Troubleshooting

### Common Issues

1. **Authentication failures**: Ensure the JWT secret key matches between client and server
2. **Certificate errors**: Regenerate TLS certificates if they expire or become invalid
3. **Connection refused**: Verify the server is running on the correct port (default: 50051)
4. **Script execution errors on Windows**: 
   - Ensure you're running PowerShell with appropriate execution policy
   - You may need to run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Debug Mode

For detailed logging, set the log level to DEBUG in both server and client:
```python
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments

- Google for the gRPC framework
- The Python gRPC community for excellent libraries and tools
- JWT.io for JSON Web Token resources and best practices

---

For questions or support, please open an issue on GitHub or contact the maintainers.
