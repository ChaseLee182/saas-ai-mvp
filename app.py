# -*- coding: utf-8 -*-
import streamlit as st
import os
import requests
import json

# --- Configuration & Styling ---
st.set_page_config(layout="wide", page_title="B2B Content AI Generator MVP")

# Custom CSS for a professional look
st.markdown("""
<style>
.main-header {
    font-size: 36px !important;
    font-weight: 700;
    color: #007bff; /* Blue for branding */
    margin-bottom: 5px;
}
textarea, .stSelectbox {
    border-radius: 8px;
}
.stButton>button {
    background-color: #007bff;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 10px 20px;
    border: none;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: background-color 0.3s;
}
.stButton>button:hover {
    background-color: #0056b3;
}
.stAlert {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# --- LLM API Setup (Universal API) ---

# 使用 OpenAI 模型的通用 API 地址。
# 您可以使用任何兼容 OpenAI 格式的 API 服务。
API_URL = "https://api.openai.com/v1/chat/completions"
# 默认使用 GPT-4o 作为性能最高的模型
DEFAULT_MODEL = "gpt-4o" 

def generate_content_universal(api_key, technical_updates, brand_notes, platform, tone):
    """
    使用通用的 requests 库调用 OpenAI 风格的 API。
    如果用户输入的是 Google 密钥，尝试调用 Google API (虽然可能因网络而失败)。
    """
    
    # 动态切换模型和API URL
    if api_key.startswith("sk-"):
        # OpenAI 密钥
        model_to_use = DEFAULT_MODEL
        url_to_use = API_URL
        # 移除可能误导的Google API URL，确保使用OpenAI的
        os.environ.pop("GEMINI_API_KEY", None) 
    elif api_key.startswith("AIza"):
        # Google Gemini 密钥 (我们仍然尝试，但警告可能失败)
        st.warning("检测到 Google API 密钥。由于网络限制，调用可能会失败。强烈推荐使用 OpenAI 密钥 (sk-开头的)。")
        model_to_use = "gemini-2.5-flash"
        url_to_use = f"https://generativelanguage.googleapis.com/v1beta/models/{model_to_use}:generateContent"
        # 确保使用 Google API 密钥
        # 注意：此处需要特定的 Google Client配置，但为了简洁，我们尝试使用通用 POST
        # 实际生产中，Google API需要更复杂的客户端库配置，因此我们强烈推荐OpenAI路线
        # 这里的通用调用可能会失败，但我们尝试兼容
        
        # 重新定义 headers 和 payload 以适应 Google API 的不同结构
        
        system_instruction_google = f"""你是一位专业的B2B SaaS内容营销专家。你的任务是将技术更新和功能描述转化为引人入胜的、面向{platform}平台的营销文案。
        文案必须遵循以下风格：{tone}。
        品牌理念：'{brand_notes}'。
        你的输出必须是符合JSON Schema的。"""
        
        prompt_google = f"这是最新的技术更新日志：\n---\n{technical_updates}\n---\n请基于以上内容，生成一篇完整的、引人注目的{platform}帖子。"
        
        google_payload = {
            "contents": [{"parts": [{"text": prompt_google}]}],
            "systemInstruction": {"parts": [{"text": system_instruction_google}]},
            "config": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "generated_title": {"type": "STRING", "description": "为文案生成的引人注目的标题。"},
                        "generated_content": {"type": "STRING", "description": "完整的、可直接发布的B2B营销文案内容。"},
                    },
                    "required": ["generated_title", "generated_content"],
                }
            }
        }
        
        try:
            headers = {
                "Content-Type": "application/json",
                # Google API 密钥通常作为 URL 参数而非 Bearer Token
            }
            # 临时将 API 密钥作为 URL 参数
            response = requests.post(f"{url_to_use}?key={api_key}", headers=headers, json=google_payload, timeout=120)
            response.raise_for_status()
            
            # Google API 的响应解析
            response_json = response.json()
            json_text = response_json['candidates'][0]['content']['parts'][0]['text']
            # 尝试解析 JSON 字符串
            data = json.loads(json_text)
            return data["generated_title"], data["generated_content"]
            
        except Exception as e:
            st.error(f"⚠️ Google API 调用失败！请检查您的网络连接或使用更稳定的 OpenAI 密钥。错误信息: {e}")
            return None, None
            
    else:
        # 密钥格式不正确
        st.error("密钥格式不正确。请确保您输入的是以 'sk-' 开头的 OpenAI 密钥或有效的 Google API 密钥。")
        return None, None

    # --- 通用 API (OpenAI) 调用逻辑 ---
    # 仅在 'sk-' 密钥下执行
    try:
        # System Prompt
        system_prompt = f"""You are a world-class B2B SaaS Content Marketing Expert. Your task is to transform raw technical updates and feature descriptions into compelling, professional marketing copy suitable for a {platform} audience.
        The copy must adopt a {tone} style.
        Brand Guideline: '{brand_notes}'.
        Your output MUST be a valid JSON object following the provided schema, containing only the title and the content."""
        
        # User Prompt
        prompt = f"Here is the latest technical update log/description:\n---\n{technical_updates}\n---\nBased on this, generate a complete, engaging marketing post for the {platform} platform."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        
        payload = {
            "model": model_to_use,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.5,
        }
        
        response = requests.post(url_to_use, headers=headers, json=payload, timeout=120)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

        response_json = response.json()
        
        # 检查 OpenAI 响应结构
        if 'choices' in response_json and response_json['choices']:
            json_string = response_json['choices'][0]['message']['content']
            data = json.loads(json_string)
            return data["generated_title"], data["generated_content"]
        else:
            st.error(f"API 调用成功，但响应结构异常。原始响应: {response_json}")
            return None, None

    except requests.exceptions.RequestException as e:
        st.error(f"API 请求失败。请检查您的密钥、网络连接或代理设置。详细错误: {e}")
        return None, None
    except json.JSONDecodeError:
        st.error("AI 响应格式错误。请稍后重试。")
        return None, None
    except Exception as e:
        st.error(f"发生未知错误: {e}")
        return None, None


# --- Streamlit UI ---

st.markdown('<p class="main-header">🚀 B2B SaaS 内容 AI 生成 MVP</p>', unsafe_allow_html=True)
st.markdown("通过 AI 将技术更新日志转化为专业的市场营销文案。")

# --- Sidebar: API Key and Settings ---
with st.sidebar:
    st.markdown("### 🔑 API 密钥配置 (快速修复)")
    
    # 将输入框名称从 Gemini 改为 通用
    api_key_input = st.text_input(
        "输入您的通用 AI API 密钥 (OpenAI sk- 或 Google AIzaS-)",
        type="password",
        help="请粘贴您的 OpenAI 密钥 (sk-开头) 或 Google 密钥 (AIzaS-开头)。"
    )
    
    # 将密钥存储在 session_state 中
    if api_key_input:
        st.session_state['api_key'] = api_key_input
        st.success("密钥已输入，可以开始生成内容了！")
    elif 'api_key' in st.session_state:
         del st.session_state['api_key']

    st.markdown("---")
    st.markdown("### ⚙️ 文案风格设置")
    
    target_platform = st.selectbox(
        "目标平台",
        ["Blog Post", "LinkedIn Post", "Twitter Thread", "Email Newsletter"],
        index=0,
        key="platform"
    )

    tone_audience = st.selectbox(
        "语气和受众",
        ["Professional (SaaS, B2B)", "Excited and Technical (For Developers)", "Friendly and Educational (For Small Business)", "Bold and Visionary (For Executives)"],
        index=0,
        key="tone"
    )

# --- Main Content Area ---

st.markdown("### 1. 粘贴您的技术更新或功能说明")

technical_updates = st.text_area(
    "输入技术更新日志或功能说明 (必须)",
    height=250,
    placeholder="E.g., - Core Feature Update: We refactored the data processing pipeline to use a new asynchronous queue, which reduces latency for large file uploads by an average of 35%.\n- Bug Fixes: Fixed a critical bug where users in the European region could not apply discount codes to subscription renewals.\n- New API Endpoint: Added a new /api/v2/webhooks/status endpoint for better external monitoring of real-time event delivery.",
    key="updates"
)

brand_notes = st.text_area(
    "品牌注释/核心价值 (可选)",
    placeholder="E.g., Our core value is 'Collaboration First' or 'We focus on security and reliability above all else.'",
    height=80,
    key="notes"
)


# --- Generation Button ---
if st.button("生成专业内容！"):
    if not api_key_input:
        st.error("⚠️ 请先在侧边栏输入您的 API 密钥，然后重试。")
    elif not technical_updates:
        st.error("⚠️ 请在上方输入技术更新日志或功能说明。")
    else:
        with st.spinner("🚀 AI 正在将您的技术术语转化为营销内容，请稍候..."):
            
            # 调用通用生成函数
            title, content = generate_content_universal(
                api_key=api_key_input,
                technical_updates=technical_updates,
                brand_notes=brand_notes,
                platform=target_platform,
                tone=tone_audience
            )

        if title and content:
            st.session_state['generated_title'] = title
            st.session_state['generated_content'] = content
            st.success("🎉 内容生成成功！请在下方查看和编辑。")
            st.experimental_rerun() # Rerun to refresh the output area

# --- Output Area ---

if 'generated_title' in st.session_state and 'generated_content' in st.session_state:
    st.markdown("---")
    st.markdown("### 2. 生成结果 (查看 & 编辑)")
    
    # 标题显示
    st.markdown("#### 标题 (可编辑)")
    final_title = st.text_input(
        "Generated Title", 
        value=st.session_state['generated_title'], 
        key="final_title"
    )
    
    # 内容显示
    st.markdown("#### 文案内容 (可编辑)")
    final_content = st.text_area(
        "Generated Content (Review & Edit)",
        value=st.session_state['generated_content'],
        height=450,
        key="final_content"
    )

    st.markdown("---")
    st.markdown("### 3. 导出选项")
    
    # 确保保存最终编辑的内容到 session_state
    st.session_state['final_title'] = final_title
    st.session_state['final_content'] = final_content

    # 导出按钮
    col_copy, col_md = st.columns([1, 1])

    # 准备导出的 Markdown 文件内容
    final_text_export = f"# {st.session_state['final_title']}\n\n{st.session_state['final_content']}"

    # 下载 Markdown 按钮
    with col_md:
        st.download_button(
            label="下载 Markdown",
            data=final_text_export,
            file_name=f"{st.session_state['final_title'].lower().replace(' ', '_')}.md",
            mime="text/markdown"
        )
    
    # 复制内容按钮 (Streamlit 简单按钮无法直接复制，此处仅为占位和提示)
    with col_copy:
        st.button('复制文案内容 (请手动复制)', help="出于安全限制，Streamlit 简单按钮不能直接访问剪贴板，请手动复制下方的文案。")

# 清理 session_state 以防刷新混乱
if 'generated_title' in st.session_state and 'generated_content' in st.session_state:
    if st.button("清空并重新开始"):
        for key in ['generated_title', 'generated_content', 'final_title', 'final_content']:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()