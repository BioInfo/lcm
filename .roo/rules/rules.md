# LCM Framework Project Intelligence

This document captures important patterns, preferences, and project intelligence for the LCM Framework.

## Project Structure Patterns

1. **Module Organization**
   - Source code is organized in the `src` directory with subdirectories by component
   - Each component has its own `__init__.py` file to make it a proper package
   - Related functionality is grouped together (e.g., all UI components in `src/ui`)

2. **Configuration Management**
   - Configuration is centralized in `config/settings.py`
   - Environment variables are used for deployment-specific settings
   - Sensible defaults are provided for all configuration options

3. **Entry Points**
   - The main entry point is `run.py` in the project root
   - Command-line arguments control which components to run
   - Scripts are made executable with `chmod +x`

4. **Documentation Structure**
   - User-facing documentation is in the project root (README.md)
   - Developer documentation is in the `docs` directory
   - Memory bank is in `.roo/memory-bank` for project knowledge

## Code Style Preferences

1. **Python Conventions**
   - Follow PEP 8 style guidelines
   - Use type hints for function parameters and return values
   - Include docstrings for all modules, classes, and functions
   - Use meaningful variable and function names

2. **Import Organization**
   - Standard library imports first
   - Third-party library imports second
   - Local module imports third
   - Alphabetical ordering within each group

3. **Error Handling**
   - Use try/except blocks for expected exceptions
   - Include specific exception types rather than catching all exceptions
   - Log errors with appropriate context
   - Provide meaningful error messages to users

## Implementation Patterns

1. **API Endpoints**
   - Use FastAPI for all API endpoints
   - Define request/response models with Pydantic
   - Include comprehensive docstrings for OpenAPI documentation
   - Implement proper error handling and status codes

2. **UI Components**
   - Use Gradio for interactive interfaces
   - Implement consistent styling across components
   - Separate UI logic from business logic
   - Provide clear user feedback for actions

3. **Model Handling**
   - Load models lazily to minimize startup time
   - Use appropriate data types (float16 for GPU, float32 for CPU)
   - Implement proper resource management
   - Include performance metrics collection

4. **Testing Approach**
   - Organize tests by type (unit, acceptance, stress)
   - Use pytest for all testing
   - Include both positive and negative test cases
   - Test edge cases and error conditions

## Deployment Patterns

1. **Docker Configuration**
   - Use multi-stage builds for smaller images
   - Separate services for different components
   - Mount volumes for persistent data
   - Use environment variables for configuration

2. **Resource Management**
   - Monitor GPU memory usage
   - Implement proper cleanup of resources
   - Use appropriate batch sizes for inference
   - Consider quantization for production deployment

## Known Challenges

1. **Model Size Constraints**
   - LCM and Llama models require significant memory
   - Consider implementing model quantization for resource-constrained environments
   - Provide fallback to CPU when GPU is not available

2. **Concurrent Request Handling**
   - Multiple simultaneous requests can exhaust GPU memory
   - Implement request queuing for high-traffic scenarios
   - Consider horizontal scaling for production deployments

3. **UI Responsiveness**
   - Model inference can cause UI lag
   - Implement asynchronous processing where possible
   - Provide clear loading indicators for users

This document will be updated as new patterns and intelligence are discovered during project development.