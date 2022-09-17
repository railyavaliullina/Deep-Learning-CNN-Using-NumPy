import numpy as np
from copy import deepcopy

from configs.mnist_config import cfg as mnist_cfg
from configs.cifar_config import cfg as cifar_cfg
from configs.config import cfg as initial_cfg
from utils.data_utils import get_data
from models.BaseModel import BaseModelClass
from utils.eval_utils import get_accuracy
from utils.log_utils import log_metrics, log_params, start_logging, end_logging


def run(cfg):
    net = BaseModelClass(cfg)

    # save to mlflow experiment name and experiment params
    start_logging(cfg, experiment_name='CNN_overfit_on_batch')
    log_params(cfg)

    losses = []
    acc_on_batches = []
    batch_generator_ = train_dl.batch_generator()
    batch = next(batch_generator_)
    for i in range(cfg["overfitting_on_batch"]["nb_iters"]):
        images, labels = batch
        images = np.expand_dims(np.stack(images), 1)  # .reshape((cfg['dataloader']['batch_size']['train'], -1))
        loss = net.make_step(images, labels)
        losses.append(loss)

        # log loss
        log_metrics(['loss'], [loss], i, cfg)

        # if i % 50 == 0:
        mean_loss = np.mean(losses)
        print(f'iteration: {i}, loss: {mean_loss}')
        # print(loss)

        # evaluate on batch
        acc_on_batch = get_accuracy(batch, dataset_cfg, net, on_batch=True)
        print(f'Accuracy on batch after iter {i}: {acc_on_batch}')

        # log accuracy
        log_metrics(['batch_accuracy'], [acc_on_batch], i, cfg)

        if acc_on_batch == 100:
            acc_on_batches.append(acc_on_batch)

        if len(acc_on_batches) >= 5:
            break


if __name__ == '__main__':
    dataset_cfg = cifar_cfg if initial_cfg["dataset"] == 'cifar' else mnist_cfg

    print(f'Current dataset: {initial_cfg["dataset"]}')
    train_dl = get_data(initial_cfg, dataset_type='train')
    test_dl = get_data(initial_cfg, dataset_type='test')

    run(initial_cfg)

    # for function_name, validation_func in initial_cfg['hyperparams_validation']['validation_functions'].items():
    #     print(f'\nValidation type: {function_name}')
    #     initial_cfg_ = deepcopy(initial_cfg)
    #     cfgs = validation_func(initial_cfg_)
    #     for name, cfg in cfgs.items():
    #         cfg_ = deepcopy(cfg)
    #         print(f'\n{name}')
    #         run(cfg_)
