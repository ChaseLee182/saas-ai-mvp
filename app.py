import streamlit as st
import os
# 导入 os 用于获取 GEMINI_API_KEY
import requests
from bs4 import BeautifulSoup
# 导入 Google GenAI 库，确保您已在 requirements.txt 中添加 google-genai
from google import genai 
from google.genai.errors import APIError

# --- 配置页面和样式 ---
# 设置页面布局为宽屏，并定义一个标题
st.set_page_config(layout="wide", page_title="B2B Content AI Generator MVP")

# 使用 CSS 注入来调整布局和样式，使其看起来更专业
st.markdown("""
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
# 1. 核心功能：数据抓取（抓取 TechCrunch 科技博客的文案风格）
# ---------------------------------------------------------

# 目标 URL：TechCrunch 的通用科技新闻页 (更稳定，结构更清晰)
TECHCRUNCH_URL = "https://techcrunch.com/category/startups/" 

def fetch_style_content(url):
    """
    抓取目标 URL 的内容，用于提取文案风格（针对 TechCrunch 博客列表页）。
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 寻找文章摘要或简介的元素。针对 TechCrunch
        # 寻找文章列表中的摘要/描述文本
        summaries = soup.find_all('div', class_='post-description', limit=5)
        
        style_text = ""
        if summaries:
            # 拼接抓取到的所有摘要文本
            for summary in summaries:
                # 提取摘要文本，并清理空行
                style_text += summary.get_text(strip=True) + " "
            
            if len(style_text) > 200:
                # 返回清理后的文本
                return style_text.strip()
            
            return "ERROR: 无法从 TechCrunch 列表页元素中提取足够的文案风格文本（内容太少）。"
        
        return "ERROR: 无法找到 TechCrunch 文章摘要或简介元素。"
        
    except requests.exceptions.RequestException as e:
        return f"ERROR: 数据抓取失败（网络/URL错误）。{e}"
    except Exception as e:
        return f"ERROR: 网页解析失败。{e}"

# ---------------------------------------------------------
# 2. 核心功能：AI 内容生成（调用 Gemini API）
# 此函数替换了您原文件中的 generate_content_mock 函数
# ---------------------------------------------------------

def generate_content_with_ai(tech_input, platform, tone, brand_notes, style_sample):
    """
    调用 Gemini API，根据用户输入和抓取到的风格数据生成营销文案。
    """
    # 检查 API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ("ERROR: 无法找到 GEMINI_API_KEY。请在 Streamlit Cloud Secrets 中进行设置。", "API Key 缺失")

    try:
        client = genai.Client(api_key=api_key)
        
        # 构造详细的提示词 (Prompt Engineering)
        prompt = f"""
        你是一位顶级 SaaS 公司的专业内容营销专家。你的任务是将原始技术更新内容转化为高质量的营销文案。
        
        **关键指令：** 请严格模仿以下提供的“目标公司文案样本”的语言、语调、结构和专业度。
        
        --- 目标公司文案样本 (TechCrunch 风格) ---
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
        4. **结构化输出**: 必须包含清晰的“核心价值 (Value Proposition)”和“关键亮点 (Key Features)”部分，重点突出对客户的业务价值。
        5. 文案总长度应适中，符合 {platform} 的阅读习惯。

        请直接输出最终的营销文案。
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash', # 使用高效的 Flash 模型
            contents=prompt
        )
        
        # 提取AI生成的标题 (这里简化为从用户输入中提取)
        title = f"🚀 {platform} 重磅发布：{tech_input.split('.')[0].strip()}!"
        
        return response.text, title

    except APIError as e:
        return (f"ERROR: Gemini API 调用失败。请检查您的 API Key 是否有效。错误详情: {e}", "API 错误")
    except Exception as e:
        return (f"ERROR: AI 生成过程中出现未知错误。{e}", "未知错误")


# --- 3. UI 界面布局 (双栏) ---
col_input, col_output = st.columns([0.65, 0.35]) 


with col_input:
    st.markdown('<p class="main-header">Product Update AI Generator</p >', unsafe_allow_html=True)
    st.write("将您的技术文档转化为专业的营销文案，达到 TOP 10 SaaS 公司的质量标准。")
    st.markdown("---")
    
    # --- 步骤 1：技术内容输入 ---
    st.subheader("1. 粘贴您的技术更新内容")
    tech_input = st.text_area(
        "输入您的 TechCrunch/GitHub 日志、技术说明或 Bug 修复列表。",
        height=280,
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
    
    # --- 步骤 3：一键生成 ---
    if st.button('✨ Generate Professional Content Now!'):
        if not tech_input:
            st.warning("请输入技术更新内容后再点击生成按钮！")
        else:
            with st.spinner('正在抓取 TOP 10 SaaS 范例数据 (TechCrunch) 并调用 AI 生成内容...'):
                
                # 1. 抓取 TECHCRUNCH 文案风格
                style_sample = fetch_style_content(TECHCRUNCH_URL)
                
                # 2. 处理抓取结果
                if style_sample.startswith("ERROR"):
                    # 如果抓取失败，显示错误并使用通用风格作为后备
                    st.error(style_sample)
                    final_style_sample = "抓取失败，请使用通用顶级 SaaS 风格。"
                else:
                    st.success("TechCrunch 文案风格样本抓取成功！")
                    final_style_sample = style_sample

                # 3. 调用 AI 生成内容
                generated_text, generated_title = generate_content_with_ai(
                    tech_input, platform, tone, brand_notes, final_style_sample
                )
                
                # 将生成的内容存储在 session_state 中，以便在右侧显示
                st.session_state['generated_content'] = generated_text
                st.session_state['generated_title'] = generated_title
    
    # 初始化 session state，防止首次加载报错
    if 'generated_content' not in st.session_state:
        st.session_state['generated_content'] = "请点击上方按钮生成内容。"
        st.session_state['generated_title'] = "AI 文案预览"


# --- 4. 右侧：输出与预览区 ---
with col_output:
    st.markdown('<p style="font-size:24px; font-weight:600;"✍️ 文案预览与微调 (Final Output)</p >', unsafe_allow_html=True)
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
    
    # --- 步骤 4：导出与复制 ---
    st.markdown('<p style="font-size:20px; font-weight:600;">一键导出</p >', unsafe_allow_html=True)
    
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