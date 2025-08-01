#!/bin/bash

# 乳腺癌数据清洗项目 - Git管理脚本

echo "=== 乳腺癌数据清洗项目 Git 管理工具 ==="

# 检查Git状态
check_status() {
    echo "📊 检查Git状态..."
    git status
}

# 添加文件到暂存区
add_files() {
    echo "📁 添加文件到暂存区..."
    git add .
    echo "✅ 文件已添加到暂存区"
}

# 提交更改
commit_changes() {
    local message="$1"
    if [ -z "$message" ]; then
        message="Update: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    echo "💾 提交更改: $message"
    git commit -m "$message"
}

# 推送到远程仓库
push_to_remote() {
    echo "🚀 推送到远程仓库..."
    git push origin main
}

# 拉取远程更新
pull_from_remote() {
    echo "📥 拉取远程更新..."
    git pull origin main
}

# 查看提交历史
show_history() {
    echo "📜 查看提交历史..."
    git log --oneline -10
}

# 创建新分支
create_branch() {
    local branch_name="$1"
    if [ -z "$branch_name" ]; then
        echo "❌ 请提供分支名称"
        return 1
    fi
    echo "🌿 创建新分支: $branch_name"
    git checkout -b "$branch_name"
}

# 切换分支
switch_branch() {
    local branch_name="$1"
    if [ -z "$branch_name" ]; then
        echo "❌ 请提供分支名称"
        return 1
    fi
    echo "🔄 切换到分支: $branch_name"
    git checkout "$branch_name"
}

# 合并分支
merge_branch() {
    local branch_name="$1"
    if [ -z "$branch_name" ]; then
        echo "❌ 请提供要合并的分支名称"
        return 1
    fi
    echo "🔀 合并分支: $branch_name"
    git merge "$branch_name"
}

# 显示帮助信息
show_help() {
    echo "使用方法: $0 [命令] [参数]"
    echo ""
    echo "可用命令:"
    echo "  status              - 检查Git状态"
    echo "  add                 - 添加文件到暂存区"
    echo "  commit [消息]       - 提交更改"
    echo "  push                - 推送到远程仓库"
    echo "  pull                - 拉取远程更新"
    echo "  history             - 查看提交历史"
    echo "  new-branch <名称>   - 创建新分支"
    echo "  switch <分支名>     - 切换分支"
    echo "  merge <分支名>      - 合并分支"
    echo "  full-update [消息]  - 完整更新流程"
    echo "  help                - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 status                    # 检查状态"
    echo "  $0 full-update '修复bug'     # 完整更新"
    echo "  $0 new-branch feature       # 创建功能分支"
}

# 完整更新流程
full_update() {
    local message="$1"
    if [ -z "$message" ]; then
        message="Update: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    echo "🔄 开始完整更新流程..."
    
    # 检查状态
    check_status
    
    # 添加文件
    add_files
    
    # 提交更改
    commit_changes "$message"
    
    # 推送到远程
    push_to_remote
    
    echo "✅ 完整更新流程完成！"
}

# 主程序
case "$1" in
    "status")
        check_status
        ;;
    "add")
        add_files
        ;;
    "commit")
        commit_changes "$2"
        ;;
    "push")
        push_to_remote
        ;;
    "pull")
        pull_from_remote
        ;;
    "history")
        show_history
        ;;
    "new-branch")
        create_branch "$2"
        ;;
    "switch")
        switch_branch "$2"
        ;;
    "merge")
        merge_branch "$2"
        ;;
    "full-update")
        full_update "$2"
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "❌ 未知命令: $1"
        echo "使用 '$0 help' 查看帮助信息"
        exit 1
        ;;
esac 