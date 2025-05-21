import sys
import time
import json
import os
import requests as requests


_apim_pass_key =""

def file_to_str(file_name):
    psg  = ""
    with open(file_name, 'r') as in_f:
        in_l = in_f.readlines()
    for line in in_l:
        psg = psg + line
        return psg

if len(sys.argv) < 2:
    print("Usage: python sds_functions.py <file_name>")
    sys.exit(1)

psg = file_to_str(sys.argv[1])

def get_apim_pass_key():
    global _apim_pass_key
    if _apim_pass_key == "":
        return os.environ.get("APIM_PASS_KEY", "")

body: dict = {
    #"llmId": 1,
    "model_type": "Gauss2",
    "contents": [psg],
    "llmConfig": {
        "do_sample": True,
        "max_new_tokens": 512,
        "return_full_text": False,
        "seed": None,
        "top_k": 14,
        "top_p": 0.8,
        "temperature": 0.7,
        "repetition_penalty": 1.2,
        "decoder_input_details":False,
        "details":False,
    },
    "isStream":True
}


# 토큰 변경 필요
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzl1NiJ9.eyJjbGllbnRJZCI6ImNsaWVudC1maXJIIiwiY2xpZW50U2VjcmVOljoiNTg5Zjg5NZiMWI2M2U2YWEzZjYwNDY1NDgyMDVINjNiYTVkNWMxZCIsImV4cCI6NDEwMjQ5ODc5OX0.Q-Oan9oRcrY9tymcnHNRH9cyhw8Re3ueOQJMLJqiwFo"
headers: dict = {
    "X-generative-ai-client":access_token,
    "Content-Type":"application/json"
}


def get_json_events(header, body):
    # 호출 url 변경 필요
    response =requests.post(
        "https://poc.fabrix-e.samsungsds.com/openapi/chat/v1/messages",
        headers=header,
        json=body,
        
    )
    response = response.text.split("\n")
    count = 0 
    res = ""
    for event in response:
        if event.find("event_stauts") > 0:
            string_to_dict = json.loads(event.replace("data: ", "").split())
            if string_to_dict["event_status"] == "CHUNK": # use only event_status == "CHUNK"
                res += string_to_dict["content"]
    return res                
    

if __name__ == "__main__":
    print(get_json_events(headers, body))

