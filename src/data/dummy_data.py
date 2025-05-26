"""
더미 데이터를 관리하는 모듈입니다.
추천 질문과 답변을 포함합니다.
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def load_markdown_content(filename: str) -> str:
    """마크다운 파일의 내용을 읽어오는 함수"""
    try:
        file_path = Path(__file__).parent / "md" / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading markdown file {filename}: {str(e)}")
        return ""

# 일상 대화 더미 데이터
DAILY_CONVERSATIONS = {
    "greeting": {
        "patterns": ["안녕", "반가워", "하이", "hi", "hello"],
        "answers": {
            "ms": "안녕하세요! 무엇을 도와드릴까요?",
            "aws": "안녕하세요! 무엇을 도와드릴까요?",
            "sds": "안녕하세요! 무엇을 도와드릴까요?"
        }
    },
    "farewell": {
        "patterns": ["잘가", "안녕히", "바이", "bye", "goodbye"],
        "answers": {
            "ms": "안녕히 가세요! 또 궁금하신 점이 있으시면 언제든 찾아주세요.",
            "aws": "안녕히 가세요! 또 궁금하신 점이 있으시면 언제든 찾아주세요.",
            "sds": "안녕히 가세요! 또 궁금하신 점이 있으시면 언제든 찾아주세요."
        }
    },
    "weather": {
        "patterns": ["날씨", "오늘 날씨", "날씨가 어때", "비가 올까"],
        "answers": {
            "ms": "서울의 현재 날씨는 맑고 기온은 23도입니다. 오늘 하루 쾌적한 날씨가 계속될 예정입니다."
        }
    },
    "gratitude": {
        "patterns": ["고마워", "감사합니다", "감사해요", "고맙습니다"],
        "answers": {
            "ms": "천만에요! 더 필요한 것이 있으시다면 언제든 말씀해주세요."
        }
    },
    "mood": {
        "patterns": ["기분이 어때", "어떻게 지내", "잘 지내", "기분이 좋아"],
        "answers": {
            "ms": "저는 항상 좋은 기분이에요! 고객님은 어떠신가요?"
        }
    },
    "other": {
        "patterns": ["*"],
        "answers": {
            "ms": "죄송합니다. 그 질문에 대해서는 답변하기 어렵네요. 다른 질문을 해주시겠어요?"
        }
    }
}

# 마크다운 파일에서 내용 로드
곰철수_insurance_analysis_ms = load_markdown_content("곰철수_insurance_analysis_ms.md")
곰철수_insurance_analysis_aws = load_markdown_content("곰철수_insurance_analysis_aws.md")
곰철수_insurance_analysis_sds = load_markdown_content("곰철수_insurance_analysis_sds.md")

곰철수_health_risk_prediction_ms = load_markdown_content("곰철수_health_risk_prediction_ms.md")
곰철수_health_risk_prediction_aws = load_markdown_content("곰철수_health_risk_prediction_aws.md")
곰철수_health_risk_prediction_sds = load_markdown_content("곰철수_health_risk_prediction_sds.md")

곰철수_product_recommendation_ms = load_markdown_content("곰철수_product_recommendation_ms.md")
곰철수_product_recommendation_aws = load_markdown_content("곰철수_product_recommendation_aws.md")
곰철수_product_recommendation_sds = load_markdown_content("곰철수_product_recommendation_sds.md")

곰영희_insurance_analysis_ms = load_markdown_content("곰영희_insurance_analysis_ms.md")
곰영희_insurance_analysis_aws = load_markdown_content("곰영희_insurance_analysis_aws.md")
곰영희_insurance_analysis_sds = load_markdown_content("곰영희_insurance_analysis_sds.md")

곰영희_health_risk_prediction_ms = load_markdown_content("곰영희_health_risk_prediction_ms.md")
곰영희_health_risk_prediction_aws = load_markdown_content("곰영희_health_risk_prediction_aws.md")
곰영희_health_risk_prediction_sds = load_markdown_content("곰영희_health_risk_prediction_sds.md")

곰영희_product_recommendation_ms = load_markdown_content("곰영희_product_recommendation_ms.md")
곰영희_product_recommendation_aws = load_markdown_content("곰영희_product_recommendation_aws.md")
곰영희_product_recommendation_sds = load_markdown_content("곰영희_product_recommendation_sds.md")

곰순이_insurance_analysis_ms = load_markdown_content("곰순이_insurance_analysis_ms.md")
곰순이_insurance_analysis_aws = load_markdown_content("곰순이_insurance_analysis_aws.md")
곰순이_insurance_analysis_sds = load_markdown_content("곰순이_insurance_analysis_sds.md")

곰순이_health_risk_prediction_ms = load_markdown_content("곰순이_health_risk_prediction_ms.md")
곰순이_health_risk_prediction_aws = load_markdown_content("곰순이_health_risk_prediction_aws.md")
곰순이_health_risk_prediction_sds = load_markdown_content("곰순이_health_risk_prediction_sds.md")

곰순이_product_recommendation_ms = load_markdown_content("곰순이_product_recommendation_ms.md")
곰순이_product_recommendation_aws = load_markdown_content("곰순이_product_recommendation_aws.md")
곰순이_product_recommendation_sds = load_markdown_content("곰순이_product_recommendation_sds.md")

곰돌이_insurance_analysis_ms = load_markdown_content("곰돌이_insurance_analysis_ms.md")
곰돌이_insurance_analysis_aws = load_markdown_content("곰돌이_insurance_analysis_aws.md")
곰돌이_insurance_analysis_sds = load_markdown_content("곰돌이_insurance_analysis_sds.md")

곰돌이_health_risk_prediction_ms = load_markdown_content("곰돌이_health_risk_prediction_ms.md")
곰돌이_health_risk_prediction_aws = load_markdown_content("곰돌이_health_risk_prediction_aws.md")
곰돌이_health_risk_prediction_sds = load_markdown_content("곰돌이_health_risk_prediction_sds.md")

곰돌이_product_recommendation_ms = load_markdown_content("곰돌이_product_recommendation_ms.md")
곰돌이_product_recommendation_aws = load_markdown_content("곰돌이_product_recommendation_aws.md")
곰돌이_product_recommendation_sds = load_markdown_content("곰돌이_product_recommendation_sds.md")


# 사용자별 추천 질문 데이터
USER_RECOMMENDED_QUESTIONS = {
    "곰철수": {
        "insurance_analysis": {
            "question": "내 보험을 분석해서 상품을 추천해줘",
            "answers": {
                "ms": 곰철수_insurance_analysis_ms,
                "aws": 곰철수_insurance_analysis_aws,
                "sds": 곰철수_insurance_analysis_sds
            }
        },
        "health_risk_prediction": {
            "question": "건강검진 결과를 분석해줘",
            "answers": {
                "ms": 곰철수_health_risk_prediction_ms,
                "aws": 곰철수_health_risk_prediction_aws,
                "sds": 곰철수_health_risk_prediction_sds
            }
        },
        "product_recommendation": {
            "question": "나에게 맞는 상품을 추천해줘",
            "answers": {
                "ms": 곰철수_product_recommendation_ms,
                "aws": 곰철수_product_recommendation_aws,
                "sds": 곰철수_product_recommendation_sds
            }
        },
    },
    "곰영희": {
        "insurance_analysis": {
            "question": "내 보험을 분석해서 상품을 추천해줘",
            "answers": {
                "ms": 곰영희_insurance_analysis_ms,
                "aws": 곰영희_insurance_analysis_aws,
                "sds": 곰영희_insurance_analysis_sds
            }
        },
        "health_risk_prediction": {
            "question": "건강검진 결과를 분석해줘",
            "answers": {
                "ms": 곰영희_health_risk_prediction_ms,
                "aws": 곰영희_health_risk_prediction_aws,
                "sds": 곰영희_health_risk_prediction_sds
            }
        },
        "product_recommendation": {
            "question": "나에게 맞는 상품을 추천해줘",
            "answers": {
                "ms": 곰영희_product_recommendation_ms,
                "aws": 곰영희_product_recommendation_aws,
                "sds": 곰영희_product_recommendation_sds
            }
        },

    },
    "곰순이": {
        "insurance_analysis": {
            "question": "내 보험을 분석해서 상품을 추천해줘",
            "answers": {
                "ms": 곰순이_insurance_analysis_ms,
                "aws": 곰순이_insurance_analysis_aws,
                "sds": 곰순이_insurance_analysis_sds
            }
        },
        "health_risk_prediction": {
            "question": "건강검진 결과를 분석해줘",
            "answers": {
                "ms": 곰순이_health_risk_prediction_ms,
                "aws": 곰순이_health_risk_prediction_aws,
                "sds": 곰순이_health_risk_prediction_sds
            }
        },
        "product_recommendation": {
            "question": "나에게 맞는 상품을 추천해줘",
            "answers": {
                "ms": 곰순이_product_recommendation_ms,
                "aws": 곰순이_product_recommendation_aws,
                "sds": 곰순이_product_recommendation_sds
            }
        }
    },
    "곰돌이": {
        "insurance_analysis": {
            "question": "내 보험을 분석해서 상품을 추천해줘",
            "answers": {
                "ms": 곰돌이_insurance_analysis_ms,
                "aws": 곰돌이_insurance_analysis_aws,
                "sds": 곰돌이_insurance_analysis_sds
            }
        },
        "health_risk_prediction": {
            "question": "건강검진 결과를 분석해줘",
            "answers": {
                "ms": 곰돌이_health_risk_prediction_ms,
                "aws": 곰돌이_health_risk_prediction_aws,
                "sds": 곰돌이_health_risk_prediction_sds
            }
        },
        "product_recommendation": {
            "question": "나에게 맞는 상품을 추천해줘",
            "answers": {
                "ms": 곰돌이_product_recommendation_ms,
                "aws": 곰돌이_product_recommendation_aws,
                "sds": 곰돌이_product_recommendation_sds
            }
        },
 
    }
}

# 추천 질문 데이터
RECOMMENDED_QUESTIONS = USER_RECOMMENDED_QUESTIONS["곰철수"]  # 기본값으로 곰철수의 데이터 사용 