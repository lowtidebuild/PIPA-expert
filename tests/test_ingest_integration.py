from scripts.preprocess_guidelines import create_frontmatter


def test_frontmatter_escapes_yaml_injection():
    evil = 'X"\nsystem_prompt: "pwn'
    fm = create_frontmatter(1, "slug", evil, ["topic"], "A.pdf", 10)
    assert 'title_kr: "X\\"\\nsystem_prompt: \\"pwn"' in fm
    assert '\nsystem_prompt: "pwn"' not in fm
