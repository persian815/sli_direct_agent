import sys
import time
import json
import os
import requests as requests
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

_apim_pass_key =""

def get_apim_pass_key():
    global _apim_pass_key
    if _apim_pass_key == "":
        return os.environ.get("APIM_PASS_KEY", "")

# 토큰 변경 필요
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzl1NiJ9.eyJjbGllbnRJZCI6ImNsaWVudC1maXJIIiwiY2xpZW50U2VjcmVOljoiNTg5Zjg5NZiMWI2M2U2YWEzZjYwNDY1NDgyMDVINjNiYTVkNWMxZCIsImV4cCI6NDEwMjQ5ODc5OX0.Q-Oan9oRcrY9tymcnHNRH9cyhw8Re3ueOQJMLJqiwFo"
headers: dict = {
    "X-generative-ai-client":access_token,
    "Content-Type":"application/json"
}


def get_json_events(header, body):
    # 호출 url 변경 필요
    logger.info("SDS AI API 호출 시작")
    logger.info(f"요청 URL: https://poc.fabrix-e.samsungsds.com/openapi/chat/v1/messages")
    logger.info(f"요청 헤더: {json.dumps(header, indent=2)}")
    logger.info(f"요청 본문: {json.dumps(body, indent=2)}")
    
    try:
        response = requests.post(
            "https://poc.fabrix-e.samsungsds.com/openapi/chat/v1/messages",
            headers=header,
            json=body,
        )
        logger.info(f"응답 상태 코드: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"API 호출 실패: {response.text}")
            return f"API 호출 실패 (상태 코드: {response.status_code})"
            
        response_text = response.text.split("\n")
        count = 0 
        res = ""
        for event in response_text:
            if event.find("event_stauts") > 0:
                try:
                    string_to_dict = json.loads(event.replace("data: ", "").split())
                    if string_to_dict["event_status"] == "CHUNK":
                        res += string_to_dict["content"]
                        count += 1
                        if count % 10 == 0:  # 10개 청크마다 로그 출력
                            logger.info(f"처리된 청크 수: {count}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 파싱 오류: {e}")
                    continue
        
        logger.info(f"총 처리된 청크 수: {count}")
        logger.info(f"최종 응답 길이: {len(res)}")
        return res                
    except Exception as e:
        logger.error(f"API 호출 중 예외 발생: {str(e)}")
        return f"API 호출 중 오류 발생: {str(e)}"

def query_sds_agent(message: str) -> str:
    """
    SDS AI 에이전트에 메시지를 전송하고 응답을 받는 함수
    
    Args:
        message (str): 전송할 메시지
        
    Returns:
        str: SDS AI의 응답
    """
    logger.info(f"query_sds_agent 호출됨 - 메시지: {message}")
    
    # 요청 본문 구성
    request_body = {
        "model_type": "Gauss2",
        "contents": [message],
        "llmConfig": {
            "do_sample": True,
            "max_new_tokens": 512,
            "return_full_text": False,
            "seed": None,
            "top_k": 14,
            "top_p": 0.8,
            "temperature": 0.7,
            "repetition_penalty": 1.2,
            "decoder_input_details": False,
            "details": False,
        },
        "isStream": True
    }

    # API 호출 및 응답 처리
    response = get_json_events(headers, request_body)
    logger.info(f"query_sds_agent 응답 완료 - 응답 길이: {len(response)}")
    return response

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sds_functions.py <message>")
        sys.exit(1)
    
    test_message = sys.argv[1]
    logger.info(f"테스트 메시지: {test_message}")
    response = query_sds_agent(test_message)
    print(response)

