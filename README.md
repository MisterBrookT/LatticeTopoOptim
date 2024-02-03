# LatticeTopoOptim
## abaqus驱动命令
abaqus提供了一系列abaqus驱动命令以供在外部访问abaqus，如下：
    
    abaqus cae
        [database=database-file] 指定 Abaqus CAE 使用的数据库文件。
        [replay=replay-file] 指定 Abaqus CAE 使用的回放文件，用于自动化重复之前的操作。
        [recover=journal-file] 指定 Abaqus CAE 使用的日志文件，用于恢复操作。
        [startup=startup-file] 指定 Abaqus CAE 使用的启动文件，在启动时自动运行一些命令或脚本。
        [script=script-file] 指定 Abaqus CAE 使用的脚本文件，用于自动化执行一系列命令
        [noGUI=noGUI-file] 指定 Abaqus CAE 使用的无 GUI 模式脚本文件，用于在无需图形界面的环境下执行脚本
        [noenvstartup] 禁用环境启动文件。
        [noSavedOptions] 禁用保存的选项。
        [noSavedGuiPrefs] 禁用保存的图形界面偏好设置。
        [noStartupDialog] 指定自定义脚本文件，用于执行特定的操作。
        [custom=script-file] 指定自定义脚本文件，用于执行特定的操作。
        [guiTester=GUI-script] 指定用于自动化测试的 GUI 脚本文件。
        [guiRecord] 启用 GUI 录制模式，记录用户在图形界面上的操作。
        [guiNoRecord] 禁用 GUI 录制模式。

我们可以使用在py中使用命令行执行上述abaqus命令，下面是一个简单的例子：
    import os
    a = os.system("abaqus cae noGUI=test.py -- 0.8 0.3")

上述例子完成在外部编辑器调起abaqus，执行一个test.py的脚本  并在语句后面附加两个参数0.8和0.3，这将被cae编译器忽视，但可以在test.py内部被读取。

这里简单说明一点，通过使用两个'-'符号完成的参数附加，可以通过sys.argv读取，但在abaqus中，附加的参数将在第八位以后，一个完整的文件信息是
    ['C:\\ABAQUS\\6.13-2SE\\code\\bin\\ABQcaeK.exe', '-cae', '-noGUI', '-lmlog', 'ON', '-tmpdir', 'C:\\Windows\\TEMP','0.8','0.3']

## Reference

[Introduction to Bayesian Optimization(BO)](https://distill.pub/2020/bayesian-optimization/)

[SMAC: A Versatile BO Package](https://automl.github.io/SMAC3/main/)

