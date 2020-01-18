from IPython.core.debugger import set_trace


class PlotResultsObs(object):
    
    def __init__(self, ):
        self.root_obs_dict = {
          'beijing': 's3://bucket-cv-competition-bj4/ZhouPeng',
          'huanan': 's3://bucket-1892/ZhouPeng',
          'huabei': 's3://bucket-cv-competition',
        }
        PlotResultsObs.setup_env()
        
        pass
    
    @staticmethod
    def setup_env():
        import os
        try:
            import mpld3
        except:
            os.system('pip install mpld3')
    
    def get_last_md_inter_time(self, filepath_obs):
        import moxing as mox
        from datetime import datetime, timedelta

        statbuf = mox.file.stat(filepath_obs)
        modi_time = datetime.fromtimestamp(statbuf.mtime_nsec/1e9) + timedelta(hours=8)
        modi_inter = datetime.now() - modi_time
        modi_minutes = modi_inter.total_seconds() // 60
        return int(modi_minutes)
    
    def get_fig_axes(self, rows, cols, figsize_wh=(15, 7)):
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        plt.rcParams['axes.prop_cycle'] = plt.cycler(
            color=['blue', 'green', 'red', 'cyan', 'magenta', 'black', 'orange', 'lime', 'tan', 'salmon', 'gold', 'darkred', 'darkblue'])
        fig, axes = plt.subplots(rows, cols, figsize=(figsize_wh[0]*cols, figsize_wh[1]*rows))
        if rows * cols > 1:
            axes = axes.ravel()
        else:
            axes = [axes]
        return fig, axes
    
    def get_itr_val_str(self, data, ismax):
        if ismax:
            itr = int(data[:, 0][data[:, 1].argmax()])
            val = data[:, 1].max()
            return f'itr.{itr:06d}_maxv.{val:.3f}'
        else:
            itr = int(data[:, 0][data[:, 1].argmin()])
            val = data[:, 1].min()
            return f'itr.{itr:06d}_minv.{val:.3f}'

    def plot_defaultdicts(self, default_dicts, show_max=True, bucket='huanan', figsize_wh=(15, 8), legend_size=12):
        import matplotlib.pyplot as plt
        %matplotlib inline
        import numpy as np
        import mpld3
        mpld3.enable_notebook()
        import os
        import moxing as mox
        import tempfile
        if not isinstance(default_dicts, list):
            default_dicts = [default_dicts]
        if not isinstance(show_max, list):
            show_max = [show_max]
        assert len(show_max) == len(default_dicts)

        fig, axes = self.get_fig_axes(rows=len(default_dicts), cols=1, figsize_wh=figsize_wh)
        
        bucket = self.root_obs_dict[bucket]    
        root_dir = os.path.expanduser('~/results')
        
        label2datas_list = []
        for idx, default_dict in enumerate(default_dicts):
            label2datas = {}
            # for each result dir
            for (result_dir, label2file) in default_dict.items():
                if result_dir == 'properties':
                    continue
                # for each texlog file
                for label, file in label2file.items():
                    filepath = os.path.join(root_dir, result_dir, file)
                    filepath_obs = os.path.join(bucket, result_dir, file)
                    if not mox.file.exists(filepath_obs):
                        print("=> Not exist: '%s'"%filepath_obs)
                        continue
                    mox.file.copy(filepath_obs, filepath)
                    # get modified time
                    modi_minutes = self.get_last_md_inter_time(filepath_obs)

                    data = np.loadtxt(filepath, delimiter=':')
                    data = data.reshape(-1, 2)
                    
                    itr_val_str = self.get_itr_val_str(data, show_max[idx])
                    label_str = f'{itr_val_str}' + f'-{modi_minutes:03d}m---' + label
                    
                    axes[idx].plot(data[:, 0], data[:, 1], label=label_str, marker='.', linewidth='5', markersize='15', alpha=0.5)
                    label2datas[label] = data
            axes[idx].legend(prop={'size': legend_size})
            axes[idx].set(**default_dict['properties'])
                    
            label2datas_list.append(label2datas)
        
        return label2datas_list

    
import collections
default_dict = collections.defaultdict(dict)

default_dict['results/Domain-Adaptive-Faster-RCNN-PyTorch/Examples/train_no_domain_adaptive_faster_rcnn_20200117-19_14_05_880'] = {
    'train_no_domain_adaptive_faster_rcnn_bs.2_cityscapes': 'textlog/eval.AP50.cityscapes_fine_instanceonly_seg_val_cocostyle.log',
    'train_no_domain_adaptive_faster_rcnn_bs.2_foggy_cityscapes': 'textlog/eval.AP50.foggy_cityscapes_fine_instanceonly_seg_val_cocostyle.log'
}
default_dict['results/Domain-Adaptive-Faster-RCNN-PyTorch/Examples/train_no_domain_adaptive_faster_rcnn_20200117-23_28_47_574'] = {
    'train_no_domain_adaptive_faster_rcnn_bs.1_cityscapes': 'textlog/eval.AP50.cityscapes_fine_instanceonly_seg_val_cocostyle.log',
    'train_no_domain_adaptive_faster_rcnn_bs.1_foggy_cityscapes': 'textlog/eval.AP50.foggy_cityscapes_fine_instanceonly_seg_val_cocostyle.log'
}
default_dict['results/Domain-Adaptive-Faster-RCNN-PyTorch/Examples/train_domain_adaptive_faster_rcnn_20200117-13_14_00_183'] = {
    'train_domain_adaptive_faster_rcnn_bs.1_cityscapes': 'textlog/eval.AP50.cityscapes_fine_instanceonly_seg_val_cocostyle.log',
    'train_domain_adaptive_faster_rcnn_bs.1_foggy_cityscapes': 'textlog/eval.AP50.foggy_cityscapes_fine_instanceonly_seg_val_cocostyle.log'
}
default_dict['properties'] = {'title': 'AP50', 'xlim': [0, 70000]}
default_dicts = [default_dict] 
show_max = [True, ]
plotobs = PlotResultsObs()
plotobs.plot_defaultdicts(default_dicts=default_dicts, show_max=show_max, bucket='beijing', figsize_wh=(16, 7.2))
pass
