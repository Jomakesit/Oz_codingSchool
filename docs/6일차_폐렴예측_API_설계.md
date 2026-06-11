6일차 - AI 폐렴 예측 API 설계

1\. 개요

저장된 진료기록에 연결된 X-ray 이미지를 AI 모델에 입력하여 폐렴 여부를 예측하고,

그 결과를 ai\_analysis\_results 테이블에 저장하는 API입니다.



2\. API 목록

메서드엔드포인트설명POST/ai/predict/{record\_id}진료기록 ID로 폐렴 예측 실행GET/ai/predict/{record\_id}진료기록 ID로 예측 결과 조회



3\. API 상세 명세

3-1. 폐렴 예측 실행



메서드: POST

엔드포인트: /ai/predict/{record\_id}

설명: 진료기록 ID에 연결된 X-ray 이미지를 AI 모델에 입력하여 폐렴 여부를 예측하고 결과를 저장합니다.



Path Parameter

파라미터타입필수설명record\_idint✅진료기록 ID

Request Body

파라미터타입필수설명xray\_imagefile✅흉부 X-ray 이미지 파일 (jpg, png)

Response Body (200 OK)

{

&#x20; "message": "폐렴 예측이 완료되었습니다.",

&#x20; "result": {

&#x20;   "id": 1,

&#x20;   "record\_id": 1,

&#x20;   "is\_pneumonia": true,

&#x20;   "confidence": 92.35,

&#x20;   "ai\_model": "ResNet18",

&#x20;   "created\_at": "2026-06-11T16:00:00"

&#x20; }

}

Error Response

상태코드설명404 Not Found진료기록 ID가 존재하지 않는 경우400 Bad Request이미지 파일이 없거나 형식이 올바르지 않은 경우



3-2. 예측 결과 조회



메서드: GET

엔드포인트: /ai/predict/{record\_id}

설명: 진료기록 ID에 대한 기존 AI 예측 결과를 조회합니다.



Path Parameter

파라미터타입필수설명record\_idint✅진료기록 ID

Response Body (200 OK)

{

&#x20; "id": 1,

&#x20; "record\_id": 1,

&#x20; "is\_pneumonia": true,

&#x20; "confidence": 92.35,

&#x20; "ai\_model": "ResNet18",

&#x20; "created\_at": "2026-06-11T16:00:00"

}

Error Response

상태코드설명404 Not Found진료기록 ID 또는 예측 결과가 존재하지 않는 경우



4\. 데이터 흐름

클라이언트

&#x20;   ↓ POST /ai/predict/{record\_id} + X-ray 이미지

FastAPI

&#x20;   ↓ record\_id로 medical\_records 조회

&#x20;   ↓ X-ray 이미지를 worker/model.py의 predict() 함수에 전달

&#x20;   ↓ 예측 결과(is\_pneumonia, confidence, ai\_model) 반환

&#x20;   ↓ ai\_analysis\_results 테이블에 저장

클라이언트에 결과 반환



5\. 사용 모델

항목내용모델 구조ResNet18 (이진 분류)입력 크기224 x 224 px출력정상(0) / 폐렴(1)모델 파일 경로worker/models/model.pth

