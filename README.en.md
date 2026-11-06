# LightStory Workflows

A local-first production methodology for games and videos: agent Skills, 81 portable ComfyUI UI/API workflows, Blender adapters, pinned dependencies and practical installation/validation guides.

[Repository](https://github.com/yuguo-Jack/lightstory-workflows) · [中文完整说明](README.md)

- **Game Production Workflows:** requirements, creative direction, Web/Unreal route selection, playable prototype, vertical slice, asset production, integration, testing, performance and delivery.
- **Video Production Workflows:** script and look development, storyboard/animatic, shot routing, references and CG previs, generation, continuity, compositing, audio, editing, grading and delivery.
- **ComfyUI Local Workflows:** independent image/video/3D/rigging/TTS/music tasks and the execution layer used by both production workflows.

Use Python 3.11+ from the source checkout:

```bash
git clone https://github.com/yuguo-Jack/lightstory-workflows.git
cd lightstory-workflows
python -m pip install -e .
python tools/lightstory.py config init --template posix
# Edit config/local.json for your machine.
python tools/lightstory.py validate
python tools/lightstory.py doctor
python tools/lightstory.py install skills --agent codex
python tools/lightstory.py install skills --agent codex --apply
```

Use `--template windows` on Windows and `--agent claude` for Claude. Windows links require system permission; Skills also support explicit `--copy --apply`. Keep the source checkout: editable installation and linked Skills use its resources. Follow the installation guide for models, nodes, plugins and branch-specific environments before generating content.

Windows is the original deployment target; POSIX configuration support is not a claim of Linux/macOS GPU validation. The CLI can also run directly without pip installation through `tools/lightstory.py`.

Read the [installation guide](docs/installation.md), [architecture](docs/architecture.md), [dependency notices](THIRD_PARTY_NOTICES.md), [validation boundaries](docs/validation.md) and [maintenance guide](docs/maintenance.md). Most detailed methods are currently in Chinese.

Third-party code, models, client plugins and online services have independent licences and setup requirements. Model weights, personal assets, credentials, runtime state and large test media are not distributed. Existing host test results do not certify a new installation or a finished creative work.
