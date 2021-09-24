from multiprocessing import cpu_count
from typing import Optional

from datasets.arrow_dataset import concatenate_datasets
from datasets.load import load_dataset, load_dataset_builder

from src.datamodules.base import BaseDataModule


class MNLIDataModule(BaseDataModule):
    def __init__(
        self, *args, **kwargs,
    ):
        # see BaseDataModule
        super().__init__(*args, **kwargs)

    @staticmethod
    def prepare_data():
        """
        Download MNLI from Huggingface datasets hub.
        See: https://huggingface.co/datasets/glue
        """
        # download with Huggingface datasets
        dataset = load_dataset_builder("glue", "mnli")
        dataset.download_and_prepare()

    # @staticmethod
    def preprocess(self, example):
        """
        Preprocess HF dataset to generically match HF tokenizers and other required preprocessing functions.

        Preprocess HF dataset to 
            1) such that input matches collators generically (`text`, `text_pair`)
            2) strip whitespace of examples as some instances have leading/trailing whitespaces

        :param example dict: example of Huggingface dataset
        """
        example["text"] = example.pop("premise").strip()
        example["text_pair"] = example.pop("hypothesis").strip()
        return example

    def setup(self, stage: Optional[str] = None):
        if stage == "fit":
            dataset = load_dataset("glue", "mnli")
            # TODO possibly switch to pandas as it's faster and produces no wall of output 
            # preprocess dataset multithreaded
            dataset = dataset.map(self.preprocess, num_proc=cpu_count())
            self.data_train = dataset["train"]
            self.data_val = concatenate_datasets(
                [dataset["validation_mismatched"], dataset["validation_matched"]]
            )
            self.data_test = self.data_val
            # self.data_test = concatenate_datasets(
            #     [dataset["test_mismatched"], dataset["test_matched"]]
            # )