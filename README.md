# BullMQ Python Consumer

A Python server that connects to Redis and consumes jobs from BullMQ queues. This implementation provides a robust job processing system with proper error handling, logging, and graceful shutdown capabilities.

It is used for image compression using BRISQUE CNN.

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables by copying the example:
```bash
cp .env.example .env
```

3. Edit `.env` with your Redis configuration:
```bash
REDIS_URL=redis://localhost:6379/0
QUEUE_NAME=image-processing
LOG_LEVEL=INFO
```

## Usage

### Basic Usage

Run the consumer:
```bash
python main.py
```

## Code flow

<img src="./public/Image Processor LLD.png"></img>

## License

MIT License
