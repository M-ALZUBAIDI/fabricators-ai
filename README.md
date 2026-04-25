# Fabricators AI Platform

An AI-powered platform for fabrication and design assistance that uses LLMs to help users with design questions, generate structured reports, and create 3D assets.

## Features

- **Chat Interface**: Ask questions about fabrication, design, and materials
- **Report Generation**: Generate structured JSON + PDF reports from conversations
- **3D Asset Generation**: Create 3D models (GLTF & STL) with embedded base64 encoding
- **Multi-Model Support**: Flexible LLM provider system (Unsloth, Claude, others)
- **Production & Testing Separation**: Different configurations for dev/prod environments
- **Pre-defined Instructions**: Extensible prompt templates for different use cases

## Project Structure

```
fabricators_ai/
├── config/           # Environment & model configuration
├── models/           # Data schemas & LLM providers
├── instructions/     # Prompt templates
├── services/         # Business logic
├── api/              # FastAPI routes
├── utils/            # Helper utilities
├── tests/            # Test suite
├── app.py            # Main application
└── requirements.txt  # Dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Development Server

```bash
# Development mode (mock LLM, no PDF)
ENVIRONMENT=development python -m uvicorn app:app --reload

# Production mode (real models, full features)
ENVIRONMENT=production python -m uvicorn app:app --reload
```

Server runs at `http://localhost:8000`

Visit `/docs` for interactive API documentation.

## API Endpoints

### Chat
- `POST /api/chat` - Send a question and get response
- `GET /api/chat/{session_id}` - Get conversation history

### Reports
- `POST /api/report` - Generate report from conversation (includes embedded 3D files)
- `GET /api/report/{report_id}` - Retrieve report
- `POST /api/report/{report_id}/export-pdf` - Export report as PDF

### 3D Generation
- `POST /api/3d/generate` - Generate 3D assets (cube, cylinder, sphere)

### System
- `GET /api/health` - Health check
- `GET /` - Root endpoint with API info

## Example Usage

### 1. Start a Chat Session

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I design a cube for 3D printing?"
  }'
```

Response:
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "answer": "To design a cube for 3D printing...",
  "timestamp": "2026-04-25T12:00:00",
  "model_used": "unsloth/mock"
}
```

### 2. Generate a Report

```bash
curl -X POST http://localhost:8000/api/report \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

Response includes:
- Conversation summary
- Design specification
- Key points
- **Embedded 3D assets as base64** (GLTF + STL)
- Shareable report ID

### 3. Generate 3D Asset

```bash
curl -X POST "http://localhost:8000/api/3d/generate?shape=cube&size=100&formats=gltf&formats=stl"
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | development | Env: development, production, testing |
| `LLM_PROVIDER` | mock | Provider: mock, unsloth |
| `MODEL_NAME` | meta-llama/Llama-2-7b-hf | Model identifier |
| `3D_GENERATION_ENABLED` | True | Enable 3D asset generation |
| `PDF_ENABLED` | False (dev), True (prod) | Enable PDF export |
| `DATABASE_URL` | sqlite:///./fabricators_dev.db | Database connection |

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Run specific test:

```bash
pytest tests/test_chat_service.py -v
```

With coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

## Development vs Production

### Development
- Uses **MockProvider** for fast testing (no actual LLM)
- SQLite database
- PDF generation disabled
- Debug logging enabled
- In-memory conversation storage

### Production
- Uses **UnslothProvider** with real models
- PostgreSQL database
- Full PDF export support
- Info level logging
- Persistent storage

Configure via `ENVIRONMENT` variable or update `.env`

## Architecture

### Services Layer
- **ChatService**: Manages conversations and LLM interactions
- **ReportService**: Generates structured reports with embedded 3D assets
- **DesignAnalyzerService**: Extracts specifications from conversations
- **3DGeneratorService**: Creates GLTF and STL 3D models

### Data Models
- **Pydantic models** for validation
- **Design3DAsset**: 3D files stored as base64
- **ReportData**: Complete report with embedded assets
- **DesignSpecification**: Extracted design parameters

### LLM Provider
- **Abstract LLMProvider** base class
- **UnslothProvider**: Real model inference
- **MockProvider**: Testing and development
- **LLMProviderFactory**: Provider creation

## 3D Asset Format

Assets are embedded in JSON reports as base64:

```json
{
  "format": "gltf",
  "data_base64": "base64_encoded_binary_data",
  "filename": "cube.gltf",
  "size_bytes": 12345
}
```

To use:
1. Decode base64 string
2. Write to file
3. Open in 3D viewer (e.g., three.js, Blender)

## Extending the System

### Add New LLM Provider

```python
from models.llm_provider import LLMProvider

class MyProvider(LLMProvider):
    async def initialize(self):
        pass
    
    async def generate(self, prompt, max_tokens=1024):
        # Your implementation
        pass
    
    async def shutdown(self):
        pass

# Register
LLMProviderFactory.register_provider("my_provider", MyProvider)
```

### Add New Prompt Template

1. Create markdown file in `instructions/`
2. Update `InstructionType` enum
3. Add to `filename_map` in `PromptTemplate.load()`

### Add New 3D Shape

```python
async def generate_torus(self, major_radius, minor_radius, formats=None):
    import trimesh
    mesh = trimesh.creation.torus(
        major_radius=major_radius,
        minor_radius=minor_radius
    )
    # Generate assets...
```

## Troubleshooting

### LLM Not Initializing
- Check `ENVIRONMENT` and `LLM_PROVIDER` settings
- For development, use `mock` provider
- For production with Unsloth, ensure PyTorch is installed

### 3D Generation Failing
- Ensure `trimesh` is installed: `pip install trimesh`
- Check `3D_GENERATION_ENABLED` is True
- Review logs for specific errors

### Tests Failing
- Ensure `pytest` and `pytest-asyncio` are installed
- Check test database permissions
- Run with `-v` flag for detailed output

## Performance Notes

- **Development**: Fast (uses mock LLM)
- **Production**: Depends on model size and hardware
- **3D Generation**: ~100-500ms per asset
- **PDF Export**: ~1-2s depending on content
- **Concurrent Requests**: Limited by LLM inference speed

## Future Enhancements

- [ ] PostgreSQL integration
- [ ] User authentication & authorization
- [ ] Conversation persistence
- [ ] Advanced 3D modeling from descriptions
- [ ] Multi-format export (OBJ, FBX)
- [ ] Material libraries
- [ ] Cost estimation engine
- [ ] Real-time collaboration

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests: `pytest tests/ -v`
4. Submit PR

## License

TBD

## Support

For issues or questions, contact: support@fabricators.ai
