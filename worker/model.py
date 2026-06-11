import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import io
from pathlib import Path

# 모델 파일 경로
MODEL_PATH = Path(__file__).parent / "models" / "model.pth"

# 이미지 전처리 설정
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def build_model() -> nn.Module:
    """ResNet18 기반 폐렴 이진 분류 모델 구조 정의"""
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 2)  # 정상 / 폐렴
    return model


# 앱 시작 시 모델을 메모리에 올림
_model: nn.Module | None = None


def load_model() -> nn.Module:
    """모델을 메모리에 로드 (최초 1회만)"""
    global _model
    if _model is None:
        model = build_model()
        if MODEL_PATH.exists():
            state = torch.load(MODEL_PATH, map_location="cpu")
            # model.pth 가 state_dict인지 전체 모델인지 자동 판별
            if isinstance(state, dict):
                model.load_state_dict(state)
            else:
                model = state
        else:
            print(f"[경고] 모델 파일 없음: {MODEL_PATH} — 랜덤 가중치로 실행됩니다.")
        model.eval()
        _model = model
    return _model


def predict(image_bytes: bytes) -> dict:
    """
    X-ray 이미지 바이트를 받아 폐렴 예측 결과 반환

    Returns:
        {
            "is_pneumonia": bool,
            "confidence": float,  # 0.00 ~ 100.00
            "ai_model": str
        }
    """
    model = load_model()

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = transform(image).unsqueeze(0)  # (1, 3, 224, 224)

    with torch.no_grad():
        output = model(tensor)
        probabilities = torch.softmax(output, dim=1)
        pneumonia_prob = probabilities[0][1].item()

    is_pneumonia = pneumonia_prob >= 0.5
    confidence = round(pneumonia_prob * 100, 2)

    return {
        "is_pneumonia": is_pneumonia,
        "confidence": confidence,
        "ai_model": "ResNet18"
    }