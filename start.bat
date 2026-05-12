@echo off
cd /d "H:\Project\RTX_VSR_tool"
call venv\Scripts\activate
streamlit run app.py --server.port 8501 --server.headless true
pause
