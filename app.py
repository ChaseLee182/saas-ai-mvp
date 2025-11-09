# -*- coding: utf-8 -*-
import streamlit as st
import os
# 移除了 requests 和 BeautifulSoup 导入

# 导入 Google GenAI 库
from google import genai
from google.genai.errors import APIError

# --- 配置页面和样式 ---
# 必须是 Streamlit 脚本中的第一个命令，且参数必须是字符串
st.set_page_config(layout="wide", page_title="B2B Content AI Generator MVP")

# 使用 CSS 注入来调整布局和样式，使其看起来更专业
st.markdown(
    """
<style>
/* 自定义标题样式 */
.main-header {
    font-size: 36px !important;
    font-weight: 700;
    color: #007bff; /* 蓝色作为品牌强调色 */
    margin-bottom: 5px;
}
/* 调整输入框和选择框的圆角 */
.stTextArea, .stSelectbox {
    border-radius: 8px;
}
/* 主按钮样式 */
.stButton>button {
    background-color: #007bff;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    height: 3.5em; /* 按钮更高 */
    width: 100%; /* 按钮占满宽度 */
    font-size: 18px;
}
/* 将 Streamlit 默认的 'st.write' 字体放大一点 */
p {
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 1. 核心功能：AI 内容生成（调用 Gemini API）
# ---------------------------------------------------------

def generate_content_with_ai(tech_input, platform, tone, brand_notes, style_sample):
    """
    调用 Gemini API，根据用户输入和风格数据生成营销文案。
    """
    
    # 检查 API Key
    api_key = os.getenv("GEMINI_API_KEY") # 修正：这里变量名保持一致
    if not api_key:
        # 修正：返回信息中的字符串已用引号包围
        return ("ERROR: 无法找到 GEMINI_API_KEY。请在 Streamlit Cloud Secrets 中进行设置。", "API Key 缺失")

    try:
        client = genai.Client(api_key=api_key)
        
        # 构造详细的提示词 (Prompt Engineering)
        # 修正：使用三引号定义多行 f-string
        prompt = f"""
        你是一位顶级 SaaS 公司的专业内容营销专家。你的任务是将原始技术更新内容转化为高质量的营销文案。
        
        **关键指令：** 请严格模仿以下提供的“目标公司文案样本”的语言、语调、结构和专业度。
        
        --- 目标公司文案样本 (硬编码风格) ---
        {style_sample}
        --- 目标公司文案样本结束 ---
        
        原始技术内容 (Raw Tech Input):
        ---
        {tech_input}
        ---
        
        生成要求:
        1. 目标平台: {platform}
        2. 语调: {tone}
        3. 品牌特殊指令: {brand_notes if brand_notes else '无特殊指令'}
        4. **结构化输出**: 必须包含清晰的“### 核心价值 (Value Proposition)”和“### 关键亮点 (Key Features)”部分，重点突出对客户的业务价值。
        5. 文案总长度应适中，符合 {platform} 的阅读习惯。
        
        请直接输出最终的营销文案。
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', # 使用高效的 Flash 模型
            contents=prompt
        )
        
        # 提取 AI 生成的标题
        # 简化标题提取，让 AI 直接根据内容生成，这里只是一个占位符
        title = f"🚀 {platform} 重磅发布：Technical Change Log Update"
        
        return response.text, title

    except APIError as e:
        return (f"ERROR: Gemini API 调用失败。请检查您的 API Key 是否有效。错误详情: {e}", "API 错误")
    except Exception as e:
        return (f"ERROR: AI 生成过程中出现未知错误。{e}", "未知错误")


# --- 2. UI 界面布局 (双栏) ---
col_input, col_output = st.columns([0.65, 0.35]) 


