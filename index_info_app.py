# index_info_app.py
import streamlit as st
import pandas as pd
from elastic_api import search_stock

st.set_page_config(page_title="📈 주식 정보 검색 시스템", layout="wide")

st.title("📈 주식 정보 검색 시스템")

# ✅ 좌측(검색 필드)과 우측(검색 결과)로 화면 분할
col1, col2 = st.columns([1, 2])  # 좌측 1, 우측 2 비율

with col1:
    st.header("🔍 검색 필드")
    
    # ✅ 회사명 검색 필드
    company_query = st.text_input("🏢 회사명을 입력하세요:")

    # ✅ 업종 및 주요 제품 검색 필드
    industry_or_product_query = st.text_input("🛠️ 업종 또는 주요 제품을 입력하세요:")

with col2:
    st.header("📋 검색 결과")

    if company_query or industry_or_product_query:
        results = search_stock(company_query, industry_or_product_query)

        # ✅ 필드명을 Elasticsearch와 일치하도록 수정
        data = [
            {
                "종목 코드": hit.to_dict().get("stock_code", ""),
                "회사명": hit.to_dict().get("company_name", ""),
                "업종": hit.to_dict().get("industry", ""),
                "주요 제품": hit.to_dict().get("main_products", "N/A"),
                "상장일": hit.to_dict().get("listing_date", "")
            }
            for hit in results
        ]

        if data:
            df = pd.DataFrame(data)

            # ✅ 검색 결과 표 출력
            st.dataframe(df)

            # ✅ 기업 선택 기능 추가 (클릭하면 상세 정보 표시)
            selected_company = st.selectbox("📌 상세 정보를 볼 기업을 선택하세요:", df["회사명"])

            # ✅ 선택한 기업의 상세 정보 찾기
            selected_data = df[df["회사명"] == selected_company].to_dict(orient="records")[0]

            # ✅ 상세 정보 보기
            with st.expander(f"📋 {selected_company} 상세 정보 보기"):
                st.markdown(f"🔹 **종목 코드:** `{selected_data['종목 코드']}`")
                st.markdown(f"🏢 **업종:** `{selected_data['업종']}`")
                st.markdown(f"🛠️ **주요 제품:** `{selected_data['주요 제품']}`")
                st.markdown(f"📅 **상장일:** `{selected_data['상장일']}`")
        else:
            st.warning("⚠️ 검색 결과가 없습니다.")
