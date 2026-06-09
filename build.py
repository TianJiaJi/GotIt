"""GotIt 打包构建脚本。"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


class BuildManager:
    """打包构建管理器。"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dist_dir = project_root / "dist"
        self.build_dir = project_root / "build"
        self.spec_file = project_root / "GotIt.spec"

    def clean(self) -> None:
        """清理构建目录。"""
        print("[清理] 删除构建目录...")
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        print("[清理] 完成")

    def check_dependencies(self) -> bool:
        """检查构建依赖。"""
        print("[检查] 验证构建依赖...")
        try:
            import PyInstaller
            print(f"[检查] PyInstaller 版本: {PyInstaller.__version__}")
            return True
        except ImportError:
            print("[错误] PyInstaller 未安装，请运行: pip install pyinstaller")
            return False

    def create_spec(self) -> None:
        """创建 PyInstaller 配置文件。"""
        print("[配置] 生成打包配置...")

        # 提前计算所有值，避免在 f-string 中使用 self
        project_root = self.project_root
        src_dir = project_root / "src"
        icon_path = project_root / "src" / "assets" / "gotit.ico"
        icon_str = str(icon_path) if icon_path.exists() else None

        # 数据文件列表
        datas = [
            (str(project_root / "config" / "config.example.json"), "config"),
        ]

        # 添加图标文件用于托盘显示
        if icon_path.exists():
            datas.append((str(icon_path), "src/assets"))
            print(f"[配置] 添加图标文件: {icon_path}")

        # 添加 OCR 模型文件（如果存在）
        # 注意：RapidOCR 期望模型在 rapidocr/models/ 目录
        models_dir = project_root / "models" / "ocr"
        if models_dir.exists():
            model_files = list(models_dir.glob("*.onnx"))
            for model_file in model_files:
                # 放到 rapidocr/models/ 目录（RapidOCR 期望的位置）
                datas.append((str(model_file), "rapidocr/models"))
            print(f"[配置] 找到 {len(model_files)} 个 OCR 模型文件")
        else:
            print("[配置] OCR 模型目录不存在，将跳过模型打包")

        # 添加 onnxruntime DLL 文件
        binaries = []
        try:
            import onnxruntime
            import glob
            onnx_path = Path(onnxruntime.__file__).parent
            capi_dir = onnx_path / "capi"

            if capi_dir.exists():
                for dll_file in capi_dir.glob("*.dll"):
                    binaries.append((str(dll_file), "."))
                    print(f"[配置] 添加 onnxruntime DLL: {dll_file.name}")
        except (ImportError, AttributeError) as e:
            print(f"[警告] 无法查找 onnxruntime DLL: {e}")

        # 添加 rapidocr 配置文件
        try:
            import rapidocr
            rapidocr_path = Path(rapidocr.__file__).parent
            config_files = ["default_models.yaml", "config.yaml"]
            for config_file in config_files:
                config_path = rapidocr_path / config_file
                if config_path.exists():
                    datas.append((str(config_path), "rapidocr"))
                    print(f"[配置] 添加 rapidocr 配置: {config_file}")
        except (ImportError, AttributeError) as e:
            print(f"[警告] 无法查找 rapidocr 配置: {e}")

        # 隐藏导入
        hidden_imports = [
            "core.config",
            "core.workflow",
            "core.screenshot",
            "core.ocr",
            "core.model_manager",
            "core.ai_answer",
            "core.llm_client",
            "core.clipboard_chat",
            "core.region",
            "core.notifier",
            "core.tray_icon",
            "ui.app_ui",
            "utils.hotkey",
            "rapidocr_onnxruntime",
            "onnxruntime",
            "onnxruntime.capi.onnxruntime_pybind11_state",
            "pynput.keyboard._win32",
            "pynput.mouse._win32",
            "pystray",
            "PIL._imaging",
            "PIL._imagingmath",
            "PIL._imagingmorph",
        ]

        # 生成 spec 文件内容
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ["gotit.py"],
    pathex=['{project_root}', '{src_dir}'],
    binaries={binaries},
    datas={datas},
    hiddenimports={hidden_imports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=["pyi_rth_gotit.py"],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GotIt",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={repr(icon_str)},
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="GotIt",
)
'''

        with open(self.spec_file, "w", encoding="utf-8") as f:
            f.write(spec_content)

        print(f"[配置] 配置文件已生成: {self.spec_file}")

    def build(self, clean: bool = True) -> bool:
        """
        执行打包构建。

        Args:
            clean: 是否先清理构建目录

        Returns:
            是否构建成功
        """
        if not self.check_dependencies():
            return False

        if clean:
            self.clean()

        # 创建 spec 文件
        self.create_spec()

        print("[构建] 开始打包...")
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "PyInstaller",
                    "--clean",
                    str(self.spec_file),
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print("[错误] 打包失败:")
                print(result.stdout)
                print(result.stderr)
                return False

            print("[构建] 打包完成！")
            print(f"[构建] 输出位置: {self.dist_dir / 'GotIt'}")

            # 复制必要文件到输出目录
            self._copy_runtime_files()

            return True

        except Exception as e:
            print(f"[错误] 构建过程出错: {e}")
            return False

    def _copy_runtime_files(self) -> None:
        """复制运行时必要文件到输出目录。"""
        output_dir = self.dist_dir / "GotIt"
        print("[构建] 复制运行时文件...")

        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 创建必要的目录结构
        config_dir = output_dir / "config"
        config_dir.mkdir(exist_ok=True)

        models_dir = output_dir / "models" / "ocr"
        models_dir.mkdir(parents=True, exist_ok=True)

        # 复制配置示例文件
        config_example = self.project_root / "config" / "config.example.json"
        if config_example.exists():
            shutil.copy2(config_example, config_dir / "config.example.json")

        print("[构建] 运行时文件复制完成")
        print("[提示] OCR 模型已打包到程序中，无需下载")

    def build_single_exe(self) -> bool:
        """构建单文件版本。"""
        if not self.check_dependencies():
            return False

        self.clean()

        print("[构建] 开始打包（单文件版本）...")

        hidden_imports = [
            "--hidden-import=core.config",
            "--hidden-import=core.workflow",
            "--hidden-import=core.screenshot",
            "--hidden-import=core.ocr",
            "--hidden-import=core.model_manager",
            "--hidden-import=core.ai_answer",
            "--hidden-import=core.llm_client",
            "--hidden-import=core.clipboard_chat",
            "--hidden-import=core.region",
            "--hidden-import=core.notifier",
            "--hidden-import=core.tray_icon",
            "--hidden-import=ui.app_ui",
            "--hidden-import=utils.hotkey",
            "--hidden-import=rapidocr_onnxruntime",
            "--hidden-import=onnxruntime",
            "--hidden-import=pynput.keyboard._win32",
            "--hidden-import=pynput.mouse._win32",
            "--hidden-import=pystray",
            "--hidden-import=WindowsToasts",
        ]

        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--windowed",  # 不显示控制台
            "--name=GotIt",
            "--icon=src/assets/gotit.ico",
            "--add-data=config/config.example.json;config",
            "--runtime-tmpdir=.",  # 设置运行时临时目录
            "--runtime-hook=pyi_rth_gotit.py",  # 添加运行时钩子
        ]

        # 添加 onnxruntime DLL 文件
        try:
            import onnxruntime
            onnx_path = Path(onnxruntime.__file__).parent / "capi"
            if onnx_path.exists():
                for dll_file in onnx_path.glob("*.dll"):
                    cmd.append(f"--add-binary={dll_file};.")
                    print(f"[配置] 添加 DLL: {dll_file.name}")
        except (ImportError, AttributeError):
            pass

        # 添加 OCR 模型文件
        # 注意：RapidOCR 期望模型在 rapidocr/models/ 目录
        models_dir = self.project_root / "models" / "ocr"
        if models_dir.exists():
            model_count = 0
            for model_file in models_dir.glob("*.onnx"):
                cmd.append(f"--add-data={model_file};rapidocr/models")
                model_count += 1
            print(f"[配置] 添加 {model_count} 个 OCR 模型文件")
        else:
            print("[配置] OCR 模型目录不存在，将跳过")

        # 添加 rapidocr 配置文件
        try:
            import rapidocr
            rapidocr_path = Path(rapidocr.__file__).parent
            for config_file in ["default_models.yaml", "config.yaml"]:
                config_path = rapidocr_path / config_file
                if config_path.exists():
                    cmd.append(f"--add-data={config_path};rapidocr")
                    print(f"[配置] 添加 rapidocr 配置: {config_file}")
        except (ImportError, AttributeError):
            pass

        cmd.extend(hidden_imports)
        cmd.append("gotit.py")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print("[错误] 打包失败:")
                print(result.stdout)
                print(result.stderr)
                return False

            print("[构建] 打包完成！")
            print(f"[构建] 输出位置: {self.dist_dir / 'GotIt.exe'}")
            return True

        except Exception as e:
            print(f"[错误] 构建过程出错: {e}")
            return False


def main():
    """主函数。"""
    import argparse

    parser = argparse.ArgumentParser(description="GotIt 打包构建工具")
    parser.add_argument(
        "--single",
        action="store_true",
        help="构建单文件版本",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="不清理构建目录",
    )

    args = parser.parse_args()

    # 获取项目根目录
    project_root = Path(__file__).parent.resolve()

    build_manager = BuildManager(project_root)

    if args.single:
        success = build_manager.build_single_exe()
    else:
        success = build_manager.build(clean=not args.no_clean)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
