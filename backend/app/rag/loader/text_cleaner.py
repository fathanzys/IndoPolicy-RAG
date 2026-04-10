import re


class TextCleaner:
    """
    Membersihkan dan menormalisasi teks
    agar siap diproses oleh chunking & embedding.
    """

    @staticmethod
    def clean(text: str) -> str:
        # Hilangkan whitespace berlebih
        text = re.sub(r"\s+", " ", text)

        # Hilangkan karakter non-printable
        text = re.sub(r"[^\x20-\x7E]", " ", text)

        # Strip spasi di awal & akhir
        text = text.strip()

        return text
