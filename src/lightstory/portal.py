"""Loopback preview: public files by default, host history/output only by explicit flag."""
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote,urlsplit
from . import workflows


def page(cfg):
    rows=workflows.catalog(cfg)
    body=''.join(f'<tr><td>{escape(x["model"])}</td><td>{escape(x["function"])}</td><td><a href="../{escape(x["workflow"])}">UI画布</a> · <a href="../{escape(x["api"])}">API</a></td></tr>' for x in rows)
    return '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LightStory Workflows · 光影故事工作流</title>
<style>
:root{color-scheme:light;--ink:#263332;--accent:#6b4b30;--paper:#f6f3ec}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1180px;margin:auto;padding:40px 28px 80px}header{padding:48px 40px;background:linear-gradient(120deg,#e9d6ba,#ebe8df 60%,#dbe3df);border:1px solid #d5cec1;border-radius:18px}small{letter-spacing:2px;color:var(--accent)}h1{font-size:clamp(32px,5vw,52px);line-height:1.12;margin:14px 0 22px}h1 span{font-size:.5em;font-weight:500;display:block;margin-top:18px}h2{margin-top:38px;font-size:25px}h3{margin:0 0 12px}p{max-width:900px}a{color:#375f5c;text-underline-offset:4px}nav{display:flex;flex-wrap:wrap;gap:12px 24px;margin-top:24px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:28px 0}.card{background:#fffdf8;border:1px solid #d9d4c9;border-radius:14px;padding:28px}.steps{color:#5c665f}.badge{display:inline-block;margin:6px 12px 0 0;font-size:14px;border:1px solid #c9bdac;border-radius:30px;padding:4px 12px}code{background:#e9e7df;padding:2px 6px;border-radius:4px;font-size:13px}table{border-collapse:collapse;width:100%;font-size:14px;background:#fffdf8}td,th{padding:12px 15px;border-bottom:1px solid #e0dcd2;text-align:left}th{background:#e9e7df}td:first-child{white-space:nowrap}input{width:100%;font:inherit;padding:12px 16px;margin:10px 0 18px;border:1px solid #c4c9c1;border-radius:8px;background:#fffdf8}.scroll{overflow:auto}.note{border-left:3px solid #b58b56;padding:4px 20px;margin:24px 0;color:#5d625b}footer{margin-top:40px;font-size:14px;color:#6a7169}@media(max-width:720px){.grid{grid-template-columns:1fr}main{padding:16px}header{padding:30px 24px}.card{padding:22px}}
</style></head><body><main>
<header><small>PRODUCTION WORKFLOWS · v0.1.0</small><h1>LightStory Workflows<span>光影故事工作流</span></h1>
<p>用一套可维护的方法，编排游戏与视频从想法到交付。保留已有创作流程，把Skill、画布、执行适配、第三方版本和安装说明收在同一工程。</p>
<span class="badge">81组UI / API</span><span class="badge">7个自主/本地适配Skill</span><span class="badge">22个Blender模块</span><span class="badge">9个H3方法按需组装</span>
<nav><a href="../README.md">README</a><a href="installation.md">安装</a><a href="quickstart.md">使用</a><a href="architecture.md">结构与分工</a><a href="validation.md">验证与限制</a></nav></header>
<section class="grid"><article class="card"><h3>Game Production</h3><p class="steps">简报与创作方向 → Web / Unreal选路 → 可玩灰盒 → 品质切片 → 资产与功能生产 → 集成与性能 → 打包试玩。</p><p>玩法、美术和UI模块按需调用；Comfy与Blender负责资产，Web调用Game Studio，Unreal走引擎工具，过场与视频接入Video流程。</p><a href="../skills/game-production-workflows/SKILL.md">打开总Skill</a> · <a href="game-workflow.md">流程导航</a></article>
<article class="card"><h3>Video Production</h3><p class="steps">剧本与规格 → 视觉开发 → 分镜 / animatic → 难点样片 → 镜头制作 → 合成剪辑与声音 → 成片播放验收。</p><p>生图负责身份、风格与关键帧；H3按镜头选路；Blender预演和结构引导用于控制；配音配乐与后期独立检查。</p><a href="../skills/video-production-workflows/SKILL.md">打开总Skill</a> · <a href="video-workflow.md">流程导航</a></article></section>
<h2>从哪一步开始</h2><ol><li>配置机器路径，运行<code>validate</code>和<code>doctor</code>。</li><li>按需安装Skill、节点、模型与客户端插件；第三方版本和许可各自管理。</li><li>新建制作项目或恢复已有状态，用户给玩法、剧本、风格和交付要求，执行者按总流程推进。</li><li>单项生成直接用Comfy Skill；只有项目需要特化时才另存Projects栏目。</li></ol>
<div class="note">历史模型记录与源码安装检查分别列明；新环境的GPU品质、实际游戏和成片仍按自己的素材验收。模型、用户素材和账户信息不随源码分发。</div>
<nav><a href="comfyui.md">Comfy执行</a><a href="blender-motion.md">Blender与动作</a><a href="integrations.md">插件和外部工具</a><a href="models-and-licenses.md">模型与许可</a><a href="maintenance.md">更新与清理</a><a href="migration.md">从原机迁移</a><a href="validation.md">验证边界</a></nav>
<h2>通用画布目录</h2><p>按模型、功能检索。输入为<code>UPLOAD_*</code>的画布必须换成自己的素材；链接打开JSON源码，原生画布安装后在ComfyUI的LightStory栏目使用。</p>
<label for="search">检索模型或功能</label><input id="search" type="search" placeholder="例如 Qwen、分镜、透明、长视频、绑定…">
<div class="scroll"><table><thead><tr><th>模型</th><th>功能</th><th>文件</th></tr></thead><tbody>'''+body+'''</tbody></table></div>
<footer>LightStory Workflows · <a href="https://github.com/yuguo-Jack/lightstory-workflows">yuguo-Jack/lightstory-workflows</a> · 文档可直接本地打开，也可通过loopback预览服务浏览。</footer>
</main><script>document.querySelector('#search').addEventListener('input',function(){const q=this.value.toLocaleLowerCase();for(const row of document.querySelectorAll('tbody tr'))row.hidden=!row.textContent.toLocaleLowerCase().includes(q)});</script></body></html>
'''


def handler(cfg,include_history=False):
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if urlsplit(self.path).path in {'/','/index.html'}:
                self.send_response(302);self.send_header('Location','/docs/overview.html');self.end_headers();return
            super().do_GET()
        def translate_path(self,raw):
            tail=unquote(urlsplit(raw).path).lstrip('/')
            parts=Path(tail).parts
            if any(x.startswith('.') for x in parts) or '..' in parts:return str(cfg.repository/'__not_served__')
            if include_history and parts and parts[0]=='workflow-support':
                archive=cfg.path('history_root') or cfg.state_root/'host-history'
                remainder=Path(*parts[1:])
                if len(parts)<2 or parts[1] not in {'validation','catalog','docs','preview','api','index.html','guide.html','README.md'}:return str(cfg.repository/'__not_served__')
                p=(archive/remainder).resolve()
                if not p.is_relative_to(archive.resolve()) or any(x.startswith('.') for x in p.relative_to(archive.resolve()).parts):return str(cfg.repository/'__not_served__')
                return str(p)
            if include_history and parts and parts[0]=='output' and cfg.outputs:
                p=(cfg.outputs/Path(*parts[1:])).resolve()
                if p.is_relative_to(cfg.outputs.resolve()):return str(p)
                return str(cfg.repository/'__not_served__')
            if not tail or tail=='index.html':return str(cfg.repository/'docs/overview.html')
            if parts and parts[0] not in {'docs','workflows','skills','README.md','README.en.md','THIRD_PARTY_NOTICES.md'}:return str(cfg.repository/'__not_served__')
            p=(cfg.repository/tail).resolve()
            if not p.is_relative_to(cfg.repository) or p.is_symlink():return str(cfg.repository/'__not_served__')
            resolved=p.relative_to(cfg.repository).parts
            if not resolved or any(x.startswith('.') for x in resolved) or resolved[0] not in {'docs','workflows','skills','README.md','README.en.md','THIRD_PARTY_NOTICES.md'}:return str(cfg.repository/'__not_served__')
            return str(p)
        def list_directory(self,path):
            self.send_error(403,'Open a named document or workflow');return None
    return Handler


def serve(cfg,port=8192,include_history=False):
    if not 1024<=int(port)<=65535:raise ValueError('Use an unprivileged valid port')
    print(f'LightStory public-doc preview: http://127.0.0.1:{port}/',flush=True)
    if include_history:print('Local host-history/output preview explicitly enabled; do not expose this port through a proxy.',flush=True)
    ThreadingHTTPServer(('127.0.0.1',port),handler(cfg,include_history)).serve_forever()
