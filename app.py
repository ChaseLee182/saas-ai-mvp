# -*- coding: utf-8 -*-
# --- 模块导入 ---
import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError
import json
import time

# --- 配置 Streamlit 页面 ---
st.set_page_config(
    page_title="SaaS AI 文案生成器 (最终稳定版)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 应用程序标题和描述 ---
st.title("🚀 B2B SaaS 内容 AI 生成 MVP")
st.markdown("通过 AI 将技术更新日志转化为专业的市场营销文案。")

# --- 状态管理和初始化 ---
# 确保 AI 客户端只初始化一次
@st.cache_resource
def initialize_gemini_client():
    """
    初始化 Gemini API 客户端。
    强制使用 st.secrets 读取 API 密钥，确保与 Streamlit Cloud 兼容。
    """
    try:
        # 尝试从 Streamlit secrets 中获取 API 密钥
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        return client
    except KeyError:
        # 如果密钥不存在，则打印错误并返回 None
        st.error(
            "无法找到 GEMINI_API_KEY。请在 Streamlit Secrets 中配置您的 API 密钥。"
        )
        return None
    except Exception as e:
        st.error(f"AI 客户端初始化失败: {e}")
        return None

# 初始化客户端
ai_client = initialize_gemini_client()

# --- 内容生成逻辑 ---

def generate_content(client, log_content, style_prompt, format_prompt):
    """
    调用 Gemini API 生成内容。
    使用 JSON 模式确保输出结构化，便于解析。
    """
    if not client:
        return {"title": "AI 客户端未初始化", "body": "请检查 API 密钥配置。"}

    # 构建完整的系统指令
    system_instruction = (
        "您是一个世界级的 B2B SaaS 产品营销专家。您的任务是将晦涩的技术更新日志 "
        "转化为引人注目的市场营销内容。请使用专业的、以客户为中心的语言，并突出价值。"
        f"内容风格要求: {style_prompt}. 内容格式要求: {format_prompt}. "
        "您必须严格以 JSON 格式返回结果，包含 'title' (标题) 和 'body' (正文)。"
        "正文应使用 Markdown 格式。"
    )

    # 用户的输入和指令
    user_prompt = f"请将以下技术更新日志转化为市场内容：\n\n--- 技术日志 ---\n{log_content}"

    # 配置模型调用
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "title": {"type": "STRING", "description": "吸引人的营销标题。"},
                "body": {"type": "STRING", "description": "完整的文章正文，使用Markdown格式。"}
            }
        },
    )

    try:
        # 使用 gemini-2.5-flash-preview-09-2025 模型进行内容生成
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-09-2025',
            contents=[user_prompt],
            config=config,
        )

        # 解析 JSON 响应
        json_text = response.candidates[0].content.parts[0].text.strip()
        
        # 尝试清理和解析 JSON
        try:
            # 有时模型输出可能包含额外的markdown标记，需要清理
            if json_text.startswith("```json"):
                json_text = json_text[7:].strip()
            if json_text.endswith("```"):
                json_text = json_text[:-3].strip()
                
            parsed_data = json.loads(json_text)
            return parsed_data

        except json.JSONDecodeError as e:
            st.error(f"AI 响应解析失败 (JSONDecodeError): {e}")
            st.markdown(f"**原始响应 (请报告此错误):**\n```\n{json_text}\n```")
            return {"title": "解析错误", "body": "AI 返回的格式不正确，请重试。"}

    except APIError as e:
        # 处理 API 相关的错误（例如，权限、速率限制）
        st.error(f"Gemini API 错误: {e}")
        return {"title": "API 错误", "body": "AI 服务调用失败。请检查您的 API 密钥是否有效或重试。"}
    except Exception as e:
        # 处理其他未知错误
        st.exception(e)
        return {"title": "未知错误", "body": "生成过程中发生了一个意外错误。"}

# --- Streamlit UI 侧边栏和输入 ---

with st.sidebar:
    st.header("🖊️ 内容输入和定制")

    # 1. 技术更新日志输入
    technical_log = st.text_area(
        "输入技术更新日志或功能说明 (必填)",
        value="重构了数据处理管道，将大型数据集的延迟降低了 35%。删除了对旧版 API 的支持。",
        height=200,
        help="提供清晰的技术细节，AI 将把它们转化为市场语言。"
    )

    # 2. 文案风格选择
    st.subheader("选择文案风格")
    style_options = {
        "Professional (SaaS, B2B)": "使用专业的 B2B 语言，专注于价值、可靠性和 ROI (投资回报率)。",
        "Enthusiastic (Startup)": "使用充满活力、激动人心的语气，适合初创公司和快速发布。",
        "Formal (Enterprise)": "使用正式、权威的语气，适合大型企业和官方公告。",
        "Casual (Community)": "使用友好、轻松的语气，适合社区更新和发布说明。"
    }
    selected_style = st.selectbox(
        "内容风格",
        options=list(style_options.keys()),
        index=0
    )
    st.info(style_options[selected_style])
    
    # 3. 目标格式选择
    st.subheader("选择目标格式")
    format_options = {
        "Blog Post (Medium)": "撰写一篇中等长度的博客文章，结构清晰，引人入胜。",
        "Press Release (Short)": "撰写一份简洁的官方新闻稿，突出最重要的商业影响。",
        "Email Announcement (Client-Facing)": "撰写一封面向客户的邮件，简洁地通知他们新功能。",
        "Product Changelog Entry": "撰写一份清晰的产品更新日志条目，简要概述新功能。"
    }
    selected_format = st.selectbox(
        "目标内容格式",
        options=list(format_options.keys()),
        index=0
    )
    st.info(format_options[selected_format])

# --- 主内容区域和输出 ---

if st.button("✨ 生成专业内容！", type="primary"):
    if not technical_log:
        st.warning("请在左侧侧边栏中输入技术更新日志。")
    elif not ai_client:
        # 密钥错误已在初始化时处理，这里不再重复
        pass 
    else:
        # 组合风格和格式描述，传递给 AI
        style_prompt = style_options[selected_style]
        format_prompt = format_options[selected_format]

        with st.spinner("🚀 AI 正在基于最高标准生成文案... 请稍候..."):
            
            # 调用生成函数
            content = generate_content(
                ai_client,
                technical_log,
                style_prompt,
                format_prompt
            )

        # --- 显示结果 ---
        st.subheader("🎉 生成结果")
        
        # 确保内容有标题和正文
        if content.get("title") and content.get("body"):
            st.markdown(f"### {content['title']}")
            st.markdown("---")
            st.markdown(content['body'])
            
            # --- 额外功能（例如，复制）---
            st.download_button(
                label="📥 下载为 Markdown 文件",
                data=f"# {content['title']}\n\n{content['body']}",
                file_name="ai_generated_content.md",
                mime="text/markdown"
            )
        else:
            st.error("内容生成失败，请检查上方的错误信息。")