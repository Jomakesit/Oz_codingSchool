# app/apis/practice_apis.py

from fastapi import APIRouter, HTTPException

user_list = [
	{
		"id": 1,
		"name": "홍길동",
		"age": 24,
		"email": "gildong24@example.com",
		"password": "Password1234!!"
	},
	{
		"id": 2,
		"name": "장문복",
		"age": 21,
		"email": "moonluck12@example.com",
		"password": "Check1321!"
	},
	{
		"id": 3,
		"name": "임우진",
		"age": 31,
		"email": "limousine33@example.com",
		"password": "lwsPAssword12@"
	}
]

# 회원정보 삭제 API 라우터 생성
router = APIRouter()
@router.delete("/{user_id}")
def delete_user(user_id: int):
    # user_list에서 해당 user_id를 가진 회원을 검색
    for user in user_list:
        if user["id"] == user_id:
            user_list.remove(user)  # 리스트에서 해당 회원 삭제
            return {"message": f"성공적으로 삭제되었습니다. (ID: {user_id})"}
    
    # 리스트를 다 돌았는데도 해당 id가 없으면 404 에러 반환
    raise HTTPException(status_code=404, detail="User not found")
