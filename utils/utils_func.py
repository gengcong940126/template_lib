import importlib
import shutil
from easydict import EasyDict
import numpy as np
import os
import sys
import re
import logging
from numpy import array_equal
import yaml
import json
import time
import traceback

colors_dict = {
      'blue': '#2B99F0',
      'red': '#FE2224',
      'dark_red': '#FF0000',
      'pink': '#FD4BD7',
      'green': '#17CE11',
      'dark_green': '#17CE11',
      'blue_violet': '#7241BE',
      'black': '#020202',
      'grey': '#A6A6A6',
      'peach': '#FEAA92',
      'yellow': '#FEFF00',
      'purple': '#A40190',
      'beauty_green': '#33E69C',
      'beauty_blue': '#1F5CFA',
      'beauty_light_blue': '#0CE6DA',
      'beauty_red': '#F84D4D',
      'beauty_orange': '#FF743E',
    }

color_beauty_dict = {
  'orange': '#FF743E',
  'green': '#33E69C',
  'dark_green': '#17CE11',
  'red': '#F84D4D',
  'light_blue': '#0CE6DA',
  'blue': '#1F5CFA'
}


def get_filelist_recursive(directory, ext='*.png'):
  from pathlib import Path
  file_list = list(Path(directory).rglob(ext))
  return file_list


class MaxToKeep(object):
  def __init__(self, max_to_keep=None):
    self.max_to_keep = max_to_keep
    self.recent_checkpoints = []
    pass

  def step(self, file_path):
    if self.max_to_keep is not None:
      self.recent_checkpoints.append(file_path)
      if len(self.recent_checkpoints) > self.max_to_keep:
        file_to_delete = self.recent_checkpoints.pop(0)
        if os.path.exists(file_to_delete):
          if os.path.isdir(file_to_delete):
            shutil.rmtree(file_to_delete)
          else:
            os.remove(file_to_delete)
    pass

def make_zip(source_dir, output_filename):
  import zipfile
  zipf = zipfile.ZipFile(output_filename, 'w')
  pre_len = len(os.path.dirname(source_dir))
  for parent, dirnames, filenames in os.walk(source_dir):
    for filename in filenames:
      pathfile = os.path.join(parent, filename)
      arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
      zipf.write(pathfile, arcname)
  zipf.close()


def unzip_file(zip_file, dst_dir):
  import zipfile
  assert zipfile.is_zipfile(zip_file)

  fz = zipfile.ZipFile(zip_file, 'r')
  for file in fz.namelist():
    fz.extract(file, dst_dir)
  fz.close()
  print(f'Unzip {zip_file} to {dst_dir}')


def time2string(elapsed):
  """
  elapsed = time.time() - time_start
  """
  # hours, rem = divmod(elapsed, 3600)
  # minutes, seconds = divmod(rem, 60)
  # time_str = "{:0>2}h:{:0>2}m:{:05.2f}s".format(int(hours), int(minutes), seconds)
  time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
  return time_str


def print_exceptions():
  print(traceback.format_exc())


def array2string(array_np):
  array_str = np.array2string(array_np, threshold=np.inf)
  return array_str


def get_arc_from_file(arc_file, arc_idx, nrows=1, sep=' '):
  """
  0:
  [3 3 4 1 3 1 3 3 4 1 3 1 3 3 4 1 3 1]
  """
  if os.path.isfile(arc_file):
    print(f'Using arc_file: {arc_file}, \tarc_idx: {arc_idx}')
    with open(arc_file) as f:
      while True:
        epoch_str = f.readline().strip(': \n')
        sample_arc = []
        for _ in range(nrows):
          class_arc = f.readline().strip('[\n ]')
          sample_arc.append(np.fromstring(class_arc, dtype=int, sep=sep))
        if arc_idx == int(epoch_str):
          break
    sample_arc = np.array(sample_arc)
  else:
    raise NotImplemented
  print('fixed arcs: \n%s' % sample_arc)
  return sample_arc.squeeze()


class average_precision_score(object):
  @staticmethod
  def accuracy_score(y_true, y_pred, normalize=True):
    from sklearn.metrics import average_precision_score, precision_recall_curve, accuracy_score

    acc = accuracy_score(y_true, y_pred, normalize=normalize)
    return acc

  @staticmethod
  def average_precision_score(y_true, y_score):
    '''Compute average precision (AP) from prediction scores
    '''
    from sklearn.metrics import average_precision_score
    average_precision = average_precision_score(y_true, y_score)
    return average_precision


def _make_gen(reader):
  b = reader(1024 * 1024)
  while b:
    yield b
    b = reader(1024 * 1024)

