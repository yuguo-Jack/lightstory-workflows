"""Loopback preview: public files by default, host history/output only by explicit flag."""
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote,urlsplit
from . import workflows


def page(cfg):
    rows=workflows.catalog(cfg)
    names={'Qwen-Image 2.1':'Qwen-Image-2.1','Ming-3.0-TTS':'Ming-3.0-TTS Tiny'}
    body=''.join(f'<tr><td>{escape(names.get(x["model"],x["model"]))}</td><td>{escape(x["function"])}</td><td><a href="../{escape(x["workflow"])}">UI画布</a> · <a href="../{escape(x["api"])}">API</a></td></tr>' for x in rows)
    return '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LightStory Workflows · 光影故事工作流</title>
<style>
:root{color-scheme:light;--ink:#263332;--accent:#6b4b30;--paper:#f6f3ec}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1180px;margin:auto;padding:40px 28px 80px}header{padding:48px 40px;background:linear-gradient(120deg,#e9d6ba,#ebe8df 60%,#dbe3df);border:1px solid #d5cec1;border-radius:18px}small{letter-spacing:2px;color:var(--accent)}h1{font-size:clamp(32px,5vw,52px);line-height:1.12;margin:14px 0 22px}h1 span{font-size:.5em;font-weight:500;display:block;margin-top:18px}h2{margin-top:38px;font-size:25px}h3{margin:0 0 12px}p{max-width:900px}a{color:#375f5c;text-underline-offset:4px}nav{display:flex;flex-wrap:wrap;gap:12px 24px;margin-top:24px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:28px 0}.card{background:#fffdf8;border:1px solid #d9d4c9;border-radius:14px;padding:28px}.steps{color:#5c665f}.badge{display:inline-block;margin:6px 12px 0 0;font-size:14px;border:1px solid #c9bdac;border-radius:30px;padding:4px 12px}code{background:#e9e7df;padding:2px 6px;border-radius:4px;font-size:13px}table{border-collapse:collapse;width:100%;font-size:14px;background:#fffdf8}td,th{padding:12px 15px;border-bottom:1px solid #e0dcd2;text-align:left}th{background:#e9e7df}td:first-child{white-space:nowrap}input{width:100%;font:inherit;padding:12px 16px;margin:10px 0 18px;border:1px solid #c4c9c1;border-radius:8px;background:#fffdf8}.scroll{overflow:auto}.note{border-left:3px solid #b58b56;padding:4px 20px;margin:24px 0;color:#5d625b}footer{margin-top:40px;font-size:14px;color:#6a7169}@media(max-width:720px){.grid{grid-template-columns:1fr}main{padding:16px}header{padding:30px 24px}.card{padding:22px}}
</style></head><body><main>
<header><small>PRODUCTION WORKFLOWS · v0.1.0</small><h1>LightStory Workflows<span>光影故事工作流</span></h1>
<p>用一套可维护的方法，编排游戏与视频从想法到交付。保留已有创作流程，把Skill、画布、执行适配、第三方版本和安装说明收在同一工程。</p>
<span class="badge">81组UI / API</span><span class="badge">7个自主/本地适配Skill</span><span class="badge">22个Blender模块</span><span class="badge">9个MiniMax H3方法按需组装</span>
<nav><a href="../README.md">README</a><a href="installation.md">安装</a><a href="quickstart.md">使用</a><a href="architecture.md">结构与分工</a><a href="validation.md">验证与限制</a></nav></header>
<section class="grid"><article class="card"><h3>Game Production</h3><p class="steps">简报与创作方向 → Web / Unreal选路 → 可玩灰盒 → 品质切片 → 资产与功能生产 → 集成与性能 → 打包试玩。</p><p>玩法、美术和UI模块按需调用；Comfy与Blender负责资产，Web调用Game Studio，Unreal走引擎工具，过场与视频接入Video流程。</p><a href="../skills/game-production-workflows/SKILL.md">打开总Skill</a> · <a href="game-workflow.md">流程导航</a></article>
<article class="card"><h3>Video Production</h3><p class="steps">剧本与规格 → 视觉开发 → 分镜 / animatic → 难点样片 → 镜头制作 → 合成剪辑与声音 → 成片播放验收。</p><p>Qwen-Image-2.1制作关键帧，MiniMax H3生成视频；Blender负责预演与CG，Ming-3.0-TTS Tiny配音，MiniMax Music 3配乐，后期工具完成剪辑。</p><a href="../skills/video-production-workflows/SKILL.md">打开总Skill</a> · <a href="video-workflow.md">流程导航</a></article></section>
<h2>从哪一步开始</h2><ol><li>配置机器路径，运行<code>validate</code>和<code>doctor</code>。</li><li>按需安装Skill、节点、模型与客户端插件；第三方版本和许可各自管理。</li><li>新建制作项目或恢复已有状态，用户给玩法、剧本、风格和交付要求，执行者按总流程推进。</li><li>单项生成直接用Comfy Skill；只有项目需要特化时才另存Projects栏目。</li></ol>
<div class="note"><strong>模型画布实测环境：Windows＋NVIDIA GeForce RTX 4080（16GB显存）＋32GB内存。</strong>81组工作流已有本机样例运行记录，量化、低内存方案及输入规模见<a href="validation.md#验证环境与范围">验证说明</a>。GPU/CPU运行与工程安装检查分别记录；模型、私人素材和账户信息不随源码分发。</div>
<nav><a href="comfyui.md">Comfy执行</a><a href="blender-motion.md">Blender与动作</a><a href="integrations.md">插件和外部工具</a><a href="models-and-licenses.md">模型与许可</a><a href="maintenance.md">更新与清理</a><a href="migration.md">从原机迁移</a><a href="validation.md">验证边界</a></nav>
<h2>通用画布目录</h2><p>按模型、功能检索。输入为<code>UPLOAD_*</code>的画布必须换成自己的素材；链接打开JSON源码，原生画布安装后在ComfyUI的LightStory栏目使用。</p>
<label for="search">检索模型或功能</label><input id="search" type="search" placeholder="例如 Qwen、分镜、透明、长视频、绑定…">
<div class="scroll"><table><thead><tr><th>模型名称</th><th>工作流功能</th><th>文件</th></tr></thead><tbody>'''+body+'''</tbody></table></div>
<section><h2>欢迎提需求与反馈</h2><p>欢迎在<a href="https://github.com/yuguo-Jack/lightstory-workflows/issues">Issues</a>提需求、反馈问题或分享实际使用场景。新模型与工作流、游戏/视频制作环节、部署适配、批量处理、性能和文档改进，都欢迎讨论。</p><p>不需要先有完整方案：说说你想做什么、目前卡在哪里、使用什么硬件环境，有参考样例或复现步骤更好。真实需求会帮助确定后续完善方向，也欢迎通过Pull Request一起改进。希望大家多提想法，让这套流程越来越实用。</p></section>
<section><h2>打赏支持</h2><p>如果这套流程对你有帮助，欢迎通过支付宝自愿打赏，支持持续维护、模型适配和本地验证。<strong>提需求和反馈无需打赏，欢迎大家多提建议。</strong></p><a href="assets/alipay-support.jpg"><img src="assets/alipay-support.jpg" alt="支付宝打赏收款码，收款人：Jack" width="300" style="max-width:100%;height:auto" loading="lazy"></a><p>使用支付宝扫码；点击图片可查看原图。</p></section>
<footer>LightStory Workflows · 文档可直接本地打开，也可通过loopback预览服务浏览。</footer>
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
