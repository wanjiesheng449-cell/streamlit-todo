import streamlit as st

# 设置页面标题和图标
st.set_page_config(page_title="极简代办清单", page_icon="📝")

st.title("📝 我的极简代办清单")
st.markdown("---")

# 1. 初始化任务数据 (存储在 session_state 中，防止页面刷新后数据丢失)
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# 2. 侧边栏：添加新任务
with st.sidebar:
    st.header("➕ 添加新任务")
    new_task_name = st.text_input("请输入任务内容", key="new_task_input")
    if st.button("添加任务", use_container_width=True):
        if new_task_name.strip():
            st.session_state.tasks.append({"name": new_task_name.strip(), "done": False})
            st.rerun()  # 刷新页面以显示新任务
        else:
            st.warning("任务内容不能为空哦！")

    st.markdown("---")
    if st.button("🧪 清空所有任务", type="secondary", use_container_width=True):
        st.session_state.tasks = []
        st.rerun()

# 3. 主界面：展示任务列表
if not st.session_state.tasks:
    st.info("目前没有任务，去侧边栏加一个吧！")
else:
    for index, task in enumerate(st.session_state.tasks):
        # 创建三列：状态、名字、删除按钮
        col1, col2, col3 = st.columns([1, 6, 1])
        
        # 标记完成 (勾选框)
        with col1:
            is_done = st.checkbox("", value=task["done"], key=f"check_{index}")
            if is_done != task["done"]:
                st.session_state.tasks[index]["done"] = is_done
                st.rerun()

        # 任务描述 (如果完成则显示删除线)
        with col2:
            if task["done"]:
                st.markdown(f"~~{task['name']}~~")
            else:
                st.markdown(task["name"])

        # 删除按钮
        with col3:
            if st.button("🗑️", key=f"del_{index}"):
                st.session_state.tasks.pop(index)
                st.rerun()

# 4. 页脚提示
st.markdown("---")
st.caption("由 Streamlit 驱动 • 部署助手制作")
