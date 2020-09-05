import os
import sys
import unittest
import argparse

from template_lib import utils
from template_lib.v2.config import get_command_and_outdir, setup_outdir_and_yaml, get_append_cmd_str, \
  start_cmd_run


class TestingTFFIDISScore(unittest.TestCase):

  def test_case_calculate_fid_stat_CIFAR10(self):
    """
    export  LD_LIBRARY_PATH=/usr/local/cuda-10.0/lib64:/usr/local/cudnn-10.0-v7.6.5.32/lib64
    python -c "from template_lib.gans.tests.test_evaluate import TestingTFFIDISScore;\
      TestingTFFIDISScore().test_case_calculate_fid_stat_CIFAR10()"
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    if 'PORT' not in os.environ:
      os.environ['PORT'] = '6006'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0' if utils.is_debugging() else '1'
    # func name
    assert sys._getframe().f_code.co_name.startswith('test_')
    command = sys._getframe().f_code.co_name[5:]
    class_name = self.__class__.__name__[7:] \
      if self.__class__.__name__.startswith('Testing') \
      else self.__class__.__name__
    outdir = f'results/{class_name}/{command}'

    from template_lib.v2.GAN.evaluation.tf_FID_IS_score import TFFIDISScore
    TFFIDISScore.test_case_calculate_fid_stat_CIFAR10()
    pass

  def test_case_calculate_fid_stat_CIFAR10_ddp(self):
    """
    Usage:
        export PYTHONWARNINGS=ignore
        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export TIME_STR=1
        export PYTHONPATH=./exp:./stylegan2-pytorch:./
        python -c "from template_lib.v2.tests.test_GAN import TestingTFFIDISScore;\
          TestingTFFIDISScore().test_case_calculate_fid_stat_CIFAR10_ddp()"

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0' if utils.is_debugging() else '0'

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                """
    args = setup_outdir_and_yaml(argv_str)

    nproc_per_node = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    cmd_str = f"""
        python -m torch.distributed.launch --nproc_per_node={nproc_per_node} --master_port=8888 
          template_lib/v2/GAN/evaluation/tf_FID_IS_score.py 
            --run_func TFFIDISScore.test_case_calculate_fid_stat_CIFAR10
        """
    cmd_str += get_append_cmd_str(args)
    start_cmd_run(cmd_str)
    pass

  def test_case_evaluate_FID_IS(self):
    """
    export  LD_LIBRARY_PATH=/usr/local/cuda-10.0/lib64:/usr/local/cudnn-10.0-v7.6.5.32/lib64
    python -c "from template_lib.gans.tests.test_evaluate import TestingTFFIDISScore;\
      TestingTFFIDISScore().test_case_evaluate_FID_IS()"
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    if 'PORT' not in os.environ:
      os.environ['PORT'] = '6006'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0' if utils.is_debugging() else '1'
    # func name
    assert sys._getframe().f_code.co_name.startswith('test_')
    command = sys._getframe().f_code.co_name[5:]
    class_name = self.__class__.__name__[7:] \
      if self.__class__.__name__.startswith('Testing') \
      else self.__class__.__name__
    outdir = f'results/{class_name}/{command}'

    from template_lib.v2.GAN.evaluation.tf_FID_IS_score import TFFIDISScore
    TFFIDISScore.test_case_evaluate_FID_IS()
    pass
