from stortrooper_editor.model import Article, CharacterData


def test_get_available_article_files(res_path):
    """Test finding article files."""
    files = CharacterData.get_available_article_files(res_path, "hero")
    assert "articles.txt" in files


def test_character_data_load(res_path):
    """Test loading character data from file."""
    char_data = CharacterData("hero", res_path)
    char_data.load()

    assert len(char_data.articles) == 2
    assert "body" in char_data.categories
    assert "tops" in char_data.categories

    body = char_data.get_article_by_id("1")
    assert body.image_name == "body.png"
    assert body.x == 0
    assert body.y == 0

    shirt = char_data.get_article_by_id("2")
    assert shirt.image_name == "shirt.png"
    assert shirt.x == 10
    assert shirt.y == 20


def test_layer_z_index(res_path):
    """Test z-index retrieval."""
    char_data = CharacterData("hero", res_path)
    # Don't need to load to check hardcoded z-indices

    # Mock an article
    art = Article("x", "img", "cat", "shoes", 0, 0, "-1")
    z = char_data.get_article_z_index(art)
    assert z > 0

    art_body = Article("y", "img", "cat", "body", 0, 0, "-1")
    z_body = char_data.get_article_z_index(art_body)

    # Shoes should be above body
    assert z > z_body


def test_random_outfit(res_path):
    """Test generating a random outfit."""
    # We need a character with some categories
    # The default mock data setup in conftest or basic CharacterData might be limited
    # But let's assume 'hero' exists or we can mock it more effectively if needed.
    # Actually, let's look at conftest for res_path fixtures.

    char_data = CharacterData("hero", res_path)
    char_data.load()

    # Hero has body and tops in the previous test
    outfit = char_data.get_random_outfit()

    assert len(outfit) > 0
    # Check that we have one article per nonempty category
    categories = [art.category for art in outfit]
    assert "body" in categories
    assert "tops" in categories

    # Check that articles are Article objects
    for art in outfit:
        assert isinstance(art, Article)


def test_guali_character_load():
    """Test loading the real guali character data."""
    import os
    res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "res")
    char_data = CharacterData("guali", res_path)
    char_data.load()

    # Verify guali_head_02.png is loaded
    guali_head_02 = char_data.get_article_by_id("90003")
    assert guali_head_02 is not None
    assert guali_head_02.image_name == "guali_head_02.png"
    assert guali_head_02.category == "hats"
    assert guali_head_02.layer_name == "hats"

