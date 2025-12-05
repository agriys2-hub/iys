import streamlit as st
from openai import OpenAI
import base64

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="视觉工坊 (混合双核版)", layout="wide", page_icon="🧬")

# --- 2. 侧边栏：双 API Key 配置 ---
with st.sidebar:
    st.title("🧬 混合动力引擎")
    st.info("本工具采用双模型架构：\n\n👁️ **视觉识别**：通义千问 (Qwen)\n🧠 **文本创作**：DeepSeek")
    
    st.markdown("---")
    
    # 输入 DeepSeek Key
    st.markdown("### 1. DeepSeek 配置 (用于文本)")
    deepseek_key = st.text_input("DeepSeek API Key", type="password", key="ds_key")
    st.caption("[👉 获取 DeepSeek Key](https://platform.deepseek.com/)")
    
    st.markdown("---")
    
    # 输入 通义千问 Key
    st.markdown("### 2. 通义千问 配置 (用于识图)")
    qwen_key = st.text_input("阿里云 DashScope Key", type="password", key="qw_key")
    st.caption("[👉 获取通义千问 Key](https://bailian.console.aliyun.com/?apiKey=1)")

# --- 3. 核心功能函数 ---

def get_deepseek_client():
    """获取 DeepSeek 客户端连接"""
    if not deepseek_key:
        return None
    return OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")

def get_qwen_client():
    """获取通义千问客户端连接 (兼容协议)"""
    if not qwen_key:
        return None
    return OpenAI(api_key=qwen_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

def image_to_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# === 功能 1: 图片反推 (使用 Qwen-VL-Max) ===
def qwen_vision_analysis(base64_img):
    client = get_qwen_client()
    if not client:
        return "⚠️ 请先在侧边栏配置阿里云 Key"
    
    try:
        response = client.chat.completions.create(
            model="qwen-vl-max", # 阿里最强视觉模型
            messages=[
                {
                    "role": "system",
                    "content": "你是一名资深的 AI 绘画提示词专家。"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请详细分析这张图片，生成一段高质量的 Midjourney 英文提示词。包含：Subject, Art Style, Lighting, Color Palette, Composition。直接输出 Prompt。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Qwen 调用失败: {e}"

# === 功能 2: 剧本转分镜 (使用 DeepSeek-V3) ===
def deepseek_script_to_storyboard(script, style):
    client = get_deepseek_client()
    if not client:
        return "⚠️ 请先在侧边栏配置 DeepSeek Key"
    
    prompt = f"""
    你是一个电影分镜大师。请根据用户提供的剧本，设计 3-4 个关键分镜。
    风格要求：{style}。
    
    请输出英文提示词（Prompt），格式如下：
    [Shot 1]: <画面中文简述>
    Prompt: /imagine prompt: <英文提示词> --ar 16:9 --v 6.0
    
    剧本内容：
    {script}
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.3 # 让 DeepSeek 发挥创意
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"DeepSeek 调用失败: {e}"

# === 功能 3: 角色三视图 (使用 DeepSeek-V3) ===
def deepseek_char_sheet(desc, style):
    client = get_deepseek_client()
    if not client:
        return "⚠️ 请先在侧边栏配置 DeepSeek Key"
    
    prompt = f"""
    我需要一个角色的三视图 Prompt。
    角色：{desc}
    风格：{style}
    
    请生成一段高质量的英文 Prompt，必须包含 "(three views, front view, side view, back view)" 关键词。
    只输出 Prompt 代码块。
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

st.header("🧬 视觉工坊 (DeepSeek + Qwen)")

tab1, tab2, tab3 = st.tabs(["👁️ 图片反推 (Qwen-VL)", "🎬 剧本转分镜 (DeepSeek)", "👤 角色三视图 (DeepSeek)"])

# === Tab 1: 图片反推 (调用通义千问) ===
with tab1:
    st.subheader("图片反推提示词")
    uploaded_file = st.file_uploader("上传图片", type=["jpg", "png", "jpeg"])
    
    if uploaded_file and st.button("🚀 Qwen 识别", key="btn1"):
        if not qwen_key:
            st.error("请先配置阿里云 DashScope Key")
        else:
            with st.spinner("通义千问正在观察图片..."):
                img_b64 = image_to_base64(uploaded_file)
                result = qwen_vision_analysis(img_b64)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(uploaded_file, caption="原图", use_column_width=True)
                with col2:
                    if "失败" in result:
                        st.error(result)
                    else:
                        st.success("反推成功！")
                        st.text_area("提示词结果", value=result, height=250)

# === Tab 2: 剧本转分镜 (调用 DeepSeek) ===
with tab2:
    st.subheader("剧本 -> 分镜 Prompt")
    script_input = st.text_area("输入剧本片段", height=150)
    style_select = st.selectbox("风格", ["赛博朋克", "吉卜力", "写实电影", "皮克斯 3D"])
    
    if st.button("🎬 DeepSeek 生成", key="btn2"):
        if not deepseek_key:
            st.error("请先配置 DeepSeek Key")
        elif not script_input:
            st.warning("请输入剧本")
        else:
            with st.spinner("DeepSeek 正在思考分镜..."):
                res = deepseek_script_to_storyboard(script_input, style_select)
                st.markdown(res)

# === Tab 3: 角色三视图 (调用 DeepSeek) ===
with tab3:
    st.subheader("角色三视图 Prompt")
    c1, c2 = st.columns(2)
    with c1:
        char_desc = st.text_input("角色描述", "例：白发红瞳的吸血鬼少女")
    with c2:
        style = st.selectbox("画风", ["二次元 (Anime)", "次世代 3D", "油画"])
        
    if st.button("👤 生成咒语", key="btn3"):
        if not deepseek_key:
            st.error("请先配置 DeepSeek Key")
        else:
            with st.spinner("DeepSeek 正在构建三视图..."):
                res = deepseek_char_sheet(char_desc, style)
                st.code(res, language="bash")