def rawgencount(filename):
  "count num of lines of a file"
  f = open(filename, 'rb')
  f_gen = _make_gen(f.raw.read)
  n_lines = sum(buf.count(b'\n') for buf in f_gen)
  f.close()
  return n_lines


def array_eq_in_list(myarr, list_arrays):
  return next((True for elem in list_arrays if array_equal(elem, myarr)), False)


def top_accuracy(output, target, topk=(1,)):
  """ Computes the precision@k for the specified values of k """
  maxk = max(topk)
  batch_size = target.size(0)

  _, pred = output.topk(maxk, 1, True, True)
  pred = pred.t()
  # one-hot case
  if target.ndimension() > 1:
    target = target.max(1)[1]

  correct = pred.eq(target.view(1, -1).expand_as(pred))

  res = []
  for k in topk:
    correct_k = correct[:k].view(-1).float().sum(0)
    res.append(correct_k.mul_(1.0 / batch_size))
  return res


def topk_errors(preds, labels, ks):
  """Computes the top-k error for each k.
  top1_err, top5_err = self._topk_errors(preds, labels, [1, 5])
  """
  import torch
  err_str = "Batch dim of predictions and labels must match"
  assert preds.size(0) == labels.size(0), err_str
  # Find the top max_k predictions for each sample
  _top_max_k_vals, top_max_k_inds = torch.topk(
    preds, max(ks), dim=1, largest=True, sorted=True
  )
  # (batch_size, max_k) -> (max_k, batch_size)
  top_max_k_inds = top_max_k_inds.t()
  # (batch_size, ) -> (max_k, batch_size)
  rep_max_k_labels = labels.view(1, -1).expand_as(top_max_k_inds)
  # (i, j) = 1 if top i-th prediction for the j-th sample is correct
  top_max_k_correct = top_max_k_inds.eq(rep_max_k_labels)
  # Compute the number of topk correct predictions for each k
  topks_correct = [top_max_k_correct[:k, :].view(-1).float().sum() for k in ks]
  return [(1.0 - x / preds.size(0)) * 100.0 for x in topks_correct]

class AverageMeter():
  """ Computes and stores the average and current value """

  def __init__(self):
    self.reset()

  def reset(self):
    """ Reset all statistics """
    self.val = 0
    self.avg = 0
    self.sum = 0
    self.count = 0

  def update(self, val, n=1):
    """ Update statistics """
    self.val = val
    self.sum += val * n
    self.count += n
    self.avg = self.sum / self.count


def print_number_params(models_dict, logger=None):
  if logger is None:
    logger = logging.getLogger('tl')
  for label, model in models_dict.items():
    if model is None:
      logger.info(f'Number of params in {label}:\t 0M')
    else:
      logger.info('Number of params in {}:\t {}M'.format(
        label, sum([p.data.nelement() for p in model.parameters()])/1e6
      ))


def get_ddp_attr(obj, attr=None, **kwargs):
  if attr is None:
    return getattr(obj, 'module', obj)
  return getattr(getattr(obj, 'module', obj), attr, **kwargs)


def get_ddp_module(model):
  import torch
  from torch.nn.parallel import DistributedDataParallel
  if isinstance(model, DistributedDataParallel):
    model = model.module
  return model



def get_eval_attr(obj, name, default=None, **kwargs):
  if hasattr(obj, name):
    value = getattr(obj, name)
    value = eval(value, kwargs)
  else:
    value = default
  return value


def get_attr_eval(obj, name, **kwargs):
  if hasattr(obj, name):
    value = getattr(obj, name)
    value = eval(value, kwargs)
  else:
    value = kwargs['default']
  return value


def get_attr_kwargs(obj, name, kwargs_priority=False, tl_ret_kwargs={}, **kwargs):
  if hasattr(obj, name):
    value = getattr(obj, name)
    if isinstance(value, str) and value.startswith('kwargs['):
      value = eval(value)
  elif name in kwargs:
    value = kwargs[name]
  else:
    value = kwargs['default']

  if kwargs_priority:
    value = kwargs.get(name, value)

  # for printing args
  tl_ret_kwargs[name] = value

  return value


def get_attr_format(obj, name, default=None, **kwargs):
  if hasattr(obj, name):
    value = getattr(obj, name)
    if isinstance(value, str):
      value = value.format(**kwargs)
  else:
    if default is None:
      raise AttributeError
    value = default
  return value


def is_debugging():
  import sys
  gettrace = getattr(sys, 'gettrace', None)

  if gettrace is None:
    assert 0, ('No sys.gettrace')
  elif gettrace():
    return True
  else:
    return False




