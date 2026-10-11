#!/usr/bin/env python3
"""
tests/test_kit_installer.py
Testes unitários para o Instalador Unificado e Portabilidade do XP Multi-Agent Kit (SPEC-002).
Cobertura integral dos Acceptance Criteria AC-1 a AC-6 (TDD RED -> GREEN).
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# O módulo scripts.kit_installer será implementado para satisfazer estes testes (RED -> GREEN)
from scripts.kit_installer import (
    DependencyChecker,
    PathConfigurator,
    ProjectInstaller,
    GlobalInstaller,
    KitDoctor,
    main,
)


class TestDependencyChecker(unittest.TestCase):
    """AC-2: Verificação e diagnóstico de dependências do sistema."""

    def setUp(self):
        self.checker = DependencyChecker()

    def test_check_python_version_valid(self):
        result = self.checker.check_python()
        self.assertTrue(result["ok"])
        self.assertGreaterEqual(result["major"], 3)
        self.assertGreaterEqual(result["minor"], 8)

    @patch("sys.version_info", (3, 7, 0, "final", 0))
    def test_check_python_version_outdated(self):
        result = self.checker.check_python()
        self.assertFalse(result["ok"])
        self.assertIn("requer Python >= 3.8", result["message"])

    @patch("shutil.which")
    def test_check_command_git_found(self, mock_which):
        mock_which.side_effect = lambda cmd: "/usr/bin/git" if cmd == "git" else None
        result = self.checker.check_command("git", required=True)
        self.assertTrue(result["ok"])
        self.assertEqual(result["path"], "/usr/bin/git")

    @patch("shutil.which", return_value=None)
    def test_check_command_git_missing(self, mock_which):
        result = self.checker.check_command("git", required=True)
        self.assertFalse(result["ok"])
        self.assertIn("não encontrado", result["message"])

    def test_detect_package_manager(self):
        with patch("shutil.which") as mock_which:
            mock_which.side_effect = lambda cmd: "/usr/bin/apt-get" if cmd == "apt-get" else None
            pm, cmd = self.checker.detect_package_manager()
            self.assertEqual(pm, "apt")
            self.assertIn("apt-get install", cmd)

    def test_check_all_dependencies_summary(self):
        with patch.object(self.checker, "check_python", return_value={"ok": True, "message": "Python 3.10"}), \
             patch.object(self.checker, "check_command", return_value={"ok": True, "message": "OK"}):
            summary = self.checker.check_all()
            self.assertTrue(summary["can_proceed"])
            self.assertIn("python", summary["checks"])
            self.assertIn("git", summary["checks"])


class TestPathConfigurator(unittest.TestCase):
    """AC-6: Adição idempotente de ~/.local/bin ao PATH no shell RC."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.bashrc = Path(self.temp_dir) / ".bashrc"
        self.bashrc.write_text("# Arquivo existente\nexport FOO=bar\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_path_when_missing(self):
        configurator = PathConfigurator(rc_files=[self.bashrc])
        added = configurator.ensure_path_in_rc(bin_dir="/custom/local/bin")
        self.assertTrue(added)
        content = self.bashrc.read_text(encoding="utf-8")
        self.assertIn("/custom/local/bin", content)
        self.assertIn("export PATH=", content)

    def test_idempotent_no_duplicate(self):
        configurator = PathConfigurator(rc_files=[self.bashrc])
        configurator.ensure_path_in_rc(bin_dir="/custom/local/bin")
        # Segunda execução: não deve adicionar novamente
        added_again = configurator.ensure_path_in_rc(bin_dir="/custom/local/bin")
        self.assertFalse(added_again)
        content = self.bashrc.read_text(encoding="utf-8")
        self.assertEqual(content.count("/custom/local/bin"), 1)


class TestProjectInstaller(unittest.TestCase):
    """AC-5: Injeção isolada em projeto específico com links simbólicos."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir) / "sample_project"
        self.project_dir.mkdir(parents=True)
        # Mock do diretório do kit
        self.kit_dir = Path(self.temp_dir) / "xp-kit"
        self.kit_dir.mkdir()
        (self.kit_dir / ".agents" / "policies").mkdir(parents=True)
        (self.kit_dir / ".agents" / "rules").mkdir(parents=True)
        (self.kit_dir / ".agents" / "workflows").mkdir(parents=True)
        (self.kit_dir / ".agents" / "templates").mkdir(parents=True)
        (self.kit_dir / "templates").mkdir(parents=True)
        (self.kit_dir / "templates" / "universal.geminiignore").write_text("*.log\nnode_modules/\n")
        (self.kit_dir / "AGENTS.md").write_text("# Master AGENTS.md\n")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_install_project_creates_structure_and_symlinks(self):
        installer = ProjectInstaller(kit_dir=self.kit_dir)
        res = installer.install_project(self.project_dir, use_symlinks=True)
        self.assertTrue(res["ok"])

        # Verifica pasta .agents no projeto
        project_agents = self.project_dir / ".agents"
        self.assertTrue(project_agents.is_dir())

        # Verifica links simbólicos para policies, rules, workflows, templates
        for folder in ["policies", "rules", "workflows", "templates"]:
            target = project_agents / folder
            self.assertTrue(target.is_symlink() or target.is_dir())

        # Verifica AGENTS.md na raiz do projeto
        project_agents_md = self.project_dir / "AGENTS.md"
        self.assertTrue(project_agents_md.is_file())

        # Verifica ignore files
        self.assertTrue((self.project_dir / ".geminiignore").is_file())
        self.assertTrue((self.project_dir / ".antigravityignore").is_file())

        # Verifica memória de projeto inicializada
        memory_file = project_agents / "memory" / "PROJECT_MEMORY.md"
        self.assertTrue(memory_file.is_file())

    def test_preserve_existing_project_memory(self):
        installer = ProjectInstaller(kit_dir=self.kit_dir)
        project_agents = self.project_dir / ".agents"
        memory_dir = project_agents / "memory"
        memory_dir.mkdir(parents=True)
        custom_memory = memory_dir / "PROJECT_MEMORY.md"
        custom_memory.write_text("# Memória Customizada Prévia", encoding="utf-8")

        res = installer.install_project(self.project_dir, use_symlinks=True)
        self.assertTrue(res["ok"])
        # Garante que não foi sobrescrito
        self.assertEqual(custom_memory.read_text(encoding="utf-8"), "# Memória Customizada Prévia")

    def test_dry_run_mode(self):
        installer = ProjectInstaller(kit_dir=self.kit_dir)
        res = installer.install_project(self.project_dir, use_symlinks=True, dry_run=True)
        self.assertTrue(res["ok"])
        # Nenhum arquivo deve ter sido gravado
        self.assertFalse((self.project_dir / ".agents").exists())
        self.assertFalse((self.project_dir / "AGENTS.md").exists())


class TestKitDoctor(unittest.TestCase):
    """AC-6 & AC-2: Diagnóstico e auditoria do ambiente com agy-kit doctor."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.home_dir = Path(self.temp_dir) / "home"
        self.home_dir.mkdir()
        self.kit_dir = self.home_dir / "xp-kit"
        self.kit_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_doctor_diagnostics_report(self):
        doctor = KitDoctor(kit_dir=self.kit_dir, home_dir=self.home_dir)
        report = doctor.run_diagnostics()
        self.assertIn("python", report)
        self.assertIn("git", report)
        self.assertIn("antigravity_dirs", report)
        self.assertIn("path_ok", report)


class TestCliMainParser(unittest.TestCase):
    """AC-3 & AC-4: Argumentos da CLI e modos interativo e não-interativo."""

    @patch("scripts.kit_installer.GlobalInstaller.install_global")
    @patch("scripts.kit_installer.DependencyChecker.check_all")
    def test_cli_global_flag(self, mock_check, mock_global):
        mock_check.return_value = {"can_proceed": True, "checks": {}}
        mock_global.return_value = {"ok": True}
        exit_code = main(["--global", "--yes"])
        self.assertEqual(exit_code, 0)
        mock_global.assert_called_once()

    @patch("scripts.kit_installer.ProjectInstaller.install_project")
    @patch("scripts.kit_installer.DependencyChecker.check_all")
    def test_cli_project_flag(self, mock_check, mock_project):
        mock_check.return_value = {"can_proceed": True, "checks": {}}
        mock_project.return_value = {"ok": True}
        exit_code = main(["--project", "/tmp/sample", "--yes"])
        self.assertEqual(exit_code, 0)
        mock_project.assert_called_once()

    @patch("scripts.kit_installer.KitDoctor.run_diagnostics")
    def test_cli_doctor_flag(self, mock_diag):
        mock_diag.return_value = {
            "python": {"ok": True, "message": "Python 3.10"},
            "git": {"ok": True, "message": "Git 2.40"},
            "antigravity_dirs": {"ok": True, "message": "All found"},
            "path_ok": True,
        }
        exit_code = main(["doctor"])
        self.assertEqual(exit_code, 0)
        mock_diag.assert_called_once()

    @patch("scripts.kit_installer.CodeReviewGraphInstaller.install")
    def test_cli_install_graph_flag(self, mock_install):
        mock_install.return_value = {"ok": True, "path": "/bin/code-review-graph"}
        exit_code = main(["--install-graph"])
        self.assertEqual(exit_code, 0)
        mock_install.assert_called_once()


class TestOpenDesignInstaller(unittest.TestCase):
    """Testes para instalação e vinculação do OpenDesign (od)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.home_dir = Path(self.temp_dir) / "home"
        self.home_dir.mkdir()
        self.bin_dir = self.home_dir / ".local" / "bin"
        self.bin_dir.mkdir(parents=True)
        self.od_dir = self.home_dir / ".local" / "share" / "open-design"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_link_existing_opendesign(self):
        from scripts.kit_installer import OpenDesignInstaller
        # Cria arquivo od.mjs simulado
        daemon_bin = self.od_dir / "apps" / "daemon" / "bin"
        daemon_bin.mkdir(parents=True)
        od_script = daemon_bin / "od.mjs"
        od_script.write_text("#!/usr/bin/env node\nconsole.log('od v0.23.1');\n", encoding="utf-8")

        installer = OpenDesignInstaller(home_dir=self.home_dir)
        res = installer.install()
        self.assertTrue(res["ok"])
        target_link = self.bin_dir / "od"
        self.assertTrue(target_link.exists() or target_link.is_symlink())

    @patch("subprocess.run")
    def test_clone_and_install_opendesign(self, mock_run):
        from scripts.kit_installer import OpenDesignInstaller
        mock_run.return_value = MagicMock(returncode=0)

        installer = OpenDesignInstaller(home_dir=self.home_dir)
        # Mock do método de criação para simular criação do od.mjs após clone
        def fake_clone(*args, **kwargs):
            daemon_bin = self.od_dir / "apps" / "daemon" / "bin"
            daemon_bin.mkdir(parents=True, exist_ok=True)
            od_script = daemon_bin / "od.mjs"
            od_script.write_text("#!/usr/bin/env node\n", encoding="utf-8")
            return MagicMock(returncode=0)

        with patch("shutil.which", return_value="/usr/bin/git"):
            with patch.object(installer, "_run_clone_or_copy", side_effect=fake_clone):
                res = installer.install()
                self.assertTrue(res["ok"])
                self.assertTrue((self.bin_dir / "od").exists() or (self.bin_dir / "od").is_symlink())


class TestMcpConfigurator(unittest.TestCase):
    """Testes para auto-aprovação e configuração irrestrita de permissões MCP."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.home_dir = Path(self.temp_dir) / "home"
        self.home_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_configure_mcp_permissions_and_servers(self):
        from scripts.kit_installer import McpConfigurator
        configurator = McpConfigurator(home_dir=self.home_dir)
        res = configurator.configure_all()
        self.assertTrue(res["ok"])

        # Verifica se settings.json foi gerado com auto_approve
        settings_path = self.home_dir / ".gemini" / "config" / "settings.json"
        self.assertTrue(settings_path.exists())
        import json
        settings_data = json.loads(settings_path.read_text(encoding="utf-8"))
        self.assertEqual(settings_data.get("approval_mode"), "auto")
        self.assertTrue(settings_data.get("auto_approve"))
        self.assertTrue(settings_data.get("auto_approve_mcp"))
        self.assertEqual(settings_data.get("permissions", {}).get("call_mcp_tool"), "allow")

        # Verifica mcp_config.json
        mcp_cfg_path = self.home_dir / ".gemini" / "config" / "mcp_config.json"
        self.assertTrue(mcp_cfg_path.exists())
        mcp_data = json.loads(mcp_cfg_path.read_text(encoding="utf-8"))
        self.assertIn("open-design", mcp_data.get("mcpServers", {}))
        self.assertEqual(
            mcp_data["mcpServers"]["open-design"].get("args"),
            ["mcp", "--daemon-url", "http://127.0.0.1:7456"],
        )
        self.assertNotIn("autoApprove", mcp_data["mcpServers"]["open-design"])

        # Verifica code-review-graph em mcp_config.json
        self.assertIn("code-review-graph", mcp_data.get("mcpServers", {}))
        self.assertEqual(
            mcp_data["mcpServers"]["code-review-graph"].get("args"),
            ["serve"],
        )
        self.assertIn("CRG_TOOLS", mcp_data["mcpServers"]["code-review-graph"].get("env", {}))
        self.assertNotIn("autoApprove", mcp_data["mcpServers"]["code-review-graph"])


class TestCodeReviewGraphInstaller(unittest.TestCase):
    """Testes para instalação e vinculação do CodeReviewGraph (crg/agy-graph)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.home_dir = Path(self.temp_dir) / "home"
        self.home_dir.mkdir()
        self.bin_dir = self.home_dir / ".local" / "bin"
        self.bin_dir.mkdir(parents=True)
        self.crg_dir = self.home_dir / ".local" / "share" / "code-review-graph"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_link_existing_graph(self):
        from scripts.kit_installer import CodeReviewGraphInstaller
        venv_bin = self.crg_dir / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        crg_bin = venv_bin / "code-review-graph"
        crg_bin.write_text("#!/usr/bin/env python3\nprint('crg v2.3.9');\n", encoding="utf-8")
        crg_bin.chmod(0o755)

        installer = CodeReviewGraphInstaller(home_dir=self.home_dir)
        res = installer.install()
        self.assertTrue(res["ok"])
        target_link = self.bin_dir / "code-review-graph"
        self.assertTrue(target_link.exists() or target_link.is_symlink())
        self.assertTrue((self.bin_dir / "agy-graph").exists() or (self.bin_dir / "agy-graph").is_symlink())
        self.assertTrue((self.bin_dir / "agy-crg").exists() or (self.bin_dir / "agy-crg").is_symlink())

    @patch("subprocess.run")
    def test_clone_and_install_graph(self, mock_run):
        from scripts.kit_installer import CodeReviewGraphInstaller
        mock_run.return_value = MagicMock(returncode=0)

        installer = CodeReviewGraphInstaller(home_dir=self.home_dir)

        def fake_clone(*args, **kwargs):
            venv_bin = self.crg_dir / ".venv" / "bin"
            venv_bin.mkdir(parents=True, exist_ok=True)
            crg_bin = venv_bin / "code-review-graph"
            crg_bin.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
            crg_bin.chmod(0o755)
            return MagicMock(returncode=0)

        with patch("shutil.which", return_value="/usr/bin/git"):
            with patch.object(installer, "_run_clone_or_copy", side_effect=fake_clone):
                with patch.object(installer, "_setup_venv_and_install", return_value=True):
                    venv_bin = self.crg_dir / ".venv" / "bin"
                    venv_bin.mkdir(parents=True, exist_ok=True)
                    crg_bin = venv_bin / "code-review-graph"
                    crg_bin.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
                    crg_bin.chmod(0o755)

                    res = installer.install()
                    self.assertTrue(res["ok"])
                    self.assertTrue((self.bin_dir / "code-review-graph").exists() or (self.bin_dir / "code-review-graph").is_symlink())


if __name__ == "__main__":
    unittest.main()
