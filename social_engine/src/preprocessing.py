"""
Social-Media-Aware Text Preprocessing Module
Social Engine NLP Semantic Understanding Layer
"""

import re
import html
import unicodedata
import sys
import pandas as pd

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except Exception:
        pass
if sys.stderr is not None:
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')
    except Exception:
        pass

class SocialTextPreprocessor:
    """
    Production preprocessing pipeline tailored specifically for noisy social media text.
    Preserves sentiment signals, punctuation emphasis, and conversational structure
    while resolving encoding corruption, HTML artifacts, and elongation noise.
    """
    def __init__(self, normalize_mentions=True, normalize_urls=True, unpack_hashtags=True, max_repeated_chars=2):
        self.normalize_mentions = normalize_mentions
        self.normalize_urls = normalize_urls
        self.unpack_hashtags = unpack_hashtags
        self.max_repeated_chars = max_repeated_chars
        
        # Precompiled regex patterns for high-throughput batch execution
        self.url_regex = re.compile(r'https?://\S+|www\.\S+')
        self.mention_regex = re.compile(r'@\w+')
        self.hashtag_regex = re.compile(r'#(\w+)')
        self.escaped_unicode_regex = re.compile(r'(\\u[0-9a-fA-F]{4}|u2019|u2018|u201c|u201d)')
        self.repeated_char_regex = re.compile(r'(.)\1{2,}')
        self.whitespace_regex = re.compile(r'\s+')
        
        # Unicode replacement lookup
        self.unicode_replacements = {
            r'\u2019': "'",
            r'u2019': "'",
            r'\u2018': "'",
            r'u2018': "'",
            r'\u201c': '"',
            r'u201c': '"',
            r'\u201d': '"',
            r'u201d': '"',
            r'\u2014': " - ",
            r'\u2013': " - ",
            r'\u2026': "...",
            r'&amp;': '&',
            r'&lt;': '<',
            r'&gt;': '>',
            r'&quot;': '"',
            r'&#39;': "'",
        }

    def decode_corrupted_unicode(self, text: str) -> str:
        """Fixes escaped unicode characters such as literal \\u2019, u2019, and HTML entities."""
        if not isinstance(text, str):
            return ""
            
        # 1. HTML unescape
        text = html.unescape(text)
        
        # 2. Known raw escaped sequences
        for corrupt, clean in self.unicode_replacements.items():
            text = text.replace(corrupt, clean)
            
        # 3. Generic unicode escape decode if present
        if '\\u' in text:
            try:
                text = text.encode('utf-8').decode('unicode_escape')
            except Exception:
                pass
                
        # 4. Normalize unicode characters (NFKC)
        text = unicodedata.normalize('NFKC', text)
        return text

    def clean_text(self, text: str) -> str:
        """
        Executes full social-media cleaning pipeline.
        Guarantees preservation of sentiment-carrying tokens, casing, and emoticons.
        """
        if not isinstance(text, str):
            return ""
            
        # 1. Decode corruptions & entities
        text = self.decode_corrupted_unicode(text)
        
        # 2. Normalize URLs
        if self.normalize_urls:
            text = self.url_regex.sub('http://url', text)
            
        # 3. Normalize User Mentions
        if self.normalize_mentions:
            text = self.mention_regex.sub('@user', text)
            
        # 4. Handle Hashtags (unpack e.g. #AccountSecurity -> AccountSecurity while keeping semantic token)
        if self.unpack_hashtags:
            # Replace '#Topic' with 'Topic' so downstream tokenizers and embeddings treat it as a semantic word
            text = self.hashtag_regex.sub(r'\1', text)
            
        # 5. Compress elongated characters (e.g., 'sooooo' -> 'soo', 'loooove' -> 'loove')
        if self.max_repeated_chars:
            text = self.repeated_char_regex.sub(r'\1' * self.max_repeated_chars, text)
            
        # 6. Normalize whitespace
        text = self.whitespace_regex.sub(' ', text).strip()
        
        # 7. Strip extraneous surrounding quotation marks from raw CSV dumps (e.g. '""text""')
        if (text.startswith('""') and text.endswith('""')) or (text.startswith('"') and text.endswith('"')):
            text = text.strip('"')
            
        return text

def preprocess_dataframe(df: pd.DataFrame, text_col: str = 'post_text') -> pd.DataFrame:
    """
    Creates raw_text and cleaned_text columns without modifying the original dataframe in-place.
    """
    df_out = df.copy()
    preprocessor = SocialTextPreprocessor()
    df_out['raw_text'] = df_out[text_col]
    df_out['cleaned_text'] = df_out[text_col].apply(preprocessor.clean_text)
    return df_out

if __name__ == '__main__':
    # Test cases demonstrating preservation and cleaning
    test_cases = [
        "Lakers vs Heat on Jan. 17th! It\\u2019s D Wade\\u2019s b day... I feel bad he\\u2019ll lose on his birthday lololol",
        "He is my 1st love in KPOP &amp; it's not changing til now",
        "@user @user aaaah. Nokia used to make the Best Phone Cameras Ever. Sadly I think those days may be past.",
        "Check out https://t.co/xyz123 for #AccountSecurity updates! AMAZING!!! 😭🔥",
        "\"\"who is 1d?\"\"\""
    ]
    preprocessor = SocialTextPreprocessor()
    print("--- Preprocessing Verification Samples ---")
    for raw in test_cases:
        print(f"RAW    : {raw}")
        print(f"CLEANED: {preprocessor.clean_text(raw)}")
        print("-" * 50)
