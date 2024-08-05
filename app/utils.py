from flask import Markup

def convert_to_paragraphs(text_content):
    """Convert single line breaks to HTML paragraphs"""
    # Split by single newline for paragraphs
    paragraphs = text_content.split('\n')
    # Wrap each paragraph with <p> tags and join them
    paragraph_content = ''.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())
    return Markup(paragraph_content)
