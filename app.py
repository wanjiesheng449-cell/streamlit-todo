import streamlit as st
import json
import os
import uuid
from datetime import datetime

# ---------------------------------------------------------
# 持久化存储配置
# ---------------------------------------------------------
TASKS_FILE = "tasks.json"

def save_tasks(tasks):
    """保存任务到本地 JSON (原子写入)"""
    tmp_file = f"{TASKS_FILE}.tmp"
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=4)
        os.replace(tmp_file, TASKS_FILE)
    except Exception as e:
        st.error(f"保存失败: {e}")

def load_tasks():
    """读取任务 + 数据迁移 + 异常防呆"""
    if not os.path.exists(TASKS_FILE):
        return []
    
    tasks = []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            content = json.load(f)
            # 防呆：确保是列表
            if isinstance(content, list):
                tasks = content
            else:
                st.warning("数据格式错误，已重置为空列表")
                return []
    except (json.JSONDecodeError, Exception):
        st.warning("数据文件损坏，已重置")
        return []

    # 数据迁移与清洗
    migrated = False
    valid_tasks = []
    
    for task in tasks:
        # 防呆：过滤非字典项
        if not isinstance(task, dict):
            migrated = True # 标记需要重写文件以清除脏数据
            continue
            
        if "id" not in task:
            task["id"] = uuid.uuid4().hex
            migrated = True
        if "created_at" not in task:
            task["created_at"] = datetime.now().isoformat()
            migrated = True
        valid_tasks.append(task)
    
    if migrated:
        save_tasks(valid_tasks)
    
    return valid_tasks

# ---------------------------------------------------------
# 核心逻辑
# ---------------------------------------------------------
def get_task_by_id(task_id):
    """通过 ID 获取任务对象（引用）"""
    for task in st.session_state.tasks:
        if task["id"] == task_id:
            return task
    return None

def set_task_done(task_id, done_value):
    """设置任务完成状态"""
    task = get_task_by_id(task_id)
    if task:
        task["done"] = done_value
        save_tasks(st.session_state.tasks)

def delete_task(task_id):
    """删除任务"""
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]
    save_tasks(st.session_state.tasks)

# ---------------------------------------------------------
# Streamlit 界面
# ---------------------------------------------------------
st.set_page_config(page_title="极简代办清单", page_icon="📝")

st.title("📝 我的极简代办清单")

# 1. 初始化
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

# 2. 侧边栏：操作
with st.sidebar:
    st.header("➕ 添加新任务")
    new_task_name = st.text_input("任务内容", key="new_task_input")
    
    if st.button("添加", use_container_width=True):
        if new_task_name.strip():
            new_task = {
                "id": uuid.uuid4().hex,
                "name": new_task_name.strip(),
                "done": False,
                "created_at": datetime.now().isoformat()
            }
            st.session_state.tasks.append(new_task)
            save_tasks(st.session_state.tasks)
            st.rerun()
        else:
            st.warning("内容不能为空")

    st.markdown("---")
    st.header("🔧 批量操作")
    
    col_batch1, col_batch2 = st.columns(2)
    with col_batch1:
        if st.button("全标记完成", use_container_width=True):
            for t in st.session_state.tasks: t["done"] = True
            save_tasks(st.session_state.tasks)
            st.rerun()
    with col_batch2:
        if st.button("全重置未办", use_container_width=True):
            for t in st.session_state.tasks: t["done"] = False
            save_tasks(st.session_state.tasks)
            st.rerun()

    if st.button("✨ 清空已完成", use_container_width=True):
        st.session_state.tasks = [t for t in st.session_state.tasks if not t["done"]]
        save_tasks(st.session_state.tasks)
        st.rerun()

# 3. 主界面顶部：搜索/筛选/排序
st.markdown("---")
col_s1, col_s2, col_s3 = st.columns([2, 1, 1])

with col_s1:
    search_query = st.text_input("🔍 搜索任务", "", placeholder="输入关键词...")

with col_s2:
    filter_option = st.selectbox("筛选", ["全部", "未完成", "已完成"], label_visibility="collapsed")

with col_s3:
    sort_option = st.selectbox("排序", ["默认(未完成优先)", "最新创建", "最早创建"], label_visibility="collapsed")

# 4. 数据处理 pipeline
display_tasks = st.session_state.tasks[:]

# 4.1 搜索过滤
if search_query:
    display_tasks = [t for t in display_tasks if search_query.lower() in t["name"].lower()]

# 4.2 状态筛选
if filter_option == "未完成":
    display_tasks = [t for t in display_tasks if not t["done"]]
elif filter_option == "已完成":
    display_tasks = [t for t in display_tasks if t["done"]]

# 4.3 排序逻辑
if sort_option == "默认(未完成优先)":
    # 稳定排序：先按时间倒序(新在前)，再按状态(未完成在前)
    display_tasks.sort(key=lambda x: x["created_at"], reverse=True)
    display_tasks.sort(key=lambda x: x["done"]) # False < True
elif sort_option == "最新创建":
    display_tasks.sort(key=lambda x: x["created_at"], reverse=True)
elif sort_option == "最早创建":
    display_tasks.sort(key=lambda x: x["created_at"], reverse=False)


# 5. 渲染列表
if not display_tasks:
    if not st.session_state.tasks:
        st.info("👋 暂无任务，请添加")
    else:
        st.info("🔍 没有找到匹配的任务")
else:
    for task in display_tasks:
        c1, c2, c3 = st.columns([0.5, 6, 0.5])
        
        with c1:
            # 核心：Key 绑定 ID，Callback 处理状态
            is_checked = st.checkbox("", value=task["done"], key=f"c_{task['id']}")
            if is_checked != task["done"]:
                set_task_done(task["id"], is_checked) # 明确传入新状态
                st.rerun()
        
        with c2:
            content = task["name"]
            if task["done"]:
                st.markdown(f"~~{content}~~")
            else:
                st.markdown(content)
        
        with c3:
            if st.button("🗑️", key=f"d_{task['id']}"):
                delete_task(task["id"])
                st.rerun()

st.markdown("---")
st.caption(f"共 {len(st.session_state.tasks)} 个任务 • 当前显示 {len(display_tasks)} 个")
