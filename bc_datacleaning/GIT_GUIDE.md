# Git管理简明说明

本项目推荐使用Git进行版本管理。以下是常用的Git操作方法：

---

## 1. 首次上传项目到远程仓库

1. 在GitHub/Gitee等平台新建仓库（如：bc_datacleaning）。
2. 关联本地项目与远程仓库：
   ```bash
   git remote add origin https://github.com/yourname/bc_datacleaning.git
   ```
3. 添加、提交并推送代码：
   ```bash
   git add .
   git commit -m "初始化项目"
   git push -u origin main
   ```

---

## 2. 日常更新项目

1. 查看当前状态：
   ```bash
   git status
   ```
2. 添加和提交更改：
   ```bash
   git add .
   git commit -m "更新说明"
   ```
3. 推送到远程仓库：
   ```bash
   git push
   ```
4. 拉取远程最新代码：
   ```bash
   git pull
   ```

---

## 3. 分支与协作（可选）

- 创建新分支：
  ```bash
  git checkout -b feature-xxx
  ```
- 切换分支：
  ```bash
  git checkout main
  ```
- 合并分支：
  ```bash
  git merge feature-xxx
  ```

---

## 4. 使用自动化脚本

本项目提供 `git_management.sh` 脚本，简化常用操作：

- 查看帮助：
  ```bash
  ./git_management.sh help
  ```
- 一键完整更新（添加、提交、推送）：
  ```bash
  ./git_management.sh full-update "更新说明"
  ```
- 查看提交历史：
  ```bash
  ./git_management.sh history
  ```

---

## 5. 常见问题

- **推送报错：rejected**
  - 先执行 `git pull` 拉取远程最新代码，再推送。
- **.gitignore未生效**
  - 已经被跟踪的文件需先用 `git rm --cached 文件名` 移除后再提交。

---

如需更多Git用法或遇到冲突、协作问题，欢迎随时咨询！ 