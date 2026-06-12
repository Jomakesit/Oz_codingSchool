import json
import time
from worker.redis_client import redis_client
from worker.model import predict


def process_task(task_data: dict):
    task_id = task_data["task_id"]
    image_bytes = bytes.fromhex(task_data["image_bytes"])
    result_channel = f"result:{task_id}"

    prediction = predict(image_bytes)
    redis_client.publish(result_channel, json.dumps(prediction))
    print(f"[Worker] task_id={task_id} 완료: {prediction}")


def main():
    print("[Worker] AI 워커 시작 - pneumonia_queue 대기 중...")
    while True:
        task = redis_client.blpop("pneumonia_queue", timeout=5)
        if task:
            _, raw = task
            task_data = json.loads(raw)
            print(f"[Worker] 작업 수신: task_id={task_data['task_id']}")
            try:
                process_task(task_data)
            except Exception as e:
                print(f"[Worker] 오류 발생: {e}")


if __name__ == "__main__":
    main()
