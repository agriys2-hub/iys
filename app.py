import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 1. 配置与初始化 ---
st.set_page_config(page_title="视觉工坊 (Gemini 3.0版)", layout="wide", page_icon="⚡")

# 侧边栏：API Key 设置
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg", width=80) 
    st.title("视觉工坊 Pro")
    st.markdown("### Powered by Gemini 3.0")
    
    # 获取 API Key
    api_key = st.text_input("请输入 Google Gemini API Key", type="password")
    st.markdown("[👉 点击这里管理 Key (Google AI Studio)](https://aistudio.google.com/app/apikey)")
    
    st.warning("⚠️ 注意：Gemini 3.0 Pro 是高性能模型，请留意您的 API 用量配额。")

# 初始化 Gemini
model = None
if api_key:
    try:
        genai.configure(api_key=api_key)
        # 🚀 核心修改：使用最新的 Gemini 3.0 Pro 模型
        # 如果你的账号还没获得 3.0 权限，可以尝试回退到 'gemini-2.0-flash' 或 'gemini-1.5-pro'
        model = genai.GenerativeModel('gemini-3.0-pro') 
    except Exception as e:
        st.error(f"API Key 配置或模型连接出错: {e}")

# --- 2. 核心功能函数 ---

def get_image_prompt(image_file):
    """功能 1: 图片反推提示词"""
    img = Image.open(image_file)
    
    prompt = """
    你是一名资深的 AI 绘画专家（Midjourney Expert）。
    请详细分析这张图片，反推出能生成该图的高质量英文提示词（Prompt）。
    请包含：主体描述 (Subject)、艺术风格 (Art Style)、光影 (Lighting)、构图 (Composition)、渲染关键词 (Rendering)。
    请发挥 Gemini 3.0 强大的视觉理解能力，捕捉画面中微小的细节和情感氛围。
    直接输出提示词，不需要任何开场白。
    """
    
    # Gemini 3.0 对图片细节的理解力有显著提升
    response = model.generate_content([prompt, img])
    return response.text

def script_to_storyboard(script, style):
    """功能 2: 剧本转分镜提示词"""
    prompt = f"""
    你是一个专业的电影分镜师。请根据以下剧本片段，将其拆分为 3-5 个关键分镜画面。
    为每个分镜生成适配 {style} 风格的 Midjourney 英文提示词。
    
    输出格式要求：
    [Shot 1]: 画面中文描述...
    Prompt: /imagine prompt: ... --ar 16:9
    
    [Shot 2]: ...
    
    剧本内容：
    {script}
    """
    response = model.generate_content(prompt)
    return response.text

def char_three_view(char_desc, style):
    """功能 3: 角色三视图生成"""
    prompt = f"""
    我需要生成一个角色的三视图（Character Sheet），用于 3D 建模或 AI 绘画。
    角色描述：{char_desc}
    风格：{style}
    
    请帮我编写一个高质量的 Stable Diffusion/Midjourney 提示词。
    结构必须包含：
    "(three views, concept art sheet, front view, side view, back view), full body shot..."
    以及风格词和负面提示词。
    只输出英文提示词。
    """
    response = model.generate_content(prompt)
    return response.text

# --- 3. 页面 UI 布局 ---

st.header("⚡ 视觉工坊 (基于 Gemini 3.0 Pro)")

# 创建三个功能的 Tabs
tab1, tab2, tab3 = st.tabs(["🖼️ 图片反推提示词", "🎬 剧本转分镜", "👤 角色三视图"])

# === 功能 1: 图片反推 ===
with tab1:
    st.subheader("上传图片，Gemini 3.0 深度解析")
    uploaded_file = st.file_uploader("拖拽或点击上传图片 (JPG/PNG)", type=["jpg", "png", "jpeg", "webp"])
    
    if uploaded_file and st.button("🚀 开始反推", key="btn1"):
        if not model:
            st.error("请先在侧边栏输入 API Key")
        else:
            with st.spinner("Gemini 3.0 正在进行像素级分析..."):
                try:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(uploaded_file, caption="原图", use_column_width=True)
                    with col2:
                        prompt_result = get_image_prompt(uploaded_file)
                        st.success("反推成功！")
                        st.text_area("生成的提示词 (Copy 进 MJ/SD)", value=prompt_result, height=250)
                except Exception as e:
                    st.error(f"发生错误: {e}\n\n可能是您的 API Key 尚未开通 Gemini 3.0 权限，建议尝试更换为 gemini-1.5-pro。")

# === 功能 2: 剧本转分镜 ===
with tab2:
    st.subheader("输入剧本片段，生成分镜 Prompt")
    script_input = st.text_area("输入剧本/小说片段", height=150, placeholder="例：雨夜，侦探独自走在街道上，霓虹灯倒映在水坑里...")
    style_select = st.selectbox("选择画面风格", ["赛博朋克 (Cyberpunk)", "吉卜力动漫 (Ghibli)", "写实电影感 (Cinematic)", "中国水墨 (Ink Wash)"])
    
    if st.button("🎬 生成分镜表", key="btn2"):
        if not model:
            st.error("请先配置 API Key")
        elif not script_input:
            st.warning("请输入剧本内容")
        else:
            with st.spinner("Gemini 3.0 正在构思分镜..."):
                try:
                    storyboard_result = script_to_storyboard(script_input, style_select)
                    st.markdown(storyboard_result)
                except Exception as e:
                    st.error(f"发生错误: {e}")

# === 功能 3: 角色三视图 ===
with tab3:
    st.subheader("角色设定 -> 三视图 Prompt")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        char_input = st.text_input("角色描述", placeholder="例：一个穿着霓虹盔甲的未来女战士")
    with col_c2:
        art_style = st.selectbox("渲染风格", ["Anime Style (动漫)", "3D Render (C4D/Blender)", "Oil Painting (油画)", "Sketch (素描)"])
    
    if st.button("👤 生成三视图咒语", key="btn3"):
        if not model:
             st.error("请先配置 API Key")
        else:
            with st.spinner("正在生成三视图提示词..."):
                try:
                    final_prompt = char_three_view(char_input, art_style)
                    st.success("三视图提示词已生成：")
                    st.code(final_prompt, language="bash")
                except Exception as e:
                    st.error(f"发生错误: {e}")
