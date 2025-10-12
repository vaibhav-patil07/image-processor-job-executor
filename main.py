
from bullmq import Worker
import asyncio
import signal
from abc import ABC, abstractmethod
from typing import Dict, Any
from config import Config
import json
from ImageModel import ImageModel
from Storage import Storage
from ImageProcessor import ImageProcessor
import time
from RedisModel import RedisModel
from ImageJob import ImageJob

config = Config()
imageModel = ImageModel(config.DB_URL)
storage = Storage(config)
redisModel = RedisModel(config.REDIS_URL)

class DefaultJobProcessor():
    def __init__(self, config: Config):
        self.config = config
    async def processJob(self, job: Any, job_token: Any) -> Any:
        data = job.data
        imageJob = ImageJob(data)
        redisModel.publish('image-processor-progress', json.dumps({
            "image_id": imageJob.getImageId(),
            "status": "processing",
            "user_id": imageJob.getUserId(),
            "filename": imageJob.getImageName(),
            "progress": 10
            }
        ))
        print(f"Job Received : {imageJob.getMessage()}")
        start=time.time()
        imageModel.updateImageJobStatus(imageJob.getImageId(), "processing")
        downloadPath = f"uploads/{imageJob.getUserId()}/{imageJob.getImageId()}/{imageJob.getImageName()}"
        uploadPath = f"resized/{imageJob.getUserId()}/{imageJob.getImageId()}/{imageJob.getImageName()}"
        image =storage.download_image(downloadPath)
        redisModel.publish('image-processor-progress', json.dumps({
            "image_id": imageJob.getImageId(),
            "status": "processing",
            "user_id": imageJob.getUserId(),
            "filename": imageJob.getImageName(),
            "progress": 20
        }))
        imageProcessor = ImageProcessor(redisModel, imageJob)
        reducedImage = imageProcessor.reduceSize(image)
        reducedImageSize = reducedImage.nbytes
        storage.upload_image(uploadPath, reducedImage)
        redisModel.publish('image-processor-progress', json.dumps({
            "image_id": imageJob.getImageId(),
            "status": "processing",
            "user_id": imageJob.getUserId(),
            "filename": imageJob.getImageName(),
            "progress": 90
        }))
        end=time.time()
        time_taken = end - start
        print(f"Job Completed : {imageJob.getMessage()}, time_taken: {time_taken}")
        imageModel.updateImageJobStatus(imageJob.getImageId(), "completed", reducedImageSize)
        redisModel.publish('image-processor-progress', json.dumps({
            "image_id": imageJob.getImageId(),
            "status": "completed",
            "user_id": imageJob.getUserId(),
            "filename": imageJob.getImageName(),
            "progress": 100
        }))
        return "done"

async def processJob(job: Any, job_token: Any) -> Any:
     jobProcessor = DefaultJobProcessor(config)
     try:
        result = await jobProcessor.processJob(job, job_token)
     except Exception as e:
        print("Error processing job: ", e)
        raise e
     return result

async def main(config: Config):
    shutdown_event = asyncio.Event()
    def signal_handler(signal, frame):
        print("Signal received, shutting down.")
        shutdown_event.set()
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
   
    worker = Worker(config.QUEUE_NAME, processJob, {"connection": config.REDIS_URL})

    print("Worker started successfully.")
    # Wait until the shutdown event is set
    await shutdown_event.wait()

    # close the worker
    print("Cleaning up worker...")
    await worker.close()
    print("Worker shut down successfully.")

if __name__ == "__main__":
   asyncio.run(main(config))