with col_input:
    st.markdown('<p class="main-header">Product Update AI Generator</p>', unsafe_allow_html=True)
    st.write("将您的技术文档转化为专业的营销文案，达到 TOP 10 SaaS 公司的质量标准。")
    st.markdown("---")
    
    # --- 步骤 1：技术内容输入 ---
    st.subheader("1. 粘贴您的技术更新内容")
    tech_input = st.text_area(
        "输入您的 Jira/GitHub 日志、技术说明或 Bug 修复列表。",
        height=280,
        value="Core Feature Update: We have refactored the data processing pipeline to use a new asynchronous queue, which reduces latency for large file uploads by an average of 35% for all Enterprise tier clients. \n- Bug Fixes: Fixed a critical bug where users in the European region could not apply discount codes to subscription renewals due to a localized currency formatting error. \n- New API Endpoint: Added a new /api/v2/webhooks/status endpoint for better external monitoring and real-time event delivery tracking for partners. \n- Security Patch: Implemented multi-factor authentication (MFA) enforcement for all administrator accounts across the platform.",
        placeholder="例如: Fixed a critical bug in the payment gateway, added multi-currency support for European users, and improved API response time by 20%."
    )

    st.markdown("---")
    
    # --- 步骤 2：输出格式与语调设置 ---
    st.subheader("2. 输出格式与语调设置")
    
    # 使用 st.columns 优化设置区的布局
    col1, col2 = st.columns(2)
    
    with col1:
        # A. 目标平台
        platform = st.selectbox(
            '目标文案类型 (Target Platform)',
            ('博客文章 (Blog Post)', '电子邮件公告 (Email Announcement)', '推特/X 帖子 (Social Thread)')
        )
    
    with col2:
        # B. 目标受众与语调
        tone = st.selectbox(
            '目标语调与受众 (Tone & Audience)',
            ('专业 (Professional)', '友好 (Friendly)', '面向开发者 (Developer-Focused)', '幽默 (Witty)')
        )
    
    # C. 品牌特殊指令
    brand_notes = st.text_input(
        '品牌特殊指令 (Brand Notes) (可选)',
        placeholder="例如: 我们的核心价值是‘协作第一’"
    )

    st.markdown("---")
    
    # --- 步骤 3：一键生成 (硬编码风格样本) ---
    if st.button('✨ Generate Professional Content Now!'):
        
        # 修正：使用三引号定义多行字符串
        fixed_style_sample = """
        核心原则：文案必须积极、专业、以客户价值为中心。使用动词和数字突出效益。
        示例风格：在当今快速变化的数字环境中，您的团队需要的是一个能够简化复杂性的工具。我们重构了核心架构，现在，您可以以前所未有的速度和可靠性实现目标。
        """
        
        if not tech_input:
            st.warning("请输入技术更新内容后再点击生成按钮！") # 修正：添加引号
        else:
            with st.spinner('AI 正在基于 TOP 10 SaaS 风格生成专业文案...'):
                
                # 直接使用固定风格样本，不再进行网络抓取
                final_style_sample = fixed_style_sample

                # 3. 调用 AI 生成内容
                generated_text, generated_title = generate_content_with_ai(
                    tech_input, platform, tone, brand_notes, final_style_sample
                )
                
                # 抓取步骤已跳过，直接显示 AI 结果
                st.success("成功跳过抓取步骤，AI 正在基于预设的高质量风格生成文案！") # 修正：添加引号
                
                # 将生成的内容存储在 session_state 中，以便在右侧显示
                st.session_state['generated_content'] = generated_text
                st.session_state['generated_title'] = generated_title


# 初始化 session state，防止首次加载报错
if 'generated_content' not in st.session_state:
    st.session_state['generated_content'] = "请点击上方按钮生成内容。"
    st.session_state['generated_title'] = "AI 文案预览"


# --- 4. 右侧：输出与预览区 ---
with col_output:
    st.markdown('<p style="font-size:24px; font-weight:600;">✍️ 文案预览与微调 (Final Output)</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 显示生成的标题
    st.markdown(f"**标题：** {st.session_state['generated_title']}", unsafe_allow_html=True)
    
    # 显示生成的正文，并允许用户编辑
    final_text = st.text_area(
        "生成的文案正文 (Review & Edit)",
        value=st.session_state['generated_content'],
        height=450
    )
    
    st.markdown("---")
    
    # --- 4. 导出与复制 ---
    st.markdown('<p style="font-size:20px; font-weight:600;">一键导出</p>', unsafe_allow_html=True)
    
    # 导出按钮组
    col_copy, col_export = st.columns(2)
    
    with col_copy:
        st.button('📋 一键复制文本 (Copy Text)')
    
    with col_export:
        st.download_button(
            label="⬇️ 导出 Markdown",
            data=final_text,
            file_name=f"product_update_{platform.split(' ')[0]}.md",
            mime="text/markdown"
        )
    
    st.caption("注：右键点击文案编辑区，也可以进行复制操作。")