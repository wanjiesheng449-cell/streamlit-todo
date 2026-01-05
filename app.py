import streamlit as st
import json
import os

# ---------------------------------------------------------
# 持久化存储配置
# ---------------------------------------------------------
TASKS_FILE = "tasks.json"

def load_tasks():
    """从本地 JSON 文件读取任务"""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        # 如果文件损坏，给一个空列表并记录错误（这里简单处理为清空）
        return []

def save_tasks(tasks):
    """将任务保存到本地 JSON 文件"""
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"保存失败: {e}")

# ---------------------------------------------------------
# Streamlit 界面
# ---------------------------------------------------------
st.set_page_config(page_title="极简代办清单", page_icon="📝")

st.title("📝 我的极简代办清单")
st.markdown("---")

# 1. 初始化任务数据 (首次加载从 JSON 读取)
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

# 2. 侧边栏：添加新任务
with st.sidebar:
    st.header("➕ 添加新任务")
    new_task_name = st.text_input("请输入任务内容", key="new_task_input")
    if st.button("添加任务", use_container_width=True):
        if new_task_name.strip():
            st.session_state.tasks.append({"name": new_task_name.strip(), "done": False})
            save_tasks(st.session_state.tasks) # 保存到文件
            st.rerun()
        else:
            st.warning("任务内容不能为空哦！")

    st.markdown("---")
    if st.button("🧪 清空所有任务", type="secondary", use_container_width=True):
        st.session_state.tasks = []
        save_tasks(st.session_state.tasks) # 保存到文件
        st.rerun()

# 3. 主界面：展示任务列表
if not st.session_state.tasks:
    st.info("目前没有任务，去侧边栏加一个吧！")
else:
    # 修复：遍历副本以防在循环中修改原列表导致索引错乱
    for index, task in enumerate(list(st.session_state.tasks)):
        col1, col2, col3 = st.columns([1, 6, 1])
        
        with col1:
            is_done = st.checkbox("", value=task["done"], key=f"check_{index}")
            if is_done != task["done"]:
                st.session_state.tasks[index]["done"] = is_done
                save_tasks(st.session_state.tasks) # 保存状态
                st.rerun()

        with col2:
            if task["done"]:
                st.markdown(f"~~{task['name']}~~")
            else:
                st.markdown(task["name"])

        with col3:
            if st.button("🗑️", key=f"del_{index}"):
                st.session_state.tasks.pop(index)
                save_tasks(st.session_state.tasks) # 保存结果
                st.rerun()

# 4. 页脚提示
st.markdown("---")
st.caption("由 Streamlit 驱动 • 支持 JSON 本地持久化存储")
