# BullMQ Python Consumer

A Python server that connects to Redis and consumes jobs from BullMQ queues. This implementation provides a robust job processing system with proper error handling, logging, and graceful shutdown capabilities.

## Features

- **Redis Connection**: Robust connection handling with automatic reconnection
- **BullMQ Compatibility**: Works with BullMQ job queues created by Node.js applications
- **Job Processing**: Moves jobs through proper BullMQ states (wait → active → completed/failed)
- **Error Handling**: Comprehensive error handling with failed job tracking
- **Graceful Shutdown**: Handles SIGINT/SIGTERM signals for clean shutdown
- **Configurable**: Environment-based configuration
- **Logging**: Structured logging with configurable levels
- **Queue Statistics**: Monitor queue health and job counts

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
python bullmq_consumer.py
```

### Custom Job Processing

To implement custom job processing logic, create a subclass of `BullMQConsumer` and override the `process_job` method:

```python
from bullmq_consumer import BullMQConsumer
import logging

logger = logging.getLogger(__name__)

class ImageProcessorConsumer(BullMQConsumer):
    def process_job(self, job_data):
        """
        Custom job processing for image processing tasks
        """
        image_url = job_data.get('imageUrl')
        operation = job_data.get('operation', 'resize')
        
        logger.info(f"Processing image: {image_url} with operation: {operation}")
        
        # Your image processing logic here
        # ...
        
        return {
            "status": "processed",
            "imageUrl": image_url,
            "operation": operation,
            "processedAt": int(time.time())
        }

if __name__ == "__main__":
    consumer = ImageProcessorConsumer()
    consumer.start()
```

## Configuration

The application uses environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL (supports redis://, rediss://, unix://) |
| `QUEUE_NAME` | `image-processing` | BullMQ queue name |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `JOB_TIMEOUT` | `30` | Job processing timeout in seconds |
| `MAX_RETRIES` | `3` | Maximum job retry attempts |

## BullMQ Integration

This consumer works with BullMQ queues by interacting with the underlying Redis data structures:

- `bull:{queue}:wait` - Jobs waiting to be processed
- `bull:{queue}:active` - Jobs currently being processed  
- `bull:{queue}:completed` - Successfully completed jobs
- `bull:{queue}:failed` - Failed jobs

### Job Flow

1. **Consume**: Jobs are consumed from the `wait` list using `BLPOP`
2. **Activate**: Jobs are moved to the `active` list during processing
3. **Complete**: Successfully processed jobs are moved to `completed`
4. **Fail**: Failed jobs are moved to `failed` with error information

## Monitoring

### Queue Statistics

The consumer provides queue statistics:

```python
consumer = BullMQConsumer()
consumer.connect()
stats = consumer.get_queue_stats()
print(stats)
# Output: {'waiting': 5, 'active': 2, 'completed': 100, 'failed': 3}
```

### Logging

The application provides structured logging:

```
2024-01-20 10:30:00,123 - bullmq_consumer - INFO - Connected to Redis using URL: redis://localhost:6379/0
2024-01-20 10:30:00,124 - bullmq_consumer - INFO - Starting BullMQ consumer for queue: image-processing
2024-01-20 10:30:01,200 - bullmq_consumer - INFO - Received job: {"id":"1","data":{"imageUrl":"..."}}...
2024-01-20 10:30:02,150 - bullmq_consumer - INFO - Job 1 completed successfully
```

## Error Handling

The consumer includes comprehensive error handling:

- **Connection Errors**: Automatic Redis reconnection
- **Job Processing Errors**: Failed jobs are moved to the failed queue
- **Graceful Shutdown**: SIGINT/SIGTERM signals are handled cleanly
- **Timeout Handling**: Jobs can be configured with processing timeouts

## Development

### Running in Development

For development, you can run with debug logging:

```bash
LOG_LEVEL=DEBUG python bullmq_consumer.py
```

### Testing

To test the consumer, you can add jobs to the Redis queue from a Node.js BullMQ producer or manually using Redis CLI:

```bash
# Add a test job manually
redis-cli LPUSH "bull:image-processing:wait" '{"id":"test-1","data":{"imageUrl":"https://example.com/image.jpg","operation":"resize"}}'
```

## Production Deployment

For production deployment:

1. Use a process manager like `systemd` or `supervisor`
2. Set appropriate log levels and rotation
3. Monitor Redis connection health
4. Set up proper error alerting
5. Consider running multiple consumer instances for high throughput

### Systemd Service Example

```ini
[Unit]
Description=BullMQ Python Consumer
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/your/app
ExecStart=/usr/bin/python3 bullmq_consumer.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## License

MIT License
