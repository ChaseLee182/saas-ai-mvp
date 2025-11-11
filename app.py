import streamlit as st
import requests
import json
import os

# --- 配置常量 ---
# Google Gemini API URL (使用 gemini-2.5-flash 模型)
GOOGLE_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
OPENAI_API_BASE_URL = "https://api.openai.com/v1/chat/completions"

# --- 辅助函数：调用 API ---
def call_api(api_key, is_google_key, prompt, model, proxy_url=None):
    """根据密钥类型调用相应的 API (OpenAI 或 Google)。"""
    headers = {
        "Content-Type": "application/json",
    }
    
    # 使用 requests.Session 来处理代理
    session = requests.Session()
    if proxy_url:
        st.info(f"正在使用代理: {proxy_url}")
        session.proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

    if is_google_key:
        # Google Gemini API 调用
        url = f"{GOOGLE_API_BASE_URL}?key={api_key}"
        
        # 针对 Streamlit 应用场景构建的系统提示
        system_instruction = (
            "您是一位资深的 B2B SaaS 营销文案专家。请根据提供的技术更新和核心价值，"
            "将其转化为一篇专业、引人注目的营销文案。文案应突出商业价值和用户利益，"
            "使用专业且简洁的语言。"
        )

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "config": {
                # 注意: Google API 的 system instruction 放在 config 内部
                "systemInstruction": system_instruction 
            }
        }
        
        try:
            # 尝试调用 Google API
            response = session.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status() # 抛出 HTTP 错误，如 400, 429
            
            result = response.json()
            # 提取 Google Gemini 的文本
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            return generated_text
        
        except requests.exceptions.RequestException as e:
            # 捕获网络、超时或 HTTP 错误
            error_message = f"Google API 调用失败。错误信息： {e}"
            st.error(error_message)
            st.warning("请确认您的网络连接或代理设置是否允许访问 Google API。")
            st.stop()

    else:
        # OpenAI API 调用 (保持不变，但仍使用 Session 处理代理)
        url = OPENAI_API_BASE_URL
        headers["Authorization"] = f"Bearer {api_key}"
        
        # 针对 Streamlit 应用场景构建的系统提示
        system_prompt = (
            "You are a Senior B2B SaaS Marketing Copywriter. Convert the following technical updates and core values "
            "into a professional, compelling marketing copy. Highlight business value and user benefits using "
            "professional and concise language."
        )

        data = {
            "model": model, # 使用 gpt-3.5-turbo
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000
        }
        
        try:
            # 尝试调用 OpenAI API
            response = session.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result['choices'][0]['message']['content']
            return generated_text
        
        except requests.exceptions.RequestException as e:
            error_message = f"OpenAI API 请求失败。请检查您的密钥、网络连接或代理设置。详细错误: {e}"
            st.error(error_message)
            st.warning("请确认您的 OpenAI 密钥是否有效（余额充足）或网络连接正常。")
            st.stop()


# --- Streamlit 界面 ---
st.set_page_config(page_title="B2B SaaS 内容 AI 生成器", layout="wide")

# 标题和介绍
st.markdown("""
<div style='text-align: center;'>
    <h1 style='color: #4A90E2; font-size: 3em;'>🚀 B2B SaaS 内容 AI 生成器</h1>
    <p style='font-size: 1.2em;'>通过 AI 将技术更新转化为专业的市场营销文案。</p>
</div>
---
""", unsafe_allow_html=True)


# --- 侧边栏：API 密钥配置 (包含代理) ---
with st.sidebar:
    st.header("🔑 API 密钥配置 (快速修复)")
    
    # API 密钥输入
    api_key = st.text_input(
        "输入您的通用 AI API 密钥 (OpenAI sk- 或 Google AIzaS-)", 
        type="password", 
        key="api_key_input"
    )

    is_google_key = api_key.startswith("AIzaS") # 修正：只需要检查 AIzaS 开头
    
    if api_key:
        if is_google_key:
            st.success("密钥已输入，将使用 Google Gemini API。")
            model_used = "gemini-2.5-flash"
        elif api_key.startswith("sk-"):
            st.success("密钥已输入，将使用 OpenAI GPT API。")
            model_used = "gpt-3.5-turbo"
        else:
            st.warning("密钥格式不识别。请确保输入正确的 OpenAI (sk-) 或 Google (AIzaS-) 密钥。")
            st.stop()
    else:
        st.info("请输入您的 API 密钥以启用功能。")
        st.stop()

    # --- 新增代理设置 (解决 400 错误的关键尝试) ---
    st.markdown("---")
    st.subheader("🌐 网络/代理设置 (可选)")
    proxy_url = st.text_input(
        "HTTP/HTTPS 代理 URL (格式: http://host:port)",
        placeholder="例如: http://127.0.0.1:7890",
        key="proxy_url_input"
    )

    # --- 文案风格设置 ---
    st.markdown("---")
    st.subheader("📝 文案风格设置")
    target_platform = st.selectbox(
        "目标平台",
        ("Blog Post", "Newsletter/Email", "Social Media (LinkedIn)"),
        key="target_platform_select"
    )
    
    tone_and_audience = st.selectbox(
        "语气和受众",
        ("Professional (SaaS, B2B)", "Excited (Startup, Product Manager)", "Formal (Enterprise, CTO)"),
        key="tone_and_audience_select"
    )

# --- 主内容区域 ---

st.header("1. 粘贴您的技术更新或功能说明")
technical_update = st.text_area(
    "输入技术更新日志或功能说明 (必须)",
    value="""E.g., - Core Feature Update: We refactored the data processing pipeline to use a new asynchronous queue, which reduces latency for large file uploads by an average of 35%.
- Bug Fixes: Fixed a critical bug where users in the European region could not apply discount codes to subscription renewals.
- New API Endpoint: Added a new /api/v2/webhooks/status endpoint for better external monitoring of real-time event delivery.
""",
    height=250
)

st.subheader("品牌注释/核心价值 (可选)")
core_value = st.text_input(
    "E.g., Our core value is 'Collaboration First' or 'We focus on security and reliability above all else.'",
    value="Our core value is 'Collaboration First'",
)

if st.button("生成专业内容!"):
    if not technical_update.strip():
        st.error("请输入技术更新或功能说明才能生成内容。")
    else:
        # 构造给 AI 的最终提示
        final_prompt = f"""
        请将以下技术更新日志转化为一篇面向 '{tone_and_audience}' 受众的 '{target_platform}' 营销文案。
        
        ---
        
        **技术更新:**
        {technical_update}
        
        **品牌核心价值:**
        {core_value}
        
        ---
        
        **要求:**
        1. 必须使用中文。
        2. 重点突出对客户的价值和商业益处，而不是纯粹的技术实现。
        3. 语气必须符合 '{tone_and_audience}' 的风格。
        4. 确保内容适合 '{target_platform}' 的格式。
        """

        with st.spinner(f"正在使用 {model_used} 生成内容..."):
            # 调用 API
            generated_copy = call_api(api_key, is_google_key, final_prompt, model_used, proxy_url)
            
            # 显示结果
            st.markdown("---")
            st.subheader(f"🎉 生成的 {target_platform} 文案")
            st.info(f"模型：{model_used} | 语气：{tone_and_audience}")
            st.markdown(generated_copy)

st.markdown("---")
st.markdown("© 2024 SaaS AI MVP. Powered by Gemini/GPT API.")