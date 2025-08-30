@echo off
chcp 65001 >nul
echo 🔄 开始保持GitHub仓库活跃...
echo 📅 时间: %date% %time%

cd /d "D:\pj\getwaterdata"

echo 🐍 运行Python活跃度维护脚本...
python keep_alive.py

echo ✅ 活跃度维护完成！
echo 📅 下次运行时间: 24小时后
pause

