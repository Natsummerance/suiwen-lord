# 随文 · Suiwen

面向 macOS 的本地语义输入法。此仓库用于发布工具、插件索引和软件更新；核心软件仍在开发，源码暂不公开。

## 可选语言插件

语言包与主程序分开，按需安装。下载固定官方构建并核验 SHA256；不修改系统输入法。

需要 Python 3.12 或更新版本。

```sh
python3 tools/plugins.py list
python3 tools/plugins.py install mozc
python3 tools/plugins.py remove mozc
```

默认存储在 `~/Library/Application Support/Suiwen/plugins/`；移除时保留在该目录 `.trash/`，可恢复。这里只准备 Fcitx 插件文件，实际加载还需要兼容的 Fcitx 主程序。

支持日语、韩语、粤拼、注音、越南语和 m17n 多语言方案。请看 [固定版本目录](plugins/catalog.json)。不会下载模型，也不会注册或切换输入法。

## 当前发布边界

当前仅有可独立使用的插件下载工具和目录。随文应用仍在本机开发验收，尚未发布可供其他 Mac 独立运行的安装包。训练结果尚未通过完整质量评估。

工具代码采用 MIT；第三方组件保留各自许可。核心软件和训练模型未包含在此仓库，不得把工具的 MIT 许可理解为整个应用或第三方依赖的许可。
