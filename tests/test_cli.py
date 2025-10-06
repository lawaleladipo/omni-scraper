from omni_scraper.cli import create_parser

def test_cli_parser_creation():
    parser = create_parser()
    assert parser is not None
    assert hasattr(parser, 'parse_args')
