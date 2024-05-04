import streamlit as st

option = st.selectbox(
    "请选择你想要复习的学科",
    ("水力学公式", "理论力学公式", "自动控制原理"))

if option == "水力学公式":
    with open('水力学公式.md') as f:
        data = f.read()
        st.markdown(f'{data}')
        f.close()
else:
    st.write("想多了，还没整理")
