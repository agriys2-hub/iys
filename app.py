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

def get_deepseek_client(api_key):
    """初始化 DeepSeek 客户端 (逻辑大脑)"""
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def get_qwen_client(api_key):
    """初始化通义千问客户端 (视觉之眼)"""
    return OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

def encode_image(image_file):
    """将上传的图片转换为 Base64 字符串"""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# ==========================================
# 3. 侧边栏配置 (Sidebar Configuration)
# ==========================================
with st.sidebar:
    st.title("🎬 AI Director Studio")
    st.caption("v1.0 MVP | AI 视频前期筹备全栈工具")
    
    st.markdown("---")
    st.subheader("🔑 API 配置")
    
    ds_key = st.text_input("DeepSeek API Key", type="password", help="用于处理文本逻辑")
    qw_key = st.text_input("Dashscope (通义) API Key", type="password", help="用于视觉理解")
    
    st.markdown("---")
    st.info("💡 提示：所有数据仅在当前会话有效，刷新页面将重置。")

# ==========================================
# 4. 主界面逻辑 (Main Application Logic)
# ==========================================

# 顶部标题
st.markdown('<div class="main-header">AI Director Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">基于国产大模型的智能导演工作台：从灵感到分镜，一站式生成。</div>', unsafe_allow_html=True)

# 检查 API Key
if not ds_key or not qw_key:
    st.warning("⚠️ 请先在左侧侧边栏输入 DeepSeek 和 Dashscope 的 API Key 以开始使用。")
    st.stop()

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
            client = get_qwen_client(qw_key)
            base64_image = encode_image(uploaded_file)
            
            with st.spinner("Qwen-VL 正在分析光影与风格..."):
                try:
                    # 系统提示词：图生文策略
                    system_prompt = """
                    你是一个专业的视觉艺术导演。请分析这张图片。
                    请严格返回 JSON 格式，包含以下字段：
                    - style_tags (list): 风格标签（如 Cyberpunk, Minimalist）
                    - lighting_analysis (string): 光影分析
                    - prompt_en (string): 针对 Midjourney/SDXL 优化的英文提示词
                    - prompt_cn (string): 针对可灵/混元优化的中文描述
                    """
                    
                    response = client.chat.completions.create(
                        model="qwen-vl-max",
                        messages=[
                            {
                                "role": "system",
                                "content": [{"type": "text", "text": system_prompt}]
                            },
                            {
                                "role": "user",
                                "content": [
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]
                            }
                        ],
                    )
                    
                    # 简单清洗 JSON (防止 markdown 符号)
                    content = response.choices[0].message.content.replace("```json", "").replace("```", "")
                    data = json.loads(content)
                    
                    # 结果展示
                    st.success("解码成功！")
                    
                    # 风格标签卡片
                    st.markdown(f"""
                    <div class="card">
                        <h4>🏷️ 风格基因</h4>
                        <p>{", ".join([f"`{tag}`" for tag in data.get('style_tags', [])])}</p>
                        <p><b>💡 光影分析:</b> {data.get('lighting_analysis')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 提示词展示
                    tab_en, tab_cn = st.tabs(["🇺🇸 Midjourney/SDXL", "🇨🇳 可灵/混元"])
                    with tab_en:
                        st.code(data.get('prompt_en'), language="text")
                    with tab_cn:
                        st.code(data.get('prompt_cn'), language="text")
                        
                except Exception as e:
                    st.error(f"解析失败: {e}")

# -----------------------------------------------------------------------------
# 模块二：AI 导演控制台 (Director Console)
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
            client = get_deepseek_client(ds_key)
            with st.spinner("DeepSeek 正在拆解剧本并设计运镜..."):
                try:
                    # 系统提示词：剧本转分镜策略
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
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": script_text}
                        ],
                        response_format={'type': 'json_object'}
                    )
                    
                    content = response.choices[0].message.content
                    data = json.loads(content)
                    df = pd.DataFrame(data['shots'])
                    
                    # 存入 Session State 防止重载丢失
                    st.session_state['director_df'] = df
                    
                except Exception as e:
                    st.error(f"生成失败: {e}")

    # 结果展示区
    if 'director_df' in st.session_state:
        st.markdown("### 🎬 分镜结果预览")
        
        # 可编辑表格
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
        
        # CSV 下载
        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 下载 CSV 分镜表",
            data=csv,
            file_name='director_shot_list.csv',
            mime='text/csv',
        )

# -----------------------------------------------------------------------------
# 模块三：IP 一致性实验室 (IP Consistency Lab)
# -----------------------------------------------------------------------------
elif "IP 一致性实验室" in module:
    st.subheader("🎨 IP 一致性实验室 (IP Consistency Lab)")
    st.caption("确立角色形象，生成三视图以确保视频中的角色一致性。")
    
    col1, col2 = st.columns(2)
    with col1:
        char_desc = st.text_area("角色描述", placeholder="例如：一个20岁的赛博朋克女性黑客，银色短发，戴着发光的护目镜，身穿黑色皮夹克...")
    with col2:
        style_tags = st.multiselect(
            "风格选择",
            ["Pixar (皮克斯)", "Anime (日漫)", "Realistic (写实)", "Cyberpunk (赛博朋克)", "Oil Painting (油画)"],
            default=["Realistic (写实)"]
        )
    
    if st.button("生成三视图 Prompt", type="primary"):
        if not char_desc:
            st.warning("请描述角色特征。")
        else:
            client = get_deepseek_client(ds_key)
            with st.spinner("DeepSeek 正在构建角色一致性数据..."):
                try:
                    styles = ", ".join(style_tags)
                    # 系统提示词：一致性策略
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
                        model="deepseek-chat",
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
