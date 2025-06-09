from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Ollama 모델을 불러옵니다.
llm = ChatOllama(model="llama3.2:latest")

# 프롬프트
prompt = ChatPromptTemplate.from_template("{topic} is cute")

# 체인 생성
chain = prompt | llm | StrOutputParser()

# 간결성을 위해 응답은 터미널에 출력됩니다.
answer = chain.invoke({"topic": "lama"})

print(answer)