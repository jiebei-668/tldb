# 铁路隐患审批自动化脚本

## 功能说明

自动完成铁路隐患管理系统的日报审批流程：
1. 自动登录系统
2. 导航到"全省铁路隐患库" → "日报告管理" → "日报审批"
3. 自动处理所有状态为"待审批"的项目
4. 自动填写审批意见："情况属实，同意上报"
5. 自动翻页处理所有页面

## 环境要求

- Python 3.7+
- Microsoft Edge 浏览器（系统默认自带）

## 安装步骤

### 1. 安装Python依赖

```bash
cd /home/jiebei/铁路自动化脚本
pip install -r requirements.txt
```

### 2. 确认Edge浏览器已安装

Edge 浏览器通常已预装在 Windows 10/11 系统中。

Linux 用户可通过以下命令安装：
```bash
# Ubuntu/Debian
wget https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install microsoft-edge-stable
```

## 使用方法

### 方式一：使用配置文件（推荐）

1. 编辑 `config.ini` 文件，填入您的账号密码：
```ini
[credentials]
username = your_username
password = your_password
```

2. 运行脚本：
```bash
cd /home/jiebei/铁路自动化脚本
python railway_approval.py
```

### 方式二：使用命令行参数

```bash
python railway_approval.py your_username your_password
```

例如：
```bash
python railway_approval.py zhangsan pass123
```

**注意**：命令行参数会覆盖配置文件中的设置。

### 方式三：仅测试登录功能

编辑 `railway_approval.py` 文件最后几行：

```python
# bot.run()  # 注释掉
bot.test_login_only()  # 取消注释
```

## 运行流程

1. **打开网站** - 脚本自动打开 Edge 浏览器并访问网站
2. **输入账号密码** - 自动填入用户名和密码
3. **等待验证码** - 脚本暂停，**你手动输入验证码**
4. **继续登录** - 在终端按回车键，脚本 点击登录
5. **导航菜单** - 自动点击：全省铁路隐患库 → 日报告管理 → 日报审批
6. **批量审批** - 自动处理所有"待审批"项目
7. **自动翻页** - 处理完一页后自动翻下一页
8. **完成** - 处理完后等待，按回车关闭浏览器

## 输出示例

```
[22:00:00] ==================================================
[22:00:00] 铁路隐患审批自动化脚本启动
[22:00:00] ==================================================
[22:00:01] 正在打开网站...
[22:00:03] 开始登录流程...
[22:00:03] 输入用户名...
[22:00:03] 输入密码...
[22:00:03] ==================================================
[22:00:03] 请手动输入验证码，输入完成后按回车键继续...
按回车键继续...⏎  ← 你在这里按回车
[22:00:10] 点击登录按钮...
[22:00:10] 登录请求已发送...
[22:00:10] 等待登录成功...
[22:00:13] 开始导航到审批页面...
[22:00:13] 正在点击菜单: 全省铁路隐患库
[22:00:14] 成功点击: 全省铁路隐患库
[22:00:15] 正在点击子菜单项: 日报告管理
[22:00:16] 成功点击子菜单: 日报告管理
[22:00:17] 正在点击子菜单项: 日报审批
[22:00:18] 成功点击子菜单: 日报审批
[22:00:18] 等待审批页面加载...
[22:00:21] 正在处理第 1 页...
[22:00:21] ------------------------------
[22:00:21] 正在处理当前页面的待审批项目...
[22:00:22] 找到 10 行数据
[22:00:22] 第 1 行内容: ['...', '...', '待审批', '...', '操作']
[22:00:22] 发现待审批项目 (第 1 行，状态在第 3 列)
[22:00:22] 在第 5 列找到审批按钮
[22:00:22] 点击审批按钮...
[22:00:22] 正在填写审批意见...
[22:00:23] 审批弹窗已打开
[22:00:23] 已填写审批意见
[22:00:23] 点击保存按钮...
[22:00:24] 保存成功
...
```

## 故障排查

### 1. EdgeDriver 版本问题

**错误信息**：找不到 EdgeDriver 或版本不匹配

**解决方法**：
Selenium 4.x 会自动下载匹配的 EdgeDriver，无需手动安装。如果仍有问题：
```bash
# 更新 selenium 到最新版本
pip install --upgrade selenium
```

### 2. 找不到 Edge 浏览器

**错误信息**：`WebDriverException: Message: 'edge' executable needs to be in PATH`

**解决方法**：
- Windows：Edge 已预装，无需额外操作
- Linux：按照上面"安装步骤"中的命令安装 Edge
- 确认 Edge 已安装：
  ```bash
  # Windows
  where msedge

  # Linux
  which microsoft-edge
  ```

### 2. 找不到元素错误

**错误信息**：`NoSuchElementException: Unable to locate element`

**解决方法**：
- 网页结构可能发生变化
- 打开浏览器开发者工具（F12）检查元素的 class 名称
- 更新脚本中的选择器

### 3. 超时错误

**错误信息**：`TimeoutException`

**解决方法**：
- 网络较慢，增加等待时间
- 编辑脚本，增加 `time.sleep()` 的秒数

### 4. 菜单点击失败

**现象**：脚本显示"未找到菜单"

**解决方法**：
- 手动打开网站，用 F12 查看菜单的 HTML 结构
- 更新 `click_menu()` 函数中的选择器

## 配置选项

### 修改账号密码

**方式1：编辑配置文件（推荐）**

编辑 `config.ini` 文件：
```ini
[credentials]
username = your_username
password = your_password
```

**方式2：修改代码默认值**

编辑 `railway_approval.py` 中的 `load_config()` 函数：
```python
return 'your_username', 'your_password'
```

### 修改审批意见

编辑 `railway_approval.py` 找到：
```python
textarea.send_keys("情况属实，同意上报")
```

### 调整等待时间

如果网络较慢，可以搜索 `time.sleep` 增加等待时间：
- 表格渲染等待：搜索 `等待表格渲染`
- 审批后等待：搜索 `等待页面数据更新`


## 文件说明

| 文件 | 说明 |
|------|------|
| `railway_approval.py` | 主脚本文件 |
| `config.ini` | 配置文件（存储账号密码） |
| `requirements.txt` | Python依赖 |
| `README.md` | 使用说明（本文件） |

## 技术说明

- 使用 **Selenium** 进行浏览器自动化
- 使用 **Microsoft Edge** 浏览器（系统自带）
- 针对 **Element UI** 框架优化
- 使用 XPath 和 CSS 选择器定位元素
- 支持自动翻页和批量处理

## 注意事项

1. **验证码需要手动输入**，脚本会在此时暂停
2. 建议先运行 `test_login_only()` 测试登录功能
3. 如果网站结构更新，可能需要更新元素选择器
4. 首次运行建议观察整个过程，确保正常工作
5. 不要同时运行多个脚本实例

## 获取帮助

如果遇到问题：
1. 查看终端输出的详细日志
2. 用 F12 检查网页元素结构
3. 确认网络连接正常
4. 确认 Edge 浏览器已正确安装
5. 更新 Selenium 到最新版本：`pip install --upgrade selenium`
