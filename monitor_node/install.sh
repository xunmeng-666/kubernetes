#!/bin/bash sh


#初始化操作
installPython()
{
    which pip3
    if [ $? -ne 0 ];then
        which python3
        if [ $? -ne 0 ];then
            SYSTEM="uname -a 2>&1|awk '{print $3}' |awk -F '.' '{print $1}'"
            if [[ '$SYSTEM'=7 ]];then
                echo '系统为7'
                echo 'yum安装Python34'
                yum install -y epel-release && yum install -y python34 gcc gcc-c++
                python3 get-pip.py
                return 0
            elif [[ '$SYSTEM'=6 ]]; then
                echo '系统为6'
                echo 'yum安装Python34'
                yum install -y python34
                python3 get-pip.py
                return 0
            fi
        else
            python3 get-pip.py
        fi
    pip3 install psutil
    pip3 install redis
    fi

}
installPython

echo "
rm -rf install.sh
python3 ./bin/start.py" > start.sh
sh start.sh