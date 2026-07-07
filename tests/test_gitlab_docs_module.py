import src.gitlab_docs as gitlab_docs


class TestGitlabDocsModule:
    def test_getattr_reexports_cli_symbols(self):
        assert gitlab_docs.check is not None
        assert gitlab_docs.policies is not None

    def test_dir_includes_reexported_and_dynamic_names(self):
        names = gitlab_docs.__dir__()
        assert "check" in names
        assert "run_compliance" in names
        assert "build_policy_catalog" in names
