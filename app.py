import streamlit as st
from openai import OpenAI
import base64

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="视觉工坊 (全能双语版)", layout="wide", page_icon="💎")

# --- 2. 侧边栏：双 API Key 配置 ---
with st.sidebar:
    st.title("💎 视觉工坊")
    st.markdown("### 全功能双语输出版")
    st.info("本版本已统一所有功能输出格式：\n\n🇨🇳 **中文深度解析**\n🇺🇸 **英文绘画咒语**")
    
    st.markdown("---")
    
    # 1. DeepSeek 配置
    st.markdown("#### 🧠 文本/逻辑引擎 (DeepSeek)")
    deepseek_key = st.text_input("DeepSeek API Key", type="password", key="ds_key")
    st.caption("用于：剧本分析、分镜构思、角色设计")
    
    st.markdown("---")
    
    # 2. 通义千问 配置
    st.markdown("#### 👁️ 视觉引擎 (通义千问)")
    qwen_key = st.text_input("阿里云 DashScope Key", type="password", key="qw_key")
    st.caption("用于：图片反推解析")

# --- 3. 核心功能函数 ---

def get_deepseek_client():
    if not deepseek_key:
        return None
    return OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")

def get_qwen_client():
    if not qwen_key:
        return None
    return OpenAI(api_key=qwen_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

def image_to_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# === 功能 1: 图片反推 (Qwen-VL) ===
def qwen_vision_analysis(base64_img):
    client = get_qwen_client()
    if not client:
        return "⚠️ 请先在侧边栏配置阿里云 Key"
    
    try:
        response = client.chat.completions.create(
            model="qwen-vl-max",
            messages=[
                {
                    "role": "system",
                    "content": "你是一名资深的 AI 绘画提示词专家。"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """
                        请分析这张图片，输出标准双语报告：
                        
                        ### 🔍 中文画面解析
                        (详细描述画面主体、风格、光影、构图，约100字)
                        
                        ### 🎨 English Prompt
                        (基于分析生成的高质量 Midjourney 提示词)
                        """},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Qwen 调用失败: {e}"

# === 功能 2: 剧本转分镜 (DeepSeek) - 已强化双语格式 ===
def deepseek_script_to_storyboard(script, style):
    client = get_deepseek_client()
    if not client:
        return "⚠️ 请先在侧边栏配置 DeepSeek Key"
    
    # 强制 DeepSeek 按照 Markdown 格式输出中英对照
    prompt = f"""
    你是一个电影分镜大师。请根据用户提供的剧本，设计 3-4 个关键分镜。
    风格要求：{style}。
    
    【重要】请严格按照以下 Markdown 格式输出，不要包含其他废话：

    ### 🎬 Shot 1
    **📖 中文构思**：(详细描述画面内容、镜头角度、光影氛围)
    **🖌️ Prompt**: `/imagine prompt: (英文提示词) --ar 16:9 --v 6.0`

    ### 🎬 Shot 2
    **📖 中文构思**：...
    **🖌️ Prompt**: ...

    (以此类推)
    
    剧本内容：
    {script}
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.3 
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"DeepSeek 调用失败: {e}"

# === 功能 3: 角色三视图 (DeepSeek) - 已强化双语格式 ===
def deepseek_char_sheet(desc, style):
    client = get_deepseek_client()
    if not client:
        return "⚠️ 请先在侧边栏配置 DeepSeek Key"
    
    # 强制 DeepSeek 输出设计思路和提示词
    prompt = f"""
    我需要一个角色的三视图 Prompt。
    角色：{desc}
    风格：{style}
    
    请严格按照以下 Markdown 格式输出：
    
    ### 🧠 中文设计思路
    (用中文简要说明角色的设计要点，如服装细节、发型、配饰、配色方案等)
    
    ### 🎨 English Prompt
    ```bash
    (必须包含: three views, front view, side view, back view, full body shot, white background)
    (此处生成完整的英文提示词)
    ```
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"DeepSeek 调用失败: {e}"

# --- 4. 页面 UI 布局 ---

st.header("💎 视觉工坊 (全能双语版)")

tab1, tab2, tab3 = st.tabs(["👁️ 图片反推 (Qwen)", "🎬 剧本转分镜 (DeepSeek)", "👤 角色三视图 (DeepSeek)"])

# === Tab 1: 图片反推 ===
with tab1:
    st.subheader("图片反推：中文解析 + 英文咒语")
    uploaded_file = st.file_uploader("上传图片", type=["jpg", "png", "jpeg", "webp"])
    
    if uploaded_file and st.button("🚀 开始双语分析", key="btn1"):
        if not qwen_key:
            st.error("请先配置阿里云 Key")
        else:
            with st.spinner("通义千问正在进行双语解析..."):
                img_b64 = image_to_base64(uploaded_file)
                result = qwen_vision_analysis(img_b64)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(uploaded_file, caption="原图", use_column_width=True)
                with col2:
                    if "失败" in result:
                        st.error(result)
                    else:
                        st.success("解析完成！")
                        st.markdown(result)

# === Tab 2: 剧本转分镜 ===
with tab2:
    st.subheader("剧本 -> 分镜 (中英对照)")
    script_input = st.text_area("输入剧本片段", height=150, placeholder="例如：雨夜，杀手站在霓虹灯下的街道，手中握着一把生锈的左轮手枪...")
    style_select = st.selectbox("风格", ["赛博朋克 (Cyberpunk)", "吉卜力动漫 (Ghibli)", "好莱坞大片 (Cinematic)", "皮克斯 3D (Pixar)"])
    
    if st.button("🎬 生成分镜表", key="btn2"):
        if not deepseek_key:
            st.error("请先配置 DeepSeek Key")
        elif not script_input:
            st.warning("请输入剧本")
        else:
            with st.spinner("DeepSeek 正在构思画面 (双语模式)..."):
                res = deepseek_script_to_storyboard(script_input, style_select)
                st.markdown(res)

# === Tab 3: 角色三视图 ===
with tab3:
    st.subheader("角色三视图 (含设计思路)")
    c1, c2 = st.columns(2)
    with c1:
        char_desc = st.text_input("角色描述", "例：白发红瞳的吸血鬼少女，穿着哥特洛丽塔裙")
    with c2:
        style = st.selectbox("画风", ["二次元 (Anime)", "次世代 3D (Unreal Engine 5)", "油画 (Oil Painting)", "极简线条 (Line Art)"])
        
    if st.button("👤 生成设计方案", key="btn3"):
        if not deepseek_key:
            st.error("请先配置 DeepSeek Key")
        else:
            with st.spinner("DeepSeek 正在设计角色 (双语模式)..."):
                res = deepseek_char_sheet(char_desc, style)
                st.markdown(res)
