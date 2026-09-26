# REPO MAP — XP Multi-Agent Kit (Símbolos & Estrutura)
> Mapa gerado automaticamente pelo `agy-repo-map`. Consulte antes de buscar arquivos.

### / (raiz)
- `AGENTS.md`
- `README.md`

### docs/
- `universal-token-reduction-guide.md`

### scripts/
- `agy-audit-config`
- `agy-compact`
- `agy-effort`
- `agy-git-ops`
- `agy-handoff`
- `agy-health`
- `agy-init-memory`
- `agy-memory-archive`
- `agy-repo-map`
- `agy-sanitize`
- `agy-worktree`
- `agy_effort_router.py` [class EffortDecision, def get_cli_settings_path(), def get_current_settings_effort()]
- `agy_health.py` [def check_plugin_directories(), def check_memory_health(), def evaluate_quota_health()]
- `apply_ignore_rules.py` [def get_template_content(), def discover_all_project_directories(), def apply_ignore_to_directory()]
- `ci_healer.py` [def can_attempt_next(), def is_limit_exceeded(), def clean_ansi()]
- `context_compactor.py` [def strip_ansi_codes(), def compress_whitespace(), def compress_logs()]
- `git_worktree_manager.py` [def sanitize_branch_name(), def get_repo_root(), def create_worktree()]
- `install-global.sh`
- `memory_archiver.py` [def parse_episodic_entries(), def split_memory_sections(), def archive_memory()]
- `repo_map.py` [def load_symbol_cache(), def save_symbol_cache(), def extract_python_symbols()]
- `sanitize-tool-output.sh`
- `token_tracker.py` [def get_model_display_name(), def get_provider_defaults(), def make_progress_bar()]

### scripts/global-token-optimizer/
- `agy-wrapper.sh`
- `install-shell-aliases.sh`

### scripts/hooks/
- `dynamic_effort_hook.py` [def clean_user_prompt(), def extract_conversation_context(), def extract_latest_user_prompt()]
- `post-push-watcher.sh`
- `smart-tool-optimizer.py` [def count_file_lines(), def detect_contiguous_read(), def optimize_view_file()]
- `smart_tool_optimizer.py` [def count_file_lines(), def detect_contiguous_read(), def optimize_view_file()]
- `token-badge-hook.py` [def main()]
- `tool-size-guard.py` [def process_tool_payload(), def main()]

### templates/
- `PROJECT_MEMORY_TEMPLATE.md`
- `universal.geminiignore`

### tests/
- `test_agy_audit_config.py` [class TestAgyAuditConfig(setUp, test_clean_config_reports_healthy, test_bloated_rules_detected, test_eager_mcp_detected)]
- `test_agy_effort_router.py` [class TestAgyEffortRouter(test_classify_l0_trivial_prompts, test_classify_l1_small_prompts, test_classify_l2_feature_prompts, test_classify_l3_critical_prompts)]
- `test_agy_git_ops.py` [class TestAgyGitOps(setUp, tearDown, test_help_command, test_status_command_clean)]
- `test_agy_handoff.py` [class TestAgyHandoff(setUp, test_handoff_output_format_and_compactness, test_handoff_file_generation)]
- `test_agy_health.py` [class TestAgyHealth(setUp, tearDown, test_check_plugin_directories_heals_when_missing, test_check_plugin_directories_ok_when_exists)]
- `test_agy_sanitize.py` [class TestAgySanitize(setUp, test_short_input_not_truncated, test_long_input_is_truncated, test_command_execution_success)]
- `test_apply_ignore_rules.py` [class TestApplyIgnoreRules(setUp, tearDown, test_get_template_content, test_apply_ignore_to_directory)]
- `test_ci_healer.py` [class TestCiHealer(setUp, test_module_importable, test_parse_gh_run_json, test_extract_error_snippet_from_log)]
- `test_context_compactor.py` [class TestContextCompactor(test_strip_ansi_codes, test_compress_whitespace, test_compress_logs_dedup_repeats, test_compress_diff_collapses_context)]
- `test_dynamic_effort_hook.py` [class TestDynamicEffortHook(setUp, tearDown, test_extract_latest_user_prompt, test_handle_pre_invocation_classifies_and_injects_step)]
- `test_git_worktree_manager.py` [class TestGitWorktreeManager(test_sanitize_branch_name, test_create_worktree_success, test_create_worktree_failure_raises, test_remove_worktree)]
- `test_memory_archiver.py` [class TestMemoryArchiver(setUp, tearDown, _generate_sample_memory, test_parse_episodic_entries)]
- `test_repo_map.py` [class TestRepoMap(setUp, tearDown, test_generate_repo_map_extracts_python_and_ts_symbols, test_repo_map_strictly_under_80_lines)]
- `test_smart_tool_optimizer.py` [class TestSmartToolOptimizer(setUp, tearDown, test_view_file_unbounded_large_file_is_clamped, test_view_file_small_file_is_unmodified)]
- `test_token_tracker.py` [class TestTokenTracker(test_estimate_tokens_empty, test_estimate_tokens_calibration, test_parse_token_limit, test_get_model_limits_known_models), class TestProviderDefaults(setUp, test_claude_defaults, test_claude_older, test_openai_gpt4o)]
- `test_tool_size_guard.py` [class TestToolSizeGuard(setUp, tearDown, test_process_payload_normal_size_no_flood, test_process_payload_exceeding_chars_triggers_flood_warning)]
