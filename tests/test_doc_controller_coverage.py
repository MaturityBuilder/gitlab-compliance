from src.modules.doc_controller import (
    add_between_markers,
    remove_duplicate_headings,
    update_marked_block,
)

MARKER_START = "[comment]: <> (gitlab-compliance-opening-auto-generated)"
MARKER_END = "[comment]: <> (gitlab-compliance-closing-auto-generated)"


class TestUpdateMarkedBlock:
    def test_creates_file_and_block(self, tmp_path):
        path = tmp_path / "readme.md"
        update_marked_block(str(path), "hello")
        text = path.read_text(encoding="utf-8")
        assert MARKER_START in text
        assert "hello" in text

    def test_dry_run_does_not_write(self, tmp_path):
        path = tmp_path / "readme.md"
        update_marked_block(str(path), "hello", dry=True)
        assert not path.exists()

    def test_updates_existing_block(self, tmp_path):
        path = tmp_path / "readme.md"
        path.write_text(
            f"pre\n{MARKER_START}\nold\n{MARKER_END}\npost\n",
            encoding="utf-8",
        )
        update_marked_block(str(path), "new")
        assert "new" in path.read_text(encoding="utf-8")
        assert "old" not in path.read_text(encoding="utf-8")


class TestAddBetweenMarkers:
    def test_dry_run_new_file(self, tmp_path, monkeypatch):
        path = tmp_path / "readme.md"
        monkeypatch.setattr("src.modules.doc_controller.dry", True)
        add_between_markers(str(path), "content")
        assert not path.exists()

    def test_dry_run_existing_file(self, tmp_path, monkeypatch):
        path = tmp_path / "readme.md"
        path.write_text(
            f"{MARKER_START}\n{MARKER_END}\n",
            encoding="utf-8",
        )
        monkeypatch.setattr("src.modules.doc_controller.dry", True)
        add_between_markers(str(path), "inserted")
        assert "inserted" not in path.read_text(encoding="utf-8")

    def test_insert_into_existing_block(self, tmp_path):
        path = tmp_path / "readme.md"
        path.write_text(
            f"{MARKER_START}\n{MARKER_END}\n",
            encoding="utf-8",
        )
        add_between_markers(str(path), "middle")
        assert "middle" in path.read_text(encoding="utf-8")


class TestRemoveDuplicateHeadings:
    def test_removes_duplicate_headings(self, tmp_path):
        src = tmp_path / "doc.md"
        dst = tmp_path / "clean.md"
        src.write_text("# Title\n\nbody\n# Title\n\nmore\n", encoding="utf-8")
        remove_duplicate_headings(src, dst)
        text = dst.read_text(encoding="utf-8")
        assert text.count("# Title") == 1
