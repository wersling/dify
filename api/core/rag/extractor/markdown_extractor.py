"""Abstract interface for document loader implementations."""

import re
from pathlib import Path
from typing import Optional, cast

from core.rag.extractor.extractor_base import BaseExtractor
from core.rag.extractor.helpers import detect_file_encodings
from core.rag.models.document import Document
import logging



class MarkdownExtractor(BaseExtractor):
    """Load Markdown files.


    Args:
        file_path: Path to the file to load.
    """

    def __init__(
        self,
        file_path: str,
        remove_hyperlinks: bool = False,
        remove_images: bool = False,
        encoding: Optional[str] = None,
        autodetect_encoding: bool = True,
    ):
        """Initialize with file path."""
        self._file_path = file_path
        self._remove_hyperlinks = remove_hyperlinks
        self._remove_images = remove_images
        self._encoding = encoding
        self._autodetect_encoding = autodetect_encoding

    def extract(self) -> list[Document]:
        """Load from file path."""
        tups = self.parse_tups(self._file_path)
        documents = []
        for header, value in tups:
            value = value.strip()
            if header is None:
                documents.append(Document(page_content=value))
            else:
                documents.append(Document(page_content=f"\n\n{header}\n{value}"))

        return documents

    def markdown_to_tups(self, markdown_text: str) -> list[tuple[Optional[str], str]]:
        """Convert a markdown file to a dictionary.

        The keys are the headers and the values are the text under each header.

        """

        logging.info(f"markdown_to_tups2: {self._file_path}")
        
        markdown_tups: list[tuple[Optional[str], str]] = []
        markdown_text = re.sub(r'\n{2,}', '\n', markdown_text) # 将连续的换行符替换为单个换行符
        lines = markdown_text.split("\n")

        current_header = None
        current_text = ""
        code_block_flag = False

        for line in lines:
            if line.startswith("```"):
                code_block_flag = not code_block_flag
                current_text += line + "\n"
                continue
            if code_block_flag:
                current_text += line + "\n"
                continue
            header_match = re.match(r"^#{1,3}\s", line) # 只解析低于3级的标题

            if header_match:
                if current_header is not None:
                    markdown_tups.append((current_header, current_text))

                current_header = line
                current_text = ""
            else:
                current_text += line + "\n"
        markdown_tups.append((current_header, current_text))

        if current_header is not None:
            # pass linting, assert keys are defined
            markdown_tups = [
                (re.sub(r"#", "", cast(str, key)).strip(), re.sub(r"<.*?>", "", value)) for key, value in markdown_tups
            ]
        else:
            markdown_tups = [(key, re.sub("\n", "", value)) for key, value in markdown_tups]

        return markdown_tups

    def remove_images(self, content: str) -> str:
        """Get a dictionary of a markdown file from its path."""
        pattern = r"!{1}\[\[(.*)\]\]"
        content = re.sub(pattern, "", content)
        return content

    def remove_hyperlinks(self, content: str) -> str:
        """Get a dictionary of a markdown file from its path."""
        pattern = r"\[(.*?)\]\((.*?)\)"
        content = re.sub(pattern, r"\1", content)
        return content

    def parse_tups(self, filepath: str) -> list[tuple[Optional[str], str]]:
        """Parse file into tuples."""
        content = ""
        try:
            content = Path(filepath).read_text(encoding=self._encoding)
        except UnicodeDecodeError as e:
            if self._autodetect_encoding:
                detected_encodings = detect_file_encodings(filepath)
                for encoding in detected_encodings:
                    try:
                        content = Path(filepath).read_text(encoding=encoding.encoding)
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {filepath}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading {filepath}") from e

        if self._remove_hyperlinks:
            content = self.remove_hyperlinks(content)

        if self._remove_images:
            content = self.remove_images(content)

        return self.markdown_to_tups(content)
