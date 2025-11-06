import streamlit as st

# --- 配置页面和样式 ---
# 设置页面布局为宽屏，并定义一个标题
st.set_page_config(layout="wide", page_title="B2B Content AI Generator MVP")

# 使用 CSS 注入来调整布局和样式，使其看起来更专业（可选，但推荐）
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


# --- 核心功能：模拟内容生成函数 ---
def generate_content_mock(tech_input, platform, tone, brand_notes):
    """
    此函数模拟调用您的 AI 模型 (Gemini API)。
    在真正的项目中，您将在这里编写 API 调用和提示词工程代码。
    """
    if not tech_input:
        return ("👋 请在左侧输入您的技术更新内容，我们将为您生成专业的营销文案。", "欢迎使用！")

    # 1. 模拟AI提炼核心点 (这是您数据清洗/提炼的第一步)
    core_points = tech_input.split('.')
    
    # 2. 模拟AI生成标题 (基于TOP 10的专业模式)
    title = f"🚀 {platform} 重磅发布：{core_points[0].strip()} — 让您的团队工作效率提升 30%!"

    # 3. 模拟AI生成结构化文案
    content = f"""
### 核心价值 (Value Proposition)
我们很高兴地宣布，新的 {platform} 版本已正式发布。本次更新主要聚焦于提升您的 **{tone}** 工作流效率，解决了一直以来困扰用户的核心痛点。
**您的 {brand_notes if brand_notes else "业务核心"}** 将因此次更新而显著受益。

---
### 关键亮点 (Key Features)

以下是本次更新带来的三大核心优势：

1.  **{core_points[0].strip()}**：我们重构了底层架构，使得 **{core_points[0].strip().split()[0]}** 的性能提升了 30%。
2.  **{core_points[1].strip() if len(core_points) > 1 else '全新数据处理管道'}**：增强了数据同步的可靠性，保障企业级数据流的零停机。
3.  **{core_points[2].strip() if len(core_points) > 2 else '安全合规强化'}**：全面升级了加密协议，完全满足最新的国际安全标准。

### 为什么这对您的业务至关重要 (Why It Matters)
借助本次增强，您的团队现在可以以前所未有的速度和准确性完成任务。这不仅是性能的飞跃，更是我们对 **{brand_notes if brand_notes else "提供卓越 SaaS 体验"}** 承诺的体现。

**👉 立即体验：** 登录您的账户，感受全新的 {platform} 吧！
"""
    return content, title

# --- 4. UI 界面布局 (双栏) ---
# 定义双栏布局，左侧占 65% 用于输入和控制，右侧占 35% 用于预览
col_input, col_output = st.columns([0.65, 0.35]) 


with col_input:
    st.markdown('<p class="main-header">Product Update AI Generator</p >', unsafe_allow_html=True)
    st.write("将您的技术文档转化为专业的营销文案，达到 TOP 10 SaaS 公司的质量标准。")
    st.markdown("---")
    
    # --- 步骤 1：技术内容输入 ---
    st.subheader("1. 粘贴您的技术更新内容")
    tech_input = st.text_area(
        "输入您的 Jira/GitHub 日志、技术说明或 Bug 修复列表。",
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
        # 按钮按下后，调用内容生成函数
        with st.spinner('AI 正在基于 TOP 10 SaaS 模式生成专业文案...'):
            generated_text, generated_title = generate_content_mock(tech_input, platform, tone, brand_notes)
        # 将生成的内容存储在 session_state 中，以便在右侧显示
        st.session_state['generated_content'] = generated_text
        st.session_state['generated_title'] = generated_title
    
    # 初始化 session state，防止首次加载报错
    if 'generated_content' not in st.session_state:
        st.session_state['generated_content'] = "请点击上方按钮生成内容。"
        st.session_state['generated_title'] = "AI 文案预览"


# --- 5. 右侧：输出与预览区 ---
with col_output:
    st.markdown('<p style="font-size:24px; font-weight:600;">✍️ 文案预览与微调 (Final Output)</p >', unsafe_allow_html=True)
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