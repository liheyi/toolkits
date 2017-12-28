import os
import re
import time
import pexpect
import delegator
from datetime import date


# 格式化当前时间
today = date.today()
backup_date = today.strftime("%Y%m%d")

# 获取tmp目录下指定的sock文件
socks_info = delegator.run('ls /tmp').pipe('grep "zzgame[67][0-9][0-9].sock"')

# 清洗获取的sock文件，并转换为List
socks_list = sock_info.out.split('\n')
socks_list.remove('')

# 开始处理
for sock in socks_list:

    # 用于命令行命令的元素
    sock_num      = re.sub("\D", "", sock)

    sock_path     = ''.join(['/tmp/mysqlzz', sock_num, '.sock'])
    sock_pass     = ''.join(['-pdsdxfsh2013game', sock_num])
    database_name = ''.join(['zzgame', sock_num])
    backup_name   = ''.join(['/tmp/', database_name, '_', backup_date])


    #  构造mysqldump/tar/scp命令行命令

    #+ 1.构造mysqldump命令行命令
    dump_cmd = ' '.join(
        ['/usr/bin/mysqldump',
         '-u', 'root ',
         '-S', sock_path,
         sock_pass,
         database_name,
         '>',
         ''.join([backup_name, '.sql'])
        ]
    )

    #+ 2.构造备份文件检查命令
    dump_check = ' '.join(
        ['/usr/bin/tail',
         '-n1',
         ''.join([backup_name, '.sql'])
        ]
    )

    #+ 3.构造tar命令行命令
    tar_cmd = ' '.join(
        ['/bin/tar',
         '-czvf',
         ''.join([backup_name, '.tgz']),
         ''.join([backup_name, '.sql'])
        ]
    )

    #+ 4.构造归档压缩检查命令
    tar_check = ' '.join(
        ['/bin/tar',
         '-tf',
         ''.join([backup_name, '.tgz'])
        ]
    )

    #+ 5.构造scp命令行命令
    scp_cmd = ' '.join(
        ['/usr/bin/scp',
         '-P', '22022',
         ''.join([backup_name, '.tgz']),
         'root@123.59.70.16:/data2/mysqlbackup/'
        ]
    )


    # 执行mysqldump命令行命令并进行检查
    dump_info = delegator.run(dump_cmd)
    # 如果命令执行成功，则 dump_info_err = ''
    if not dump_info.err:
        print(' '.join([database_name, 'backup has been completed...']))
    else:
        pass
    # 验证备份文件的完整性
    if 'Dump' == delegator.run(dump_check).pipe("awk '{print $2}'").out.strip('\n'):
        print(' '.join([database_name, 'backup CHECK is OK...']))
    else:
        pass


    # 执行tar命令行命令并进行检查
    tar_info = delegator.run(tar_cmd)
    # 如果命令执行成功，则 tar_info.err = ''
    if not tar_info.err:
        print(' '.join([database_name, 'archive has been completed...']))
    else:
        pass
    # 验证归档文件的完整性
    arch_info = delegator.run(tar_check)
    if not arch_info.err:
        print(' '.join([database_name, 'archive CHECK is OK...']))
    else:
        pass

    #  执行scp命令行命令
    #+ 由于不会使用delegator.py工具中的expect命令
    #+ 因此使用pexpect模块(非标准库模块)进行替换

    password = r'dsdxfsh2015tk@2013&!'

    try:
        scp_info = pexpect.spawn(scp_cmd)
        status   = scp_info.expect(['password:', 'yes/no'])
        if 0 == status:
            scp_info.sendline(password)
            scp_info.expect(pexpect.EOF)
            # scp_info.read()
        elif 1 == status:
            scp_info.sendline('yes')
            scp_info.expect('password:')
            scp_info.sendline(password)
            scp_info.expect(pexpect.EOF)
            # scp_info.read()
        else:
            print("There was a little problem when uploading the archive...")

    except pexpect.EOF:
        print("Uploading the archive has failed.")
        scp_info.close()

    except pexpect.TIMEOUT:
        print("Uploading the archive has timed out.")

