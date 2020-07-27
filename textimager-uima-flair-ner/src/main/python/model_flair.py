import logging
from pathlib import Path
from typing import List

import torch
from flair.data import Sentence
from flair.datasets import SentenceDataset
from flair.models import SequenceTagger
from flair.tokenization import SegtokTokenizer

torch.device('cpu')
log = logging.getLogger("flair")


class BaseModel:
    def __init__(
            self,
            path: str,
            mini_batch_size=32,
            embedding_storage_mode: str = "none",
            verbose: bool = False,
    ):
        self.tagger: SequenceTagger = SequenceTagger.load(Path(path))
        log.info("loaded model")
        self.mini_batch_size = mini_batch_size
        self.embedding_storage_mode = embedding_storage_mode
        self.verbose = verbose

    def _predict(self, sentences):
        tokenizer = SegtokTokenizer()
        dataset = SentenceDataset([Sentence(text, tokenizer) for text in sentences])
        self.tagger.predict(
            dataset,
            mini_batch_size=self.mini_batch_size,
            embedding_storage_mode=self.embedding_storage_mode,
            verbose=self.verbose
        )
        return [sentence for sentence in dataset]


class SpanModel(BaseModel):
    def tag(self, sentences, offsets) -> List[List[str]]:
        output = self._predict(sentences)

        annotations: List[List[str]] = []
        for i, offset in enumerate(offsets):
            output_sentence: Sentence = output[i]

            for span in output_sentence.get_spans(self.tagger.tag_type):
                tag, begin, end = span.tag, str(offset + span.start_pos), str(offset + span.end_pos)
                annotations.append([tag, begin, end])

        return annotations


class TokenModel(BaseModel):
    def tag(self, sentences, offsets) -> List[List[str]]:
        output = self._predict(sentences)

        annotations: List[List[str]] = []
        for i, offset in enumerate(offsets):
            output_sentence: Sentence = output[i]

            for token in output_sentence.tokens:
                token.tags_proba_dist
                tag = token.get_tag(self.tagger.tag_type).value
                begin, end = str(offset + token.start_position), str(offset + token.end_position)
                annotations.append([tag, begin, end])

        return annotations