# 📊 주식 정보 검색 시스템 (`stock_info_nori_index`)

본 프로젝트는 **Elasticsearch + Streamlit**을 활용하여 **주식 정보를 검색할 수 있는 시스템**입니다.  
한국거래소(KRX)에서 데이터를 가져와 Elasticsearch에 저장하고, 이를 Streamlit을 통해 검색할 수 있도록 구현하였습니다.

---

## 🚀 1. 프로젝트 개요
본 프로젝트는 다음과 같은 기능을 제공합니다.

✅ **KRX에서 주식 정보를 자동으로 크롤링하여 Elasticsearch에 저장**  
✅ **Elasticsearch의 형태소 분석기(`nori_tokenizer`)를 적용하여 업종 및 주요 제품 필드 검색 최적화**  
✅ **Streamlit을 활용하여 사용자 친화적인 검색 인터페이스 제공**  
✅ **주식 종목명, 업종, 주요 제품을 검색할 수 있도록 최적화된 검색 기능 지원**  
