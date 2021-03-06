import tensorflow as tf
import tensorflow_datasets as tfds
from . import ColBERTDataset, StackOverflowDataset, T2TDataset, RentTheRunwayDataset, ClickbaitDataset

class DatasetWrapper():
    def __init__(self, name: str, task: str, output_size: int=None):
        self.name = name
        self.task = task
        self.output_size = output_size
        self.strategy = tf.distribute.MultiWorkerMirroredStrategy()
        self.options = tf.data.Options()
        self.options.experimental_distribute.auto_shard_policy = tf.data.experimental.AutoShardPolicy.DATA

    def getTask(self):
        return self.task

    def getOutputSize(self):
        if self.output_size > 2:
            return self.output_size
        else:
            return 1

    def getData(self, batch_size: int, train_ratio: int=0.83):
        print('Num Replicas In Sync: ', self.strategy.num_replicas_in_sync)

        if self.task == 'classification':
            ds = tfds.load(self.name, split='train', as_supervised=True)
            if self.output_size > 2:
                ds = ds.map(lambda x, y: (x, tf.one_hot(tf.cast(y, tf.int32), self.output_size)))

            train_data = ds.take(int(len(ds) * train_ratio))\
                        .shuffle(1000)\
                        .batch(batch_size)
            test_data = ds.skip(int(len(ds) * train_ratio))\
                        .batch(batch_size)
        if self.task == 'regression':
            ds = tfds.load(self.name, split='train', as_supervised=True)
            train_data = ds.take(int(len(ds) * train_ratio))\
                        .shuffle(1000)\
                        .batch(batch_size)
            test_data = ds.skip(int(len(ds) * train_ratio))\
                        .batch(batch_size)
        if self.task == 'mlm':
            train_data = tfds.load(self.name, split='train')\
                        .shuffle(1000)
            test_data = None

        train_data = train_data.with_options(self.options)
        if test_data is not None:
            test_data = test_data.with_options(self.options)
        return train_data, test_data


dataset = {
    'colbert': DatasetWrapper('ColBERTDataset', 'classification', 2),
    'clickbait': DatasetWrapper('ClickbaitDataset', 'classification', 2),
    'stackoverflow': DatasetWrapper('StackOverflowDataset', 'classification', 20),
    'agnews': DatasetWrapper('ag_news_subset', 'classification', 4),
    't2t': DatasetWrapper('T2TDataset', 'mlm'),
    'rentrunway': DatasetWrapper('RentTheRunwayDataset', 'regression'),
}

def list_dataset():
    return dataset.keys()

def get_dataset(name: str):
    return dataset[name]
