import streamlit as st
import pandas as pd
from openai import OpenAI
import json
import base64
from io import BytesIO
from PIL import Image

# ==========================================
# 1. 页面配置与 UI 风格 (UI Configuration)
# ==========================================
st.set_page_config(
    page_title="AI Director Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 以增强 SaaS 风格质感
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1E1E1E; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #666; margin-bottom: 2rem; }
    .card {
        background-color: #F8F9FA;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 工具函数 (Helper Functions)
# ==========================================

def get_client(api_key):
    """
    初始化硅基流动客户端
    统一 Base URL: https://api.siliconflow.cn/v1
    """
    return OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")

def encode_image(image_file):
    """将上传的图片转换为 Base64 字符串"""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# ==========================================
# 3. 侧边栏配置 (Sidebar Configuration)
# ==========================================
with st.sidebar:
    st.title("🎬 AI Director Studio")
    st.caption("Powered by SiliconFlow")
    
    st.markdown("---")
    st.subheader("🔑 API 配置")
    
    # 硅基流动只需要一个 Key 就能调用所有模型
    sf_key = st.text_input("SiliconFlow API Key", type="password", help="请前往硅基流动官网获取 sk- 开头的密钥")
    
    st.markdown("---")
    st.markdown("[👉 点击注册硅基流动获取 Key](https://cloud.siliconflow.cn/)")
    st.info("💡 提示：本版本使用 DeepSeek-V3 处理文本，Qwen2-VL 处理图片。")

# ==========================================
# 4. 主界面逻辑 (Main Application Logic)
# ==========================================

# 顶部标题
st.markdown('<div class="main-header">AI Director Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">基于国产大模型 (SiliconFlow 加速版) 的智能导演工作台</div>', unsafe_allow_html=True)

# 检查 API Key
if not sf_key:
    st.warning("⚠️ 请先在左侧侧边栏输入 SiliconFlow API Key 以开始使用。")
    st.stop()

# 初始化统一的客户端
client = get_client(sf_key)

# 模块选择
module = st.radio(
    "选择功能模块:",
    ["👁️ 视觉基因解码器", "🎥 AI 导演控制台", "🎨 IP 一致性实验室"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("---")

# -----------------------------------------------------------------------------
# 模块一：视觉基因解码器 (Visual Gene Decoder)
# 模型：Qwen/Qwen2-VL-72B-Instruct
# -----------------------------------------------------------------------------
if "视觉基因解码器" in module:
    st.subheader("👁️ 视觉基因解码器 (Visual Gene Decoder)")
    st.caption("上传参考图，提取风格基因，生成可复刻的提示词。")

    col1, col2 = st.columns([1, 2])
    
    with col1:
        uploaded_file = st.file_uploader("上传参考图片", type=['png', 'jpg', 'jpeg', 'webp'])
        if uploaded_file:
            st.image(uploaded_file, caption="参考图预览", use_container_width=True)

    with col2:
        if uploaded_file and st.button("开始解码基因", type="primary"):
            base64_image = encode_image(uploaded_file)
            
            with st.spinner("Qwen2-VL 正在分析光影与风格..."):
                try:
                    # 系统提示词
                    system_prompt = """
                    你是一个专业的视觉艺术导演。请分析这张图片。
                    请严格返回 JSON 格式，不包含 markdown 格式标记（如 ```json），直接返回纯 JSON 字符串。
                    包含以下字段：
                    - style_tags (list): 风格标签（如 Cyberpunk, Minimalist）
                    - lighting_analysis (string): 光影分析
                    - prompt_en (string): 针对 Midjourney/SDXL 优化的英文提示词
                    - prompt_cn (string): 针对可灵/混元优化的中文描述
                    """
                    
                    response = client.chat.completions.create(
                        model="Qwen/Qwen2-VL-72B-Instruct",  # 硅基流动支持的视觉模型
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": system_prompt},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]
                            }
                        ],
                        max_tokens=1024
                    )
                    
                    # 清洗 JSON (以防万一模型输出了 markdown)
                    content = response.choices[0].message.content
                    content = content.replace("```json", "").replace("```", "").strip()
                    
                    data = json.loads(content)
                    
                    # 结果展示
                    st.success("解码成功！")
                    
                    st.markdown(f"""
                    <div class="card">
                        <h4>🏷️ 风格基因</h4>
                        <p>{", ".join([f"`{tag}`" for tag in data.get('style_tags', [])])}</p>
                        <p><b>💡 光影分析:</b> {data.get('lighting_analysis')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    tab_en, tab_cn = st.tabs(["🇺🇸 Midjourney/SDXL", "🇨🇳 可灵/混元"])
                    with tab_en:
                        st.code(data.get('prompt_en'), language="text")
                    with tab_cn:
                        st.code(data.get('prompt_cn'), language="text")
                        
                except Exception as e:
                    st.error(f"解析失败: {e}")
                    st.error("如果是 JSON 解析错误，请重试，这是大模型输出格式的偶发问题。")

# -----------------------------------------------------------------------------
# 模块二：AI 导演控制台 (Director Console)
# 模型：deepseek-ai/DeepSeek-V3
# -----------------------------------------------------------------------------
elif "AI 导演控制台" in module:
    st.subheader("🎥 AI 导演控制台 (Director Console)")
    st.caption("将小说/剧本批量转换为包含专业运镜的分镜提示词表格。")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        script_text = st.text_area("输入剧情/剧本片段", height=200, placeholder="例如：主角站在雨中，手中握着一把破碎的伞，眼神充满了绝望...")
    with c2:
        style_anchor = st.text_input("风格锚点 (Style Anchor)", placeholder="例如：王家卫风格，霓虹灯，高对比度，胶片质感")
        st.info("DeepSeek-V3 将自动进行情感分析并匹配运镜（如悲伤→慢推）。")
    
    if st.button("生成分镜表", type="primary"):
        if not script_text:
            st.warning("请输入剧本内容。")
        else:
            with st.spinner("DeepSeek 正在拆解剧本并设计运镜..."):
                try:
                    system_prompt = f"""
                    Role: Professional Film Director.
                    Task: Convert the script into a shot list JSON.
                    Global Style: {style_anchor if style_anchor else "Cinematic, Realistic"}
                    
                    Rules:
                    1. Analyze emotion: If sad -> slow camera; Happy -> fast/dynamic.
                    2. Use standard camera terms: ECU (Extreme Close Up), WS (Wide Shot), Dolly In, Pan, Tilt.
                    3. Output specific JSON structure:
                    {{
                        "shots": [
                            {{
                                "id": 1,
                                "action": "Brief description of action",
                                "camera_movement": "Technical camera term",
                                "lighting_atmosphere": "Lighting desc",
                                "midjourney_prompt": "Full English prompt including style, camera, and subject"
                            }}
                        ]
                    }}
                    """
                    
                    response = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-V3", # 硅基流动的 V3 模型 ID
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": script_text}
                        ],
                        response_format={'type': 'json_object'}
                    )
                    
                    content = response.choices[0].message.content
                    data = json.loads(content)
                    df = pd.DataFrame(data['shots'])
                    
                    st.session_state['director_df'] = df
                    
                except Exception as e:
                    st.error(f"生成失败: {e}")

    if 'director_df' in st.session_state:
        st.markdown("### 🎬 分镜结果预览")
        edited_df = st.data_editor(
            st.session_state['director_df'],
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "midjourney_prompt": st.column_config.TextColumn("AI 提示词", width="large"),
                "camera_movement": "运镜",
                "action": "画面内容"
            }
        )
        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 下载 CSV 分镜表", data=csv, file_name='director_shot_list.csv', mime='text/csv')

# -----------------------------------------------------------------------------
# 模块三：IP 一致性实验室 (IP Consistency Lab)
# 模型：deepseek-ai/DeepSeek-V3
# -----------------------------------------------------------------------------
elif "IP 一致性实验室" in module:
    st.subheader("🎨 IP 一致性实验室 (IP Consistency Lab)")
    st.caption("确立角色形象，生成三视图以确保视频中的角色一致性。")
    
    col1, col2 = st.columns(2)
    with col1:
        char_desc = st.text_area("角色描述", placeholder="例如：一个20岁的赛博朋克女性黑客，银色短发...")
    with col2:
        style_tags = st.multiselect(
            "风格选择",
            ["Pixar (皮克斯)", "Anime (日漫)", "Realistic (写实)", "Cyberpunk (赛博朋克)"],
            default=["Realistic (写实)"]
        )
    
    if st.button("生成三视图 Prompt", type="primary"):
        if not char_desc:
            st.warning("请描述角色特征。")
        else:
            with st.spinner("DeepSeek 正在构建角色一致性数据..."):
                try:
                    styles = ", ".join(style_tags)
                    system_prompt = f"""
                    Role: Character Designer.
                    Task: Create a consistent 3-view reference sheet prompt based on user description.
                    Style: {styles}
                    
                    Output JSON with keys:
                    - character_analysis: Brief analysis of features.
                    - prompt_3_view: A single complex prompt requesting "Front view, Side view, Back view" in one image (Character Sheet).
                    - prompt_dynamic: A prompt showing the character in an action pose.
                    """
                    
                    response = client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-V3",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": char_desc}
                        ],
                        response_format={'type': 'json_object'}
                    )
                    
                    data = json.loads(response.choices[0].message.content)
                    
                    st.success("构建完成！")
                    
                    st.markdown(f"""
                    <div class="card">
                        <h4>🧠 角色深度分析</h4>
                        <p>{data.get('character_analysis')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("#### 📐 三视图提示词 (Character Sheet)")
                    st.code(data.get('prompt_3_view'), language="text")
                    
                    st.markdown("#### ⚡ 动态场景提示词 (Action Shot)")
                    st.code(data.get('prompt_dynamic'), language="text")
                    
                except Exception as e:
                    st.error(f"生成失败: {e}")
