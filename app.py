import streamlit as st
import base64
from openai import OpenAI
import os

# --- 1. 配置与初始化 ---
st.set_page_config(page_title="视觉工坊 AI 提示词生成器", layout="wide", page_icon="🎨")

# 侧边栏：API Key 设置
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5278/5278402.png", width=80) # 示例Logo
    st.title("视觉工坊")
    st.markdown("### 全能 AI 提示词工具")
    api_key = st.text_input("请输入 OpenAI API Key", type="password")
    
    st.info("本工具依赖 GPT-4o 模型，请确保 Key 有效。")

# 初始化 OpenAI 客户端
client = None
if api_key:
    client = OpenAI(api_key=api_key)

# --- 2. 核心功能函数 ---

def image_to_base64(uploaded_file):
    """将上传的图片转换为 Base64 格式"""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def get_image_prompt(base64_image):
    """功能 1: 图片反推提示词"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请作为一名资深的 AI 绘画专家（如 Midjourney 专家）。详细分析这张图片，反推出能生成该图的高质量英文提示词（Prompt）。请包含：主体描述、艺术风格、光影、构图、渲染引擎关键词。直接输出提示词，不要废话。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            }
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content

def script_to_storyboard(script, style):
    """功能 2: 剧本转分镜提示词"""
    system_prompt = f"""
    你是一个专业的电影分镜师。请根据用户提供的剧本片段，将其拆分为 3-5 个关键分镜画面。
    为每个分镜生成适配 {style} 风格的 Midjourney 英文提示词。
    
    输出格式要求：
    [Shot 1]: 画面描述...
    Prompt: /imagine prompt: ... --ar 16:9
    
    [Shot 2]: ...
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": script}
        ]
    )
    return response.choices[0].message.content

def char_three_view(char_desc, style):
    """功能 3: 角色三视图生成"""
    prompt_template = f"""
    (three views, concept art sheet, front view, side view, back view:1.3), full body shot of {char_desc}, 
    {style} style, neutral background, high detail, character design, 8k resolution 
    --no text, watermark, cropped --ar 3:2
    """
    return prompt_template

# --- 3. 页面 UI 布局 ---

st.header("🎨 AI 提示词综合生成工坊")

# 创建三个功能的 Tabs
tab1, tab2, tab3 = st.tabs(["🖼️ 图片反推提示词", "🎬 剧本转分镜", "👤 角色三视图"])

# === 功能 1: 图片反推 ===
with tab1:
    st.subheader("上传图片，立即反编 Prompt")
    uploaded_file = st.file_uploader("拖拽或点击上传图片 (JPG/PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file and st.button("🚀 开始反推", key="btn1"):
        if not client:
            st.error("请先在侧边栏输入 API Key")
        else:
            with st.spinner("视觉分析中..."):
                try:
                    base64_img = image_to_base64(uploaded_file)
                    # 显示图片
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(uploaded_file, caption="原图", use_column_width=True)
                    with col2:
                        prompt_result = get_image_prompt(base64_img)
                        st.success("反推成功！")
                        st.text_area("生成的提示词 (Copy 进 MJ/SD)", value=prompt_result, height=250)
                except Exception as e:
                    st.error(f"发生错误: {e}")

# === 功能 2: 剧本转分镜 ===
with tab2:
    st.subheader("输入剧本片段，生成分镜 Prompt")
    script_input = st.text_area("输入剧本/小说片段", height=150, placeholder="例：雨夜，侦探独自走在街道上，霓虹灯倒映在水坑里...")
    style_select = st.selectbox("选择画面风格", ["赛博朋克 (Cyberpunk)", "吉卜力动漫 (Ghibli)", "写实电影感 (Cinematic)", "水墨画 (Ink Wash)"])
    
    if st.button("🎬 生成分镜表", key="btn2"):
        if not client:
            st.error("请先配置 API Key")
        elif not script_input:
            st.warning("请输入剧本内容")
        else:
            with st.spinner("正在拆解剧本并构建画面..."):
                storyboard_result = script_to_storyboard(script_input, style_select)
                st.markdown(storyboard_result)

# === 功能 3: 角色三视图 ===
with tab3:
    st.subheader("角色设定 -> 三视图 Prompt")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        char_input = st.text_input("角色描述 (英文最佳)", placeholder="e.g. A futuristic female warrior with neon armor")
    with col_c2:
        art_style = st.selectbox("渲染风格", ["Anime Style (动漫)", "3D Render (C4D/Blender)", "Oil Painting (油画)", "Sketch (素描)"])
    
    if st.button("👤 生成三视图咒语", key="btn3"):
        final_prompt = char_three_view(char_input, art_style)
        st.success("三视图提示词已生成：")
        st.code(final_prompt, language="bash")
        st.caption("💡 说明：将此提示词复制到 Midjourney 或 Stable Diffusion 中即可直接生成包含正、侧、背的三视图。")
