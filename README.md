# 投资复盘工具站 MVP

这是一个用于跑通 AI 建站流程的静态网站样品：

- 首页落地页
- 可用的投资复盘报告生成工具
- 两篇 SEO 内容页
- `sitemap.xml` 和 `robots.txt`
- 可直接部署到 Vercel、Netlify 或任意静态托管

## 本地预览

直接打开 `index.html` 即可，也可以运行：

```bash
python -m http.server 5173
```

然后访问：

```text
http://localhost:5173
```

## 上线流程

1. 新建 GitHub 仓库。
2. 把本目录所有文件上传到仓库。
3. 在 Vercel 新建项目并导入仓库。
4. Framework Preset 选择 Other。
5. Build Command 留空。
6. Output Directory 留空或填 `.`。
7. 部署完成后，把 `sitemap.xml` 和 `robots.txt` 里的 `https://example.com` 换成你的正式域名。

## 下一步商业化

- 接入用户登录和历史记录
- 接入 AI 生成月度复盘
- 添加会员限制
- 增加更多 SEO 内容页
- 接入 Google AdSense 或其他广告平台
