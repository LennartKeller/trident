from multiprocessing import cpu_count
from typing import Optional

from datasets.load import load_dataset, load_dataset_builder

from src.datamodules.base import BaseDataModule


class PAWSDataModule(BaseDataModule):
    def __init__(
        self, subset: str = "labeled_final", *args, **kwargs,
    ):
        # see BaseDataModule
        super().__init__(*args, **kwargs)

        self.subset: str = subset

    def prepare_data(self):
        """
        Download MNLI from Huggingface datasets hub.
        See: https://huggingface.co/datasets/glue
        """
        # download with Huggingface datasets
        dataset = load_dataset_builder("paws")
        dataset.download_and_prepare()

    @staticmethod
    def preprocess(example):
        """
        Preprocess HF dataset to generically match HF tokenizers and other required preprocessing functions.

        Preprocess HF dataset to 
            1) such that input matches collators generically (`text`, `text_pair`)
            2) strip whitespace of examples as some instances have leading/trailing whitespaces
            3) convert label to type int

        :param example dict: example of Huggingface dataset
        """
        example["text"] = example.pop("sentence1").strip()
        example["text_pair"] = example.pop("sentence2").strip()
        example["labels"] = int(example.pop("label"))
        return example

    def setup(self, stage: Optional[str] = None):
        if stage == "fit":
            dataset = load_dataset("paws", self.subset).map(
                self.preprocess, num_proc=cpu_count()
            )
            self.data_train = dataset["train"]
            self.data_val = dataset["validation"]
        if stage == "test":
            dataset = load_dataset("paws", self.subset, split="test").map(preprocess)
            self.data_test = dataset