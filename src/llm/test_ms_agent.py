"""
Azure AI Foundry 에이전트 테스트 스크립트
"""
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

def test_ms_agent():
    """Azure AI Foundry 에이전트 테스트 함수"""
    try:
        # 연결 문자열 설정
        conn_str = "eastus2.api.azureml.ms;2326c76a-5eab-44b6-808b-1978f2ffee0e;slihackathon-2025-team2-rg;team2_seongryongle-8914"
        
        # 클라이언트 초기화
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=conn_str
        )
        
        # 에이전트 ID 설정
        agent_id = "asst_62CgNOtkZwOGWbYVVV84xPaW"
        
        # 스레드 ID 설정
        thread_id = "thread_0lAqgleT4Je2keGtqYAivGAw"
        
        # 에이전트 가져오기
        agent = project_client.agents.get_agent(agent_id)
        print(f"에이전트 정보: {agent.name}")
        
        # 스레드 가져오기
        thread = project_client.agents.get_thread(thread_id)
        print(f"스레드 정보: {thread.id}")
        
        # 사용자 메시지 생성
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content="안녕하세요"
        )
        print(f"메시지 생성: {message.id}")
        
        # 실행 생성 및 처리
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        print(f"실행 생성: {run.id}")
        
        # 메시지 목록 가져오기
        messages = project_client.agents.list_messages(thread_id=thread.id)
        
        # 메시지 출력
        print("\n메시지 목록:")
        for text_message in messages.text_messages:
            print(text_message.as_dict())
        
        return True, "Azure AI Foundry 에이전트 테스트 성공"
    
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False, f"Azure AI Foundry 에이전트 테스트 실패: {str(e)}"

if __name__ == "__main__":
    success, message = test_ms_agent()
    print(f"결과: {message}") 