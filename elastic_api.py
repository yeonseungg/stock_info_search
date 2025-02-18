# elastic_api.py
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

client = Elasticsearch('http://localhost:9200')
index_name = 'stock_info_nori_index'  # ✅ 기존 stock_info → stock_info_nori_index로 변경

def search_stock(company_name=None, industry_or_product=None):
    s = Search(index=index_name).using(client)

    should_clauses = []

    # ✅ 회사명 검색 (부분 일치 검색 적용)
    if company_name:
        should_clauses.append({
            "match_phrase_prefix": {
                "company_name": {  # ✅ 기존 "회사명" → "company_name" (영문 필드명으로 변경)
                    "query": company_name,
                    "boost": 2.5
                }
            }
        })
    
    # ✅ 업종 & 주요 제품 검색 (업종 가중치 증가)
    if industry_or_product:
        should_clauses.append({
            "multi_match": {
                "query": industry_or_product,
                "fields": ["industry^3", "company_name^2.5", "main_products^1.5"]  # ✅ 기존 "업종", "주요제품" → "industry", "main_products"
            }
        })

    if should_clauses:
        s = s.query("bool", should=should_clauses, minimum_should_match=1)

    s = s.sort({"_score": {"order": "desc"}})  # ✅ 점수가 높은 순서대로 정렬

    response = s.execute()
    return response
