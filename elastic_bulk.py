# elastic_bulk.py
from elasticsearch import Elasticsearch, helpers
import pandas as pd
import json

def get_stock_info():
    base_url = "http://kind.krx.co.kr/corpgeneral/corpList.do"
    method = "download"
    url = f"{base_url}?method={method}"

    df = pd.read_html(url, header=0, encoding='euc-kr')[0]

    # ✅ 필요한 필드만 유지
    df = df[['종목코드', '회사명', '업종', '주요제품', '상장일']]

    # ✅ 필드명 영문화
    df.columns = ['stock_code', 'company_name', 'industry', 'main_products', 'listing_date']

    # ✅ 종목코드 6자리 포맷 적용
    df['stock_code'] = df['stock_code'].apply(lambda x: f"{x:06d}")

    # ✅ Null 값 처리 (dropna() 대신 fillna("N/A") 사용)
    df = df.fillna("N/A")

    # ✅ 데이터 개수 및 샘플 출력
    print(f"📌 데이터프레임 로드 완료! 데이터 개수: {len(df)}개")
    print(df.head())

    return df

# ✅ 데이터 로드
df = get_stock_info()

# ✅ 데이터프레임이 비어있는지 확인 후 종료
if df.empty:
    print("❌ 오류: 데이터프레임이 비어 있습니다! 데이터를 확인하세요.")
    exit()

# ✅ JSON 변환 (여기에서 이전 코드 누락 문제 해결)
json_records = json.loads(df.to_json(orient='records'))

# ✅ Elasticsearch 연결
es = Elasticsearch("http://localhost:9200", http_compress=True)
index_name = 'stock_info_nori_index'

# ✅ 기존 인덱스 삭제 후 재생성
if es.indices.exists(index=index_name):
    print(f"⚠️ 기존 인덱스 '{index_name}' 삭제 중...")
    es.indices.delete(index=index_name, ignore_unavailable=True)
    print(f"✅ 인덱스 '{index_name}' 삭제 완료.")

# ✅ Elasticsearch 매핑 설정 (Synonym 없음)
mapping = {
    "settings": {
        "analysis": {
            "analyzer": {
                "keyword_analyzer": {  # ✅ 회사명 검색용 (정확한 검색)
                    "tokenizer": "keyword"
                },
                "my_nori_analyzer": {  # ✅ 업종 및 주요 제품 검색용 (형태소 분석)
                    "tokenizer": "nori_tokenizer",
                    "char_filter": ["html_strip"],
                    "filter": ["nori_readingform", "lowercase"]
                }
            },
            "tokenizer": {
                "nori_tokenizer": {  # ✅ 사용자 사전 없이 기본 형태소 분석기 적용
                    "type": "nori_tokenizer"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "stock_code": {"type": "keyword"},
            "company_name": {"type": "text", "analyzer": "keyword_analyzer", "boost": 3.0},  # ✅ 회사명 검색 가중치 3.0
            "industry": {"type": "text", "analyzer": "my_nori_analyzer", "boost": 2.0},  # ✅ 업종 검색 가중치 2.0
            "main_products": {"type": "text", "analyzer": "my_nori_analyzer", "boost": 1.5},  # ✅ 주요 제품 검색 가중치 1.5
            "listing_date": {"type": "date", "format": "yyyy-MM-dd"}
        }
    }
}

# ✅ 새로운 인덱스 생성
print(f"📌 새로운 인덱스 '{index_name}' 생성 중...")
es.indices.create(index=index_name, body=mapping, ignore=400)
print(f"✅ 인덱스 '{index_name}' 생성 완료!")

# ✅ 데이터 Elasticsearch에 적재
actions = [
    {
        "_op_type": "index",
        "_index": index_name,
        "_source": row
    }
    for row in json_records
]

# ✅ Bulk API 실행
success, failed = helpers.bulk(es, actions, refresh='wait_for', stats_only=True)


# ✅ 데이터가 정상적으로 저장되었는지 확인
count = es.count(index=index_name)['count']
print(f"✅ 최종 저장된 데이터 개수: {count}개")

