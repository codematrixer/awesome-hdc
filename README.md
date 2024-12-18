>由于鸿蒙生态还处于初期，官方提供的hdc命令还在不断修改中，部分命令会有变动。
>如果文档没来得及更新，欢迎大家提PR和Issue补充指正，觉得有用的可以点 Star⭐️收藏。

HDC（OpenHarmony Device Connector） 是为鸿蒙开发/测试人员提供的用于设备调试的命令行工具，类似Android端的ADB工具。

HDC主要有三部分组成:
1. `hdc client`：运行于电脑上的客户端，用户可以在电脑命令终端（windows cmd/linux shell）下请求执行相应的hdc命令。
2. `hdc server`：作为后台进程也运行于电脑上，server管理client和设备端daemon之间通信包括连接的复用、数据通信包的收发，以及个别本地命令的直接处理。
3. `hdc daemon`：daemon部署于OpenHarmony设备端作为守护进程按需运行，负责处理来自client端请求。

![hdc](https://i.ibb.co/WHpLY3y/hdc.png)


**Table of Contents**
- [HDC安装](#hdc安装)
- [基本用法](#基本用法)
  - [基本语法](#基本语法)
- [设备连接管理](#设备连接管理)
  - [查看HDC版本](#查看hdc版本)
  - [启动/停止 HDC Server](#启动停止-hdc-server)
  - [查询设备列表](#查询设备列表)
  - [查询设备UDID](#查询设备udid)
  - [重启手机](#重启手机)
- [查看设备信息](#查看设备信息)
  - [名称](#名称)
  - [Brand](#brand)
  - [Model](#model)
  - [系统版本](#系统版本)
  - [OS版本](#os版本)
  - [CPU架构](#cpu架构)
  - [分辩率](#分辩率)
  - [wlan IP](#wlan-ip)
  - [电量/温度](#电量温度)
  - [查看屏幕信息](#查看屏幕信息)
  - [查看屏幕旋转状态](#查看屏幕旋转状态)
  - [查看屏幕亮屏状态](#查看屏幕亮屏状态)
  - [点亮屏幕（唤醒）](#点亮屏幕唤醒)
  - [查看网络状态](#查看网络状态)
- [应用管理](#应用管理)
  - [安装应用](#安装应用)
  - [卸载应用](#卸载应用)
  - [获取应用列表](#获取应用列表)
  - [启动应用](#启动应用)
  - [退出应用](#退出应用)
  - [获取应用版本](#获取应用版本)
  - [Dump应用信息](#dump应用信息)
    - [获取应用 Ability信息](#获取应用-ability信息)
    - [获取应用详情](#获取应用详情)
  - [清除应用数据](#清除应用数据)
    - [清除应用缓存](#清除应用缓存)
    - [清除应用数据](#清除应用数据-1)
  - [显示可调试应用列表](#显示可调试应用列表)
- [端口转发](#端口转发)
  - [显示端口转发列表](#显示端口转发列表)
  - [本地端口转发到手机](#本地端口转发到手机)
  - [删除端口转发任务](#删除端口转发任务)
- [无线调试](#无线调试)
- [文件传输](#文件传输)
  - [从本地电脑发送文件至手机](#从本地电脑发送文件至手机)
  - [从手机拷贝文件至本地电脑](#从手机拷贝文件至本地电脑)
- [UI模拟操作(点击滑动等)](#ui模拟操作点击滑动等)
- [屏幕截图](#屏幕截图)
- [屏幕录屏](#屏幕录屏)
- [打开Scheme (URL)](#打开scheme-url)
- [获取页面布局信息（控件树）](#获取页面布局信息控件树)
- [录制用户操作](#录制用户操作)
- [系统日志（log）](#系统日志log)
- [导出日志](#导出日志)
- [导出crash日志](#导出crash日志)
- [hidumper工具](#hidumper工具)
  - [list system abilities](#list-system-abilities)
  - [RenderService](#renderservice)
  - [DisplayManagerService](#displaymanagerservice)
  - [PowerManagerService](#powermanagerservice)
  - [BatteryService](#batteryservice)
  - [NetConnManager](#netconnmanager)
  - [MemoryManagerService](#memorymanagerservice)
  - [StorageManager](#storagemanager)
- [aa工具](#aa工具)
  - [start](#start)
  - [stop-service](#stop-service)
  - [force-stop](#force-stop)
  - [test](#test)
  - [attach](#attach)
  - [detach](#detach)
  - [appdebug](#appdebug)
- [bm工具](#bm工具)
  - [install](#install)
  - [uninstall](#uninstall)
  - [dump](#dump)
  - [clean](#clean)
  - [enable](#enable)
  - [disable](#disable)
  - [get](#get)
- [param工具](#param工具)
- [Instrument Test](#instrument-test)
- [性能工具](#性能工具)
- [参考链接](#参考链接)



# HDC安装
- 下载 [Command Line Tools](https://developer.huawei.com/consumer/cn/download/) 并解压
- `hdc`文件在`command-line-tools/sdk/default/openharmony/toolchains`目录下

- 配置电脑环境变量，以macOS为例，在`~/.bash_profile` 或者 `~/.zshrc`文件中添加如下内容：
```
export HM_SDK_HOME="/Users/develop/command-line-tools/sdk/default"  //请以sdk实际安装目录为准
export PATH=$PATH:$HM_SDK_HOME/hms/toolchains:$HM_SDK_HOME/openharmony/toolchains
export HDC_SERVER_PORT=7035
```
也可以自行编译安装：参考鸿蒙官方gitee文档

# 基本用法
## 基本语法
```shell
hdc -t <connectKey> <command>
```
如果只有一个设备/模拟器连接时，可以省略掉`-t <connectKey>` 这一部分，直接使用`hdc <command>`。在多个设备/模拟器连接的情况下需要指定`-t` 参数， `connectKey`可以通过`hdc list targets`命令获取，对应Android里的`adb devices`获取的`serialNumber`。
```shell
$ hdc list targets

127.0.0.1:5555    //<IP>:<Port>形式的connectKey ，一般为无线连接的设备或模拟器
FMR0223C13000649
```


比如给`FMR0223C13000649` 这个设备安装应用：
```shell
$ hdc -t FMR0223C13000649 install entry-default-signed.hap

[Info]App install path:/Users/develop/entry-default-signed.hap, queuesize:0, msg:install bundle successfully.
AppMod finish
```

**注意事项**

-  使用`hdc`，如果出现异常，可以尝试通过`hdc kill -r`命令杀掉并重启hdc服务。
-  如果出现`hdc list targets`获取不到设备信息的情况，可以通过任务管理器查看是否有hdc进程存在。若进程存在，则通过`hdc kill -r`命令杀掉该进程。

# 设备连接管理
## 查看HDC版本
```shell
$ hdc -v

Ver: 2.0.0a
```


## 启动/停止 HDC Server
停止
```shell
$ hdc kill

Kill server finish
```

重启
```shell
$ hdc start -r
```

## 查询设备列表
```
$ hdc list targets

127.0.0.1:5555
FMR0223C13000649
```

`-v` 选项 显示详细信息
```
$ hdc list targets -v

127.0.0.1:5555		  TCP	  Connected	  localhost
FMR0223C13000649		USB	  Connected	  unknown...
```

输出的内容第一列为设备的`connectKey`， 第二列是设备`连接方式`，第三列为设备`连接状态`，第四列暂时未知

## 查询设备UDID
```shell
$ hdc shell bm get --udid

udid of current device is :
C46284C052AE01BBD2358FE44B279524B508FC959AAB5F4B0B74E42A06569B7E
```

这个`udid`在用开发者账号打包时，需要添加这个`udid`到对应的`profile`文件中

## 重启手机
```shell
$ hdc target boot

```


# 查看设备信息

## 名称
```shell
$ hdc shell param get const.product.name               

HUAWEI Mate 60 Pro
```
## Brand
```shell
$ hdc shell param get const.product.brand

HUAWEI 
```
## Model
```shell
$ hdc shell param get const.product.model

ALN-AL00 
```
## 系统版本
```shell
$ hdc shell param get const.product.software.version                                      

ALN-AL00 5.0.0.22(SP35DEVC00E22R4P1log) 
```

## OS版本
```shell
$ hdc shell param get const.ohos.apiversion  

12 
```

## CPU架构
```shell
$ hdc  shell param get const.product.cpu.abilist  

arm64-v8a 
```
## 分辩率
```shell
$ hdc shell hidumper -s RenderService -a screen


-------------------------------[ability]-------------------------------


----------------------------------RenderService---------------------------------
-- ScreenInfo
screen[0]: id=0, powerstatus=POWER_STATUS_OFF, backlight=51, screenType=EXTERNAL_TYPE, render size: 1260x2720, physical screen resolution: 1260x2720, isvirtual=false, skipFrameInterval_:1

  supportedMode[0]: 1260x2720, refreshrate=120
  supportedMode[1]: 1260x2720, refreshrate=90
  supportedMode[2]: 1260x2720, refreshrate=60
  supportedMode[3]: 1260x2720, refreshrate=30
  activeMode: 1260x2720, refreshrate=60
  capability: name=, phywidth=72, phyheight=156,supportlayers=12, virtualDispCount=0, propCount=0, type=DISP_INTF_HDMI, supportWriteBack=false
```

执行上述命令后，解析返回内容，可以通过正则表达式提取`1260x2720`

## wlan IP
```shell
$ hdc shell ifconfig

lo        Link encap:Local Loopback
          inet addr:127.0.0.1  Mask:255.0.0.0
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:99055 errors:0 dropped:0 overruns:0 frame:0
          TX packets:99055 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:5889697 TX bytes:5889697

wlan0     Link encap:Ethernet  HWaddr ea:f9:7d:21:52:31
          inet addr:172.31.125.111  Bcast:172.31.125.255  Mask:255.255.254.0
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:1232924 errors:0 dropped:0 overruns:0 frame:0
          TX packets:2061202 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:877179224 TX bytes:2570352818

p2p0      Link encap:Ethernet  HWaddr d2:0d:f7:cc:12:fb
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:0 TX bytes:0

chba0     Link encap:Ethernet  HWaddr ec:11:05:fb:18:66
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:0 TX bytes:0
```

注意：这个命令在Beta3版本之前，会提示`Cannot open netlink socket: Permission denied`，需要升级系统。

## 电量/温度

```shell
$ hdc shell hidumper -s BatteryService -a -i                

-------------------------------[ability]-------------------------------


----------------------------------BatteryService---------------------------------
Current time: 2024-05-30 12:08:37.419
capacity: 100 
batteryLevel: 1 
chargingStatus: 3 
healthState: 1 
pluggedType: 1 
voltage: 4496732 
present: 1 
technology: Li-poly 
nowCurrent: 123 
currentAverage: 83 
totalEnergy: 5203 
remainingEnergy: 5207 
remainingChargeTime: 0 
temperature: 280 
chargeType: 1 
```

## 查看屏幕信息
```shell
$ hdc shell hidumper -s DisplayManagerService -a -a

-------------------------------[ability]-------------------------------


----------------------------------DisplayManagerService----------------------------------
-------------- DMS Multi User Info --------------
[oldScbPid:]
[userId:] 100
[ScbPid:] 4438
---------------- Screen ID: 0 ----------------
FoldStatus:                   UNKNOWN
[SCREEN SESSION]
Name:                         UNKNOWN
RSScreenId:                   0
activeModes<id, W, H, RS>:    0, 1260, 2720, 120
SourceMode:                   0
ScreenCombination:            0
Orientation:                  0
Rotation:                     0
ScreenRequestedOrientation:   0
[RS INFO]
SupportedColorGamuts:         0, 4, 6
ScreenColorGamut:             4
GraphicPixelFormat:           0
SupportedScreenHDRFormat:     2, 1, 3
ScreenHDRFormat:              2
SupportedColorSpaces:         0, 2294273, 2294278
ScreenColorSpace:             2294273
[CUTOUT INFO]
WaterFall_L<X,Y,W,H>:         0, 0, 0, 0
WaterFall_T<X,Y,W,H>:         0, 0, 0, 0
WaterFall_R<X,Y,W,H>:         0, 0, 0, 0
WaterFall_B<X,Y,W,H>:         0, 0, 0, 0
BoundingRects<X,Y,W,H>:       [494, 36, 273, 72]
[SCREEN INFO]
VirtualWidth:                 387
VirtualHeight:                836
LastParentId:                 18446744073709551615
ParentId:                     1
IsScreenGroup:                0
VirtualPixelRatio:            3.25
Rotation:                     0
Orientation:                  0
SourceMode:                   0
ScreenType:                   1
[SCREEN PROPERTY]
Rotation:                     0
Density:                      3.25
DensityInCurResolution:       3.25
PhyWidth:                     72
PhyHeight:                    156
RefreshRate:                  60
VirtualPixelRatio:            3.25
ScreenRotation:               0
Orientation:                  0
DisplayOrientation:           0
GetScreenType:                1
ReqOrientation:               0
DPI<X, Y>:                    444.5, 442.871
Offset<X, Y>:                 0, 0
Bounds<L,T,W,H>:              0, 0, 1260, 2720,
PhyBounds<L,T,W,H>:           0, 0, 1260, 2720,
AvailableArea<X,Y,W,H>        0, 0, 1260, 2720,
DefaultDeviceRotationOffset   0
```

执行上述命令后，解析返回内容，通过正则提取需要的信息，比如屏幕尺寸分辨率Bounds，VirtualWidth，VirtualHeight，PhyWidth，PhyHeight，ScreenRotation

## 查看屏幕旋转状态

```shell
$ hdc shell hidumper -s DisplayManagerService -a -a
```
通过上面的查看屏幕信息命令，通过正则提取ScreenRotation字段即可，ScreenRotation有四个值：
- 0：未旋转
- 90：顺时针旋转90度
- 180：顺时针旋转180度
- 270：顺时针旋转270度

备注：目前旋转状态只能查看，不支持设置

## 查看屏幕亮屏状态
```shell
$ hdc shell hidumper -s PowerManagerService -a -s

-------------------------------[ability]-------------------------------


----------------------------------PowerManagerService----------------------------------
POWER STATE DUMP:
Current State: AWAKE  Reason: 20  Time: 521085695
ScreenOffTime: Timeout=600000ms
DUMP DETAILS:
Last Screen On: 521248337
Last Screen Off: 467804783
Last SuspendDevice: 0
Last WakeupDevice: 464729447
Last Refresh: 521248337
DUMP EACH STATES:
State: AWAKE   Reason: POWER_KEY   Time: 521085695
   Failure: INIT   Reason:    From: AWAKE   Time: 0

State: FREEZE   Reason: INIT   Time: 0
   Failure: INIT   Reason:    From: AWAKE   Time: 0

State: INACTIVE   Reason: TIMEOUT   Time: 467805109
   Failure: INIT   Reason:    From: AWAKE   Time: 0

State: STAND_BY   Reason: INIT   Time: 0
   Failure: INIT   Reason:    From: AWAKE   Time: 0

State: DOZE   Reason: INIT   Time: 0
   Failure: INIT   Reason:    From: AWAKE   Time: 0

State: SLEEP   Reason: TIMEOUT   Time: 467810120
   Failure: INIT   Reason:    From: AWAKE   Time: 0

State: HIBERNATE   Reason: INIT   Time: 0
   Failure: INIT   Reason:    From: AWAKE   Time: 0

State: SHUTDOWN   Reason: INIT   Time: 0
   Failure: INIT   Reason:    From: AWAKE   Time: 0

State: DIM   Reason: TIMEOUT   Time: 467797280
   Failure: TIMEOUT   Reason: Blocked by running lock   From: AWAKE   Time: 447180354
```
屏幕状态有这几种：
- INACTIVE
- SLEEP
- AWAKE


## 点亮屏幕（唤醒）
```shell
$ hdc shell power-shell wakeup

WakeupDevice is called
```

## 查看网络状态

**联网状态**
```shell
$ hdc shell hidumper -s NetConnManager

-------------------------------[ability]-------------------------------


----------------------------------NetConnManager----------------------------------
Net connect Info:
	defaultNetSupplier_ is nullptr
	SupplierId:
	NetId: 0
	ConnStat: 0
	IsAvailable:
	IsRoaming: 0
	Strength: 0
	Frequency: 0
	LinkUpBandwidthKbps: 0
	LinkDownBandwidthKbps: 0
	Uid: 0
Dns result Info:
	netId: 0
	totalReports: 2
	failReports: 2
```

**wifi信息**
```shell
$ hdc shell hidumper -s WifiDevice

-------------------------------[ability]-------------------------------


----------------------------------WifiDevice----------------------------------
WiFi active state: activated

WiFi connection status: connected
  Connection.ssid: K-Lab
  Connection.bssid: cc:d0:**:**:**:e2
  Connection.rssi: -45
  Connection.band: 2.4GHz
  Connection.frequency: 2462
  Connection.linkSpeed: 156
  Connection.macAddress: ea:f9:**:**:**:31
  Connection.isHiddenSSID: false
  Connection.signalLevel: 4

Country Code: CN
```


# 应用管理
## 安装应用
```shell
$ hdc app install entry-default-signed.hap

[Info]App install path:/Users/develop/entry-default-signed.hap, queuesize:0, msg:install bundle successfully.
AppMod finish
```
或者
```shell
$ hdc install entry-default-signed.hap

[Info]App install path:/Users/develop/entry-default-signed.hap, queuesize:0, msg:install bundle successfully.
AppMod finish
```


## 卸载应用
```shell
$ hdc app uninstall com.kk.hmscrcpy

[Info]App uninstall path:, queuesize:0, msg:uninstall bundle successfully.
AppMod finish
```

或者
```shell
$ hdc uninstall com.kk.hmscrcpy

[Info]App uninstall path:, queuesize:0, msg:uninstall bundle successfully.
AppMod finish
```


## 获取应用列表
```shell
$ hdc shell bm dump -a

ID: 100:
	com.huawei.associateassistant
	com.huawei.batterycare
	com.huawei.hmos.AutoRegService
	com.huawei.hmos.advisor
	com.huawei.hmos.advsecmode
	com.huawei.hmos.aibase
	com.huawei.hmos.aidataservice
	com.huawei.hmos.aidispatchservice
	com.huawei.hmos.ailife
	com.huawei.hmos.ailifesvc
	com.huawei.hmos.audioaccessorymanager
	com.huawei.hmos.authcredmgr
  ...
```


## 启动应用
通过启动`Ability`来拉起`APP`
```shell
hdc shell aa start -a {abilityName} -b {bundleName} 

```

-  其中`bundleName`可以通过`hdc shell bm dump -a`获取

-  其中`abilityName`可以通过如下命令获取（查看当前任务栈的ability信息）

```shell
$ hdc shell aa dump -l    # 运行命令前需要手动打开app

User ID #100
  current mission lists:{
    Mission ID #139  mission name #[#com.kuaishou.hmapp:kwai:EntryAbility]  lockedState #0  mission affinity #[]
      AbilityRecord ID #55
        app name [com.kuaishou.hmapp]
        main name [EntryAbility]
        bundle name [com.kuaishou.hmapp]
        ability type [PAGE]
        state #FOREGROUND  start time [152523]
        app state #FOREGROUND
        ready #1  window attached #0  launcher #0
        callee connections:
        isKeepAlive: false
 }
```
 里面的EntryAbility就是你要打开app的Ability名称

## 退出应用
强制退出应用
```shell
hdc shell aa force-stop {bundleName} 
```

-  其中`bundleName`可以通过`hdc shell bm dump -a`获取


## 获取应用版本
```shell
$ hdc shell bm dump -n {bundleName}
```
执行上述命令后，再解析json, 提取`versionName`字段即可


## Dump应用信息
**aa dump**
```shell
$ hdc shell aa dump -h

usage: aa dump <options>
options list:
  -h, --help                   list available commands
  -a, --all                    dump all abilities
  -l, --mission-list           dump mission list
  -i, --ability                dump abilityRecordId
  -e, --extension              dump elementName (FA: serviceAbilityRecords,Stage: ExtensionRecords)
  -p, --pending                dump pendingWantRecordId
  -r, --process                dump process
  -d, --data                   dump the data abilities
  -u, --userId                 userId
  -c, --client                 client
  -c, -u are auxiliary parameters and cannot be used alone
```

**bm dump**
```shell
$ hdc shell bm dump -h

usage: bm dump <options>
options list:
  -h, --help                           list available commands
  -a, --all                            list all bundles in system
  -n, --bundle-name <bundle-name>      list the bundle info by a bundle name
  -s, --shortcut-info                  list the shortcut info
  -d, --device-id <device-id>          specify a device id
  -u, --user-id <user-id>              specify a user id
```

### 获取应用 Ability信息
```shell
$ hdc shell aa dump -l    //运行命令前需要手动打开app

User ID #100
  current mission lists:{
    Mission ID #139  mission name #[#com.kuaishou.hmapp:kwai:EntryAbility]  lockedState #0  mission affinity #[]
      AbilityRecord ID #55
        app name [com.kuaishou.hmapp]
        main name [EntryAbility]
        bundle name [com.kuaishou.hmapp]
        ability type [PAGE]
        state #FOREGROUND  start time [152523]
        app state #FOREGROUND
        ready #1  window attached #0  launcher #0
        callee connections:
        isKeepAlive: false
 }
```


### 获取应用详情

查询该应用的详细信息

```shell
$ hdc shell bm dump -n com.kuaishou.hmapp

com.kuaishou.hmapp:
{
    "appId": "com.kuaishou.hmapp_BIS88rItfUAk+V9Y4WZp2HgIZ/JeOgvEBkwgB/YyrKiwrWhje9Xn2F6Q7WKFVM22RdIR4vFsG14A7ombgQmIIxU=",
    "appIdentifier": "5765880207853819885",
    "appIndex": 0,
    "applicationInfo": {
        ...
        "applicationReservedFlag": 0,
        "arkNativeFileAbi": "",
        "arkNativeFilePath": "",
        "asanEnabled": false,
        "asanLogPath": "",
        "associatedWakeUp": false,
        "bundleName": "com.kuaishou.hmapp",
        "bundleType": 0,
        "cacheDir": "",
        "codePath": "/data/app/el1/bundle/public/com.kuaishou.hmapp",
        "compileSdkType": "HarmonyOS",
        "compileSdkVersion": "4.1.0.73",
        "cpuAbi": "arm64-v8a",
        "crowdtestDeadline": -1,
        "dataBaseDir": "/data/app/el2/database/com.kuaishou.hmapp",
        "dataDir": "",
        "debug": true,
        "description": "",
        "descriptionId": 0,
        "descriptionResource": {
            "bundleName": "com.kuaishou.hmapp",
            "id": 0,
            "moduleName": "kwai"
        },
        "deviceId": "PHONE-001",
        "distributedNotificationEnabled": true,
        "enabled": true,
        "entityType": "unspecified",
        "entryDir": "",
        "entryModuleName": "",
        "fingerprint": "96C4B0B051421A56EC9117BC6E3CF093C428B6B6D59DA13205C29C9BDD39AE7C",
        ...
        "minCompatibleVersionCode": 999999,
        "moduleInfos": [
            {
                "moduleName": "kwai",
                "moduleSourceDir": "",
                "preloads": []
            }
        ],
				...
        "userDataClearable": true,
        "vendor": "快手",
        "versionCode": 999999,
        "versionName": "12.2.40"
    },
    "compatibleVersion": 40100011,
    "cpuAbi": "",
    "defPermissions": [],
    "description": "",
    "entryInstallationFree": false,
    "entryModuleName": "kwai",
    "gid": 20020014,
    "hapModuleInfos": [
        ...
    ],
    "reqPermissions": [
        "ohos.permission.ACCELEROMETER",
        "ohos.permission.GET_NETWORK_INFO",
        "ohos.permission.GET_WIFI_INFO",
        "ohos.permission.INTERNET",
        "ohos.permission.SET_NETWORK_INFO",
        "ohos.permission.STORE_PERSISTENT_DATA"
    ],
		...
    "vendor": "快手",
    "versionCode": 999999,
    "versionName": "12.2.40"
}
```
通过这个命令可以获取到很多应用的关键信息，比如`reqPermissions`，`version`，`abilities`等等


## 清除应用数据
```shell
$ hdc shell bm clean -h

usage: bm clean <options>
options list:
  -h, --help                                      list available commands
  -n, --bundle-name  <bundle-name>                bundle name
  -c, --cache                                     clean bundle cache files by bundle name
  -d, --data                                      clean bundle data files by bundle name
  -u, --user-id <user-id>                         specify a user id
```


### 清除应用缓存
```shell
$ hdc shell bm clean -n {bundleName}  -c

clean bundle cache files successfully.
```

其中`bundleName`可以通过`hdc shell bm dump -a`获取， 比如`com.kuaishou.hmapp`

### 清除应用数据
```shell
$ hdc shell bm clean -n {bundleName} -d 
```
                

## 显示可调试应用列表
```shell
$  hdc jpid

2571
2633
2638
2658
2666
2691
2825
3310
3804
3977
30178

$ hdc track-jpid

0000
```
- `jpid`显示可调试应用列表
- `track-jpid`动态显示可调试应用列表。


# 端口转发
|命令|	说明|
|---|---|
|fport ls	|展示全部“端口转发主机端口转发数据到设备侧端口”的转发任务|
|fport local remote|	端口转发主机端口转发数据到设备侧端口|
|fport rm local remote|	删除指定“端口转发主机端口转发数据到设备侧端口”的转发任务|
|rport ls	|展示全部“端口转发设备侧端口转发数据到主机端口”的转发任务|
|rport local remote|	端口转发设备侧端口转发数据到主机端口|
|rport rm local remote|	删除指定“端口转发设备侧端口转发数据到主机端口”的转发任务|

## 显示端口转发列表
展示电脑端口转发到手机端口的列表
```shell
$ hdc fport ls

FMR0223C13000649    tcp:7912 tcp:7912    [Forward]
```

## 本地端口转发到手机
将本地电脑的`7913`端口转发到手机`7912`端口
```shell
$ hdc fport tcp:7913 tcp:7912

Forwardport result:OK
```

这个命令非常实用，比如我再手机上实现了一个 `http`服务，没有这个命令前需要通过手机`ip:port`来访问，这就需要提前知道手机的`wlanIP`，执行这个命令后可以直接通过`localhost:localPort`来访问手机里的服务。


## 删除端口转发任务
```shell
$ hdc fport rm tcp:7913 tcp:7912
Remove forward ruler success, ruler:tcp:7913 tcp:7912

$ hdc fport ls
[Empty]
```

同理，`rport`命令表示手机端口转发到电脑端口，我就不一一举例了.

# 无线调试
**方式一：通过手机ip进行连接** (这个方式需要手机和PC处于同一个局域网内)
1. 在手机上开启tcp端口 `hdc -t <serial> tmode port <port>`
2. 连接手机上的tcp端口 `hdc tconn <wlan_ip>:<port>`
3. 关闭无线连接 `hdc -t <serial> tmode port close`

示例

```shell
$ hdc -t FMR0223C13000649 tmode port 5555

$ hdc tconn 172.31.124.84:5555   # 这个ip为手机的wlanIp
Connect OK

$ hdc list targets
172.31.124.84:5555
FMR0223C13000649

$ hdc -t 172.31.124.84:5555 tmode port close
Set device run mode successful.
```

**方式二：通过PC的ip进行连接** （这个方式数据线不能拔掉）
1. 在手机上开启5555端口 `hdc -t <serial> tmode port <port>`
2. 将手机的端口转发到PC上 `hdc -t <serial> fport tcp:<host_port> tcp:<port>`
3. 连接PC上的端口 `hdc tconn 127.0.0.1:{host_port}`
4. 关闭无线连接 `hdc -t <serial> tmode port close`

示例

```shell
$ hdc -t FMR0223C13000649 tmode port 5555

$ hdc -t FMR0223C13000649 fport tcp:5556 tcp:5555
Forwardport result:OK

$ hdc tconn 127.0.0.1:5556
Connect OK

$ hdc list targets
127.0.0.1:5556
FMR0223C13000649

$ hdc -t FMR0223C13000649 tmode port close
Set device run mode successful.
```

**！！注意！！** 方式二中，由于hdc服务只监听了127.0.0.1， 导致其他主机上无法访问，需要将端口再转发一下，可以用socat等工具进行转发
```
$ socat TCP-LISTEN:5557,fork TCP:localhost:5556
```

然后在其他主机进行connect
```
$ hdc tconn <host_ip>:5557
Connect OK
```

# 文件传输
|命令|	说明|
|--|--|
|file send local remote|	从本地发送文件至远端设备|
|file recv remote local|	从远端设备发送文件至本地|

## 从本地电脑发送文件至手机
```shell
$ hdc file send ~/layout_407568854.json /data/local/tmp/layout_407568854.json

FileTransfer finish, Size:71792, File count = 1, time:24ms rate:2991.33kB/s
```


## 从手机拷贝文件至本地电脑
```shell
$ hdc file recv /data/local/tmp/layout_407568854.json ~/layout_407568854.json

[I][2024-05-28 20:15:45] HdcFile::TransferSummary success
FileTransfer finish, Size:71792, File count = 1, time:12ms rate:5982.67kB/s
```


# UI模拟操作(点击滑动等)
支持操作类型：`点击` `双击` `长按` `慢滑` `快滑` `拖拽` `输入文字` `KeyEvent`
| 配置参数名  | 配置参数含义                              | 配置参数取值                                                                                                                                                       | 示例                                                                                             |
|-------------|-------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| click       | 模拟单击操作                              | point_x (必选参数,点击x坐标点)<br>point_y (必选参数,点击y坐标点)                                                                                                   | hdc shell uitest uiInput click point_x point_y                                                   |
| doubleClick | 模拟双击操作                              | point_x (必选参数,双击x坐标点)<br>point_y (必选参数,双击y坐标点)                                                                                                  | hdc shell uitest uiInput doubleClick point_x point_y                                             |
| longClick   | 模拟长按操作                              | point_x (必选参数,长按x坐标点)<br>point_y (必选参数,长按y坐标点)                                                                                                  | hdc shell uitest uiInput longClick point_x point_y                                               |
| fling       | 模拟快滑操作                              | from_x (必选参数,滑动起点x坐标)<br>from_y(必选参数,滑动起点y坐标)<br>to_x(必选参数,滑动终点x坐标)<br>to_y(必选参数,滑动终点y坐标)<br>swipeVelocityPps_ (可选参数,滑动速度,取值范围: 200-40000, 默认值: 600, 单位: px/s)<br>stepLength(可选参数,滑动步长,默认值:滑动距离/50, 单位: px) | hdc shell uitest uiInput fling from_x from_y to_x to_y swipeVelocityPps_ stepLength               |
| swipe       | 模拟慢滑操作                              | from_x (必选参数,滑动起点x坐标)<br>from_y(必选参数,滑动起点y坐标)<br>to_x(必选参数,滑动终点x坐标)<br>to_y(必选参数,滑动终点y坐标)<br>swipeVelocityPps_ (可选参数,滑动速度,取值范围: 200-40000, 默认值: 600, 单位: px/s) | hdc shell uitest uiInput swipe from_x from_y to_x to_y swipeVelocityPps_                         |
| drag        | 模拟拖拽操作                              | from_x (必选参数,拖拽起点x坐标)<br>from_y(必选参数,拖拽起点y坐标)<br>to_x(必选参数,拖拽终点x坐标)<br>to_y(必选参数,拖拽终点y坐标)<br>swipeVelocityPps_ (可选参数,滑动速度,取值范围: 200-40000, 默认值: 600, 单位: px/s) | hdc shell uitest uiInput drag from_x from_y to_x to_y swipeVelocityPps_                          |
| dircFling   | 模拟指定方向滑动操作                      | direction (可选参数,滑动方向,可选值: [0,1,2,3], 滑动方向: [左,右,上,下],默认值: 0)<br>swipeVelocityPps_ (可选参数,滑动速度,取值范围: 200-40000, 默认值: 600, 单位: px/s)<br>stepLength(可选参数,滑动步长,默认值:滑动距离/50, 单位: px) | hdc shell uitest uiInput dircFling direction swipeVelocityPps_ stepLength                        |
| inputText   | 模拟输入框输入文本操作                    | point_x (必选参数,输入框x坐标点)<br>point_y (必选参数,输入框y坐标点)<br>input(输入文本)                                                                           | hdc shell uitest uiInput inputText point_x point_y text                                          |
| keyEvent    | 模拟实体按键事件(如:键盘,电源键,返回上一级,返回桌面等),以及组合按键操作 | keyID (必选参数,实体按键对应ID)<br>keyID2 (可选参数,实体按键对应ID)                                                                                               | hdc shell uitest uiInput keyEvent keyID                                                         |

**举例**
```shell
//点击
hdc shell uitest uiInput click 100 100

//双击
hdc shell uitest uiInput doubleClick 100 100

//长按
hdc shell uitest uiInput longClick 100 100

//快滑
hdc shell uitest uiInput fling 10 10 200 200 500

//慢滑
hdc shell uitest uiInput swipe 10 10 200 200 500

//拖拽
hdc shell uitest uiInput drag 10 10 100 100 500

//左滑
hdc shell uitest uiInput dircFling 0 500

//右滑
hdc shell uitest uiInput dircFling 1 600

//上滑
hdc shell uitest uiInput dircFling 2

//下滑
hdc shell uitest uiInput dircFling 3

//输入框输入
hdc shell uitest uiInput inputText 100 100 hello

//返回主页
hdc shell uitest uiInput keyEvent Home

//返回上一步
hdc shell uitest uiInput keyEvent Back

//组合键粘贴操作
hdc shell uitest uiInput keyEvent 2072 2038
```


`keyEvent`映射表可以参考这个文档：https://docs.openharmony.cn/pages/v4.1/en/application-dev/reference/apis-input-kit/js-apis-keycode.md


# 屏幕截图
hdc提供了两种截图命令

方式一
```shell
$ hdc shell uitest screenCap
// 默认存储路径：/data/local/tmp，文件名：时间戳 + .png。

$ hdc shell uitest screenCap -p /data/local/tmp/1.png
// 指定存储路径和文件名。
```


【推荐】方式二
```shell
$ hdc shell snapshot_display -f /data/local/tmp/2.jpeg
// 截图完成后可以通过 hdc file recv 命令导入到本地
```

方式二的截图性能效率远远高于方式一

# 屏幕录屏
相关hdc命令还未支持，官方在开发中。。。

我这边通过python脚本实现了录屏功能，使用方法如下
```shell
cd awesome-hdc/scripts
pip3 install -r requirements.txt

python3 screen_recroding.py
```

# 打开Scheme (URL)
```shell
$ hdc shell aa start -U http://www.baidu.com
start ability successfully.

$ hdc shell aa start -U kwai://home

```

# 获取页面布局信息（控件树）
```shell
$ hdc shell uitest dumpLayout -p {saveDumpPath}   # 运行命令前需要手动打开app，进入对应页面

DumpLayout saved to:/data/local/tmp/layout_407568854.json
```
-  `-p`表示控件树保存的目录，如果不指定，则默认保存在手机的`/data/local/tmp`目录
`/data/local/tmp/layout_407568854.json`文件内容如下：
```shell
{
    "attributes": {
        "accessibilityId": "",
        "bounds": "[0,0][1260,2720]",
        "checkable": "",
        "checked": "",
        "clickable": "",
        "description": "",
        "enabled": "",
        "focused": "",
        "hostWindowId": "",
        "id": "",
        "key": "",
        "longClickable": "",
        "origBounds": "",
        "scrollable": "",
        "selected": "",
        "text": "",
        "type": ""
    },
    "children": [
    	
      ...
      
    ]
```


# 录制用户操作
将当前界面操作记录到`/data/local/tmp/layout/record.csv`，结束录制操作使用`Ctrl+C`结束录制
```shell
$  hdc shell uitest uiRecord record

windowBounds : (0,0,1260,2720)
Current ForAbility :com.kuaishou.hmapp, EntryAbility
The result will be written in csv file at location: /data/local/tmp/layout/record.csv
Started Recording Successfully...
click , fingerNumber:1 ,
	finger1:click:  at Point(x:557, y:1542) ; from Point(x:557, y:1542)  to Point(x:557, y:1542) ;
click , fingerNumber:1 ,
	finger1:click:  at Point(x:550, y:1638) ; from Point(x:550, y:1638)  to Point(x:550, y:1638) ;
fling , fingerNumber:1 ,
	finger1:from Point(x:409, y:1916)  to Point(x:370, y:1528) ; Off-hand speed:1415.42, Step length:34;
fling , fingerNumber:1 ,
	finger1:from Point(x:400, y:1886)  to Point(x:389, y:1586) ; Off-hand speed:1995.97, Step length:31;
home , fingerNumber:1 ,
	finger1:from Widget(id: , type: Text, text: state: didAppear,
 feedId: 5218827670987295481,
 feedType: 3,
 ServerExpTag: feed_photo|5218827670987295481|1499501607|1_u/2003373606202106162_bs54357,
 ) ;  to Point(x:615, y:2338) ;
```

支持两种方式查看数据:
- `uiRecord record`, 将事件的位置坐标写入文件
- `uiRecord read`,   将文件内容打印到控制台

录制完成后，再将`csv`文件拷贝到电脑上
```shell
$ hdc file recv  /data/local/tmp/layout/record.csv ~/record.csv
```

`record`数据字段含义请参考如下示例数据
```shell
{
  "ABILITY": "com.ohos.launcher.MainAbility", // 前台应用界面
  "BUNDLE": "com.ohos.launcher", // 操作应用
  "CENTER_X": "", // 模拟捏合中心X, pinch事件
  "CENTER_Y": "", // 模拟捏合中心Y, pinch事件
  "EVENT_TYPE": "pointer", //  
  "LENGTH": "0", // 总体步长
  "OP_TYPE": "click", //事件类型，当前支持点击、双击、长按、拖拽、捏合、滑动、抛滑动作录制
  "VELO": "0.000000", // 离手速度
  "direction.X": "0.000000",// 总体移动X方向
  "direction.Y": "0.000000", // 总体移动Y方向
  "duration": 33885000.0, // 手势操作持续时间
  "fingerList": [{
      "LENGTH": "0", // 总体步长
      "MAX_VEL": "40000", // 最大速度
      "VELO": "0.000000", // 离手速度
      "W1_BOUNDS": "{"bottom":361,"left":37,"right":118,"top":280}", // 起点控件bounds
      "W1_HIER": "ROOT,3,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0", // 起点控件hierarchy
      "W1_ID": "", // 起点控件id
      "W1_Text": "", // 起点控件text
      "W1_Type": "Image", // 起点控件类型
      "W2_BOUNDS": "{"bottom":361,"left":37,"right":118,"top":280}", // 终点控件bounds
      "W2_HIER": "ROOT,3,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0", // 终点控件hierarchy
      "W2_ID": "", // 终点控件id
      "W2_Text": "", // 终点控件text
      "W2_Type": "Image", // 终点控件类型
      "X2_POSI": "47", // 终点X
      "X_POSI": "47", // 起点X
      "Y2_POSI": "301", // 终点Y
      "Y_POSI": "301", // 起点Y
      "direction.X": "0.000000", // x方向移动量
      "direction.Y": "0.000000" // Y方向移动量
  }],
  "fingerNumber": "1" //手指数量
}
```

# 系统日志（log）
```shell
$ hdc hilog -h

Usage:
-h --help
  Show all help information.
  Show single help information with option:
  query/clear/buffer/stats/persist/private/kmsg/flowcontrol/baselevel/domain/combo
Querying logs options:
  No option performs a blocking read and keeps printing.
  -x --exit
    Performs a non-blocking read and exits when all logs in buffer are printed.
  -a <n>, --head=<n>
    Show n lines logs on head of buffer.
  -z <n>, --tail=<n>
    Show n lines logs on tail of buffer.
  -t <type>, --type=<type>
    Show specific type/types logs with format: type1,type2,type3
    Don't show specific type/types logs with format: ^type1,type2,type3
    Type coule be: app/core/init/kmsg, kmsg can't combine with others.
    Default types are: app,core,init.
  -L <level>, --level=<level>
    Show specific level/levels logs with format: level1,level2,level3
    Don't show specific level/levels logs with format: ^level1,level2,level3
    Long and short level string are both accepted
    Long level string coule be: DEBUG/INFO/WARN/ERROR/FATAL.
    Short level string coule be: D/I/W/E/F.
    Default levels are all levels.
  -D <domain>, --domain=<domain>
    Show specific domain/domains logs with format: domain1,domain2,doman3
    Don't show specific domain/domains logs with format: ^domain1,domain2,doman3
    Max domain count is 5.
    See domain description at the end of this message.
  -T <tag>, --tag=<tag>
    Show specific tag/tags logs with format: tag1,tag2,tag3
    Don't show specific tag/tags logs with format: ^tag1,tag2,tag3
    Max tag count is 10.
  -P <pid>, --pid=<pid>
    Show specific pid/pids logs with format: pid1,pid2,pid3
    Don't show specific domain/domains logs with format: ^pid1,pid2,pid3
    Max pid count is 5.
  -e <expr>, --regex=<expr>
    Show the logs which match the regular expression <expr>.
  -v <format>, --format=<format>
    Show logs in different formats, options are:
      color or colour      display colorful logs by log level.i.e.
        DEBUG        INFO        WARN        ERROR       FATAL
      time format options are(single accepted):
        time       display local time, this is default.
        epoch      display the time from 1970/1/1.
        monotonic  display the cpu time from bootup.
      time accuracy format options are(single accepted):
        msec       display time by millisecond, this is default.
        usec       display time by microsecond.
        nsec       display time by nanosecond.
      year       display the year when -v time is specified.
      zone       display the time zone when -v time is specified.
    Different types of formats can be combined, such as:
    -v color -v time -v msec -v year -v zone.
-r
  Remove all logs in hilogd buffer, advanced option:
  -t <type>, --type=<type>
    Remove specific type/types logs in buffer with format: type1,type2,type3
    Type coule be: app/core/init/kmsg.
    Default types are: app,core
-g
  Query hilogd buffer size, advanced option:
  -t <type>, --type=<type>
    Query specific type/types buffer size with format: type1,type2,type3
    Type coule be: app/core/init/kmsg.
    Default types are: app,core
-G <size>, --buffer-size=<size>
  Set hilogd buffer size, <size> could be number or number with unit.
  Unit could be: B/K/M/G which represents Byte/Kilobyte/Megabyte/Gigabyte.
  <size> range: [64.0K,64.0K].
  Advanced option:
  -t <type>, --type=<type>
    Set specific type/types log buffer size with format: type1,type2,type3
    Type coule be: app/core/init/kmsg.
    Default types are: app,core
  **It's a persistant configuration**
-s, --statistics
  Query log statistic information.
  Set param persist.sys.hilog.stats true to enable statistic.
  Set param persist.sys.hilog.stats.tag true to enable statistic of log tag.
-S
  Clear hilogd statistic information.
-w <control>,--write=<control>
  Log persistance task control, options are:
    query      query tasks informations
    stop       stop all tasks
    start      start one task
    clear      clear /data/log/hilog/hilog*.gz
  Persistance task is used for saving logs in files.
  The files are saved in directory: /data/log/hilog/
  Advanced options:
  -f <filename>, --filename=<filename>
    Set log file name, name should be valid of Linux FS.
  -l <length>, --length=<length>
    Set single log file size. <length> could be number or number with unit.
    Unit could be: B/K/M/G which represents Byte/Kilobyte/Megabyte/Gigabyte.
    <length> range: [64.0K, 512.0M].
  -n <number>, --number<number>
    Set max log file numbers, log file rotate when files count over this number.
    <number> range: [2, 1000].
  -m <compress algorithm>,--stream=<compress algorithm>
    Set log file compressed algorithm, options are:
      none       write file with non-compressed logs.
      zlib       write file with zlib compressed logs.
  -j <jobid>, --jobid<jobid>
    Start/stop specific task of <jobid>.
    <jobid> range: [10, 0xffffffff).
  User can start task with options (t/L/D/T/P/e/v) as if using them when "Query logs" too.
  **It's a persistant configuration**
-p <on/off>, --privacy <on/off>
  Set HILOG api privacy formatter feature on or off.
  **It's a temporary configuration, will be lost after reboot**
-k <on/off>, --kmsg <on/off>
  Set hilogd storing kmsg log feature on or off
  **It's a persistant configuration**
-Q <control-type>
  Set log flow-control feature on or off, options are:
    pidon     process flow control on
    pidoff    process flow control off
    domainon  domain flow control on
    domainoff domain flow control off
  **It's a temporary configuration, will be lost after reboot**
-b <loglevel>, --baselevel=<loglevel>
  Set global loggable level to <loglevel>
  Long and short level string are both accepted.
  Long level string coule be: DEBUG/INFO/WARN/ERROR/FATAL/X.
  Short level string coule be: D/I/W/E/F/X.
  X means that loggable level is higher than the max level, no log could be printed.
  Advanced options:
  -D <domain>, --domain=<domain>
    Set specific domain loggable level.
    See domain description at the end of this message.
  -T <tag>, --tag=<tag>
    Set specific tag loggable level.
    The priority is: tag level > domain level > global level.
  **It's a temporary configuration, will be lost after reboot**
The first layer options can't be used in combination, ILLEGAL expamples:
    hilog -S -s; hilog -w start -r; hilog -p on -k on -b D


Domain description:
  Log type "core" & "init" are used for OS subsystems, the range is [0xd000000,  0xd0fffff]
  Log type "app" is used for applications, the range is [0x0,  0xffff]
  To reduce redundant info when printing logs, only last five hex numbers of domain are printed
  So if user wants to use -D option to filter OS logs, user should add 0xD0 as prefix to the printed domain:
  Exapmle: hilog -D 0xD0xxxxx
  The xxxxx is the domain string printed in logs.


Dictionary description:
-d <path>, --dictionary=<path>
  Set elf file path, name should be valid of Linux FS.
  Rescan the elf file in the system to generate a full data dictionary file

```

# 导出日志
```shell
$ hdc file recv data/log/hilog/ ./

```
# 导出crash日志
```shell
hdc file recv data/log/faultlog/faultlogger/ ./

```

# hidumper工具
```shell
$ hdc shell hidumper -h

usage:
  -h                          |help text for the tool
  -lc                         |a list of system information clusters
  -ls                         |a list of system abilities
  -c                          |all system information clusters
  -c [base system]            |system information clusters labeled "base" and "system"
  -s                          |all system abilities
  -s [SA0 SA1]                |system abilities labeled "SA0" and "SA1"
  -s [SA] -a ['-h']           |system ability labeled "SA" with arguments "-h" specified
  -e                          |faultlogs of crash history
  --net [pid]                 |dump network information; if pid is specified, dump traffic usage of specified pid
  --storage [pid]             |dump storage information; if pid is specified, dump /proc/pid/io
  -p                          |processes information, include list and information of processes and threads
  -p [pid]                    |dump threads under pid, includes smap, block channel, execute time, mountinfo
  --cpuusage [pid]            |dump cpu usage by processes and category; if PID is specified, dump category usage of specified pid
  --cpufreq                   |dump real CPU frequency of each core
  --mem [pid]                 |dump memory usage of total; dump memory usage of specified pid if pid was specified
  --zip                       |compress output to /data/log/hidumper
  --mem-smaps pid [-v]        |display statistic in /proc/pid/smaps, use -v specify more details
  --mem-jsheap pid [-T tid] [--gc]  |triggerGC and dumpHeapSnapshot under pid and tid
```

## list system abilities
```shell
$ hdc shell hidumper -ls

System ability list:
SystemAbilityManager             RenderService                    AbilityManagerService            
DataObserverMgr                  UriPermissionMgr                 AccountMgr                       
BundleMgr                        FormMgr                          ApplicationManagerService        
AccessibilityManagerService      UserIdmService                   UserAuthService                  
AuthExecutorMgrService           PinAuthService                   FaceAuthService                  
FingerprintAuthService           WifiDevice                       WifiHotspot                      
WifiP2p                          WifiScan                         1125                             
1126                             NetConnManager                   NetPolicyManager                 
NetStatsManager                  NetTetheringManager              VPNManager                       
EthernetManager                  NetsysNative                     NetsysExtService                 
DistributedNet                   1181                             HiviewService                    
HiviewFaultLogger                HiviewSysEventService            1204                             
XperfTraceService                HiDumperService                  XpowerManager                    
HiDumperCpuService               DistributedKvData                ContinuationManagerService       
ResourceSched                    BackgroundTaskManager            WorkSchedule                     
ComponentSchedServer             SocPerfService                   DeviceUsageStatistics            
MemoryManagerService             SuspendManager                   AbnormalEfficiencyManager        
ConcurrentTaskService            ResourceQuotaControl             DeviceStandbyService             
TaskHeartbeatMgrService          2901                             DeviceStatusService              
2903                             2904                             2908                             
AudioDistributed                 PlayerDistributedService         CameraService                    
AudioPolicyService               AVSessionService                 AVCodecService                   
MediaKeySystemService            MultimodalInput                  DistributedNotificationService   
CommonEventService               PowerManagerService              BatteryService                   
ThermalService                   BatteryStatisticsService         DisplayPowerManagerService       
AccessTokenManagerService        PrivacyManagerService            KeystoreService                  
DeviceThreatDetectionService     RiskAnalysisManagerService       DataCollectManagerService        
DlpCreService                    SensorService                    MiscDeviceService                
PasteboardService                TimeService                      InputMethodService               
ScreenlockService                WallpaperManagerService          ParamWatcher                     
TelephonyCallManager             TelephonyCellularCall            TelephonyCellularData            
TelephonySmsMms                  TelephonyStateRegistry           TelephonyCoreService             
4011                             TelephonyIms                     ModuleUpdateService              
UsbService                       WindowManagerService             DisplayManagerService            
DSoftbus                         DeviceAuthService                DeviceManagerService             
StorageDaemon                    StorageManager                   HdfDeviceServiceManager          
CloudFileDaemonService           EcologicalRuleManager            UiService                        
UiAppearanceService              CaDaemon                         AssetService                     
9527                             65537                            65570                            
65728                            65777                            65830                            
65850                            65888                            65904                            
65926                            65958                            65962                            
66070                            66090                            70633  
```

获取到abilities后，就可以指定service获取相关的信息。 比如通过RenderService获取一些信息
```shell
$ hdc shell hidumper -s RenderService             

-------------------------------[ability]-------------------------------


----------------------------------RenderService---------------------------------
------Graphic2D--RenderSerice ------
Usage:
 h                             |help text for the tool
screen                         |dump all screen infomation in the system
surface                        |dump all surface information
composer fps                   |dump the fps info of composer
[surface name] fps             |dump the fps info of surface
composer fpsClear              |clear the fps info of composer
[windowname] fps               |dump the fps info of window
[windowname] hitchs            |dump the hitchs info of window
[surface name] fpsClear        |clear the fps info of surface
nodeNotOnTree                  |dump nodeNotOnTree info
allSurfacesMem                 |dump surface mem info
RSTree                         |dump RSTree info
EventParamList                 |dump EventParamList info
allInfo                        |dump all info
dumpMem                        |dump Cache
trimMem cpu/gpu/shader         |release Cache
surfacenode [id]               |dump node info
fpsCount                       |dump the refresh rate counts info
clearFpsCount                  |clear the refresh rate counts info
```

## RenderService
**获取分辩率**
```shell
$ hdc shell hidumper -s RenderService -a screen 

-------------------------------[ability]-------------------------------


----------------------------------RenderService---------------------------------
-- ScreenInfo
screen[0]: id=0, powerstatus=POWER_STATUS_OFF, backlight=21, screenType=EXTERNAL_TYPE, render size: 1260x2720, physical screen resolution: 1260x2720, isvirtual=false, skipFrameInterval_:1

  supportedMode[0]: 1260x2720, refreshrate=120
  supportedMode[1]: 1260x2720, refreshrate=90
  supportedMode[2]: 1260x2720, refreshrate=60
  supportedMode[3]: 1260x2720, refreshrate=30
  activeMode: 1260x2720, refreshrate=60
  capability: name=, phywidth=72, phyheight=156,supportlayers=12, virtualDispCount=0, propCount=0, type=DISP_INTF_HDMI, supportWriteBack=false
```


**获取帧率**
首先执行如下命令进入到shell环境
```shell
$ hdc shell
```
然后执行`hidumper [surface name] fps` , 例如`composer fps`

```
$ hidumper -s RenderService -a "composer fps"

-------------------------------[ability]-------------------------------


----------------------------------RenderService---------------------------------

-- The recently fps records info of screens:

The fps of screen [Id:0] is:
107537646652857
107537663200253
107537679747128
107537696352336
107537712846086
107537729390357
107537745974211
107537762468482
107537779015357
107537795561190
107537812110148
107537828651815
107537845349732
...
```

## DisplayManagerService
```shell
$ hdc shell hidumper -s DisplayManagerService

-------------------------------[ability]-------------------------------


----------------------------------DisplayManagerService----------------------------------
Usage:
 -h                             |help text for the tool
 -a                             |dump all screen information in the system
 -z                             |switch to fold half status
 -y                             |switch to expand status
 -p                             |switch to fold status
 -f                             |get to fold status
```



## PowerManagerService
```shell
$ hdc shell hidumper -s PowerManagerService

-------------------------------[ability]-------------------------------


----------------------------------PowerManagerService----------------------------------
Power manager dump options:
  [-h] [-runninglock]
  description of the cmd option:
    -a: show dump info of all power modules.
    -h: show this help.
    -r: show the information of runninglock.
    -s: show the information of power state machine.
    -d: show power off dialog.
```

例如上文提到的获取屏幕状态
```shell
$ hdc shell hidumper -s PowerManagerService -a -s
```

## BatteryService
```shell
$ hdc shell hidumper -s BatteryService

-------------------------------[ability]-------------------------------


----------------------------------BatteryService----------------------------------
Usage:
      -h: dump help
      -i: dump battery info
      -u: unplug battery charging state
      -r: reset battery state
      --capacity <capacity>: set battery capacity, the capacity range [0, 100]
      --uevent <uevent>: set battery uevent
```

例如上文提到的获取电量温度
```shell
$ hdc shell hidumper -s BatteryService -a -i                
```

## NetConnManager

```shell
$ hdc shell hidumper -s NetConnManager

-------------------------------[ability]-------------------------------


----------------------------------NetConnManager----------------------------------
Net connect Info:
	defaultNetSupplier_ is nullptr
	SupplierId:
	NetId: 0
	ConnStat: 0
	IsAvailable:
	IsRoaming: 0
	Strength: 0
	Frequency: 0
	LinkUpBandwidthKbps: 0
	LinkDownBandwidthKbps: 0
	Uid: 0
Dns result Info:
	netId: 0
	totalReports: 2
	failReports: 2
```

## MemoryManagerService
```shell
$ hdc shell hidumper -s MemoryManagerService

-------------------------------[ability]-------------------------------


----------------------------------MemoryManagerService----------------------------------
Usage:
-h                          |help for memmgrservice dumper
-a                          |dump all info
-e                          |dump event observer
-r                          |dump reclaim info and adj
-c                          |dump config
-m                          |show malloc state
-minisys                    |show mini system information for each service
-s                          |show subscriber all the pid which can be reclaimed
-d {pid} {uid} {state}      |trigger appstate change

-t                          trigger memory onTrim:
-t 1 ---------------------- level_purgeable
-t 2 ---------------------- level_moderate
-t 3 ---------------------- level_low
-t 4 ---------------------- level_critical

-f                          trigger purgeable memory Reclaim:
-f 1 ---------------------  purg_heap all
-f 2 ---------------------  purg_ashmem all
-f 3 ---------------------  purg_subscriber all
-f 4 ---------------------  purg all purgeable memory
-f 1 -id {uid} {size} ----- purg_heap by memCG and size(KB). if input uid is 0, reclaim system_lru
-f 2 -id {ashmId} {time} -- purg_ashmem by ashmId, which can get from /proc/purgeable_ashmem_trigger
-f 3 -id {pid} ------------ purg_subscriber by pid. if input pid is 0, recalim subscriber all

Please check your command.
```


## StorageManager
TODO


# aa工具
Ability assistant（Ability助手，简称为aa），是实现应用及测试用例启动功能的工具，为开发者提供基本的应用调试和测试能力，例如启动应用组件、强制停止进程、打印应用组件相关信息等。


```shell
$ hdc shell aa help
usage: aa <command> <options>
These are common aa commands list:
  help                        list available commands
  start                       start ability with options
  stop-service                stop service with options
  dump                        dump the ability info
  force-stop <bundle-name>    force stop the process with bundle name
  attach                      attach application to enter debug mdoe
  detach                      detach application to exit debug mode
  test                        start the test framework with options
  appdebug                    set / cancel / get waiting debug status
```

## start
## stop-service
## force-stop
## test
## attach
## detach
## appdebug
详细介绍请参考文档：https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/tools/aa-tool.md

# bm工具
Bundle Manager（包管理工具，简称bm）是实现应用安装、卸载、更新、查询等功能的工具，bm为开发者提供基本的应用安装包的调试能力，例如：安装应用，卸载应用，查询安装包信息等。
```
$ hdc shell bm help
usage: bm <command> <options>
These are common bm commands list:
  help         list available commands
  install      install a bundle with options
  uninstall    uninstall a bundle with options
  dump         dump the bundle info
  get          obtain device udid
  quickfix     quick fix, including query and install
  compile      Compile the software package
  dump-overlay dump overlay info of the specific overlay bundle
  dump-target-overlay dump overlay info of the specific target bundle
  dump-dependencies dump dependencies by given bundle name and module name
  dump-shared dump inter-application shared library information by bundle name
  clean        clean the bundle data
```

## install
## uninstall
## dump
## clean
## enable
## disable
## get

详细介绍请参考文档：https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/tools/bm-tool.md

# param工具
param是为开发人员提供用于操作系统参数的工具，该工具只支持标准系统。
```shell
$ hdc shell param                                   
Command list:
    param ls [-r] [name]                            --display system parameter
    param get [name]                                --get system parameter
    param set name value                            --set system parameter
    param wait name [value] [timeout]               --wait system parameter
    param dump [verbose]                            --dump system parameter
    param shell [-p] [name] [-u] [username] [-g] [groupname]    --shell system parameter
    param save    
```

详细介绍请参考文档：https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/tools/param-tool.md


# Instrument Test
主要用来做APP 的UI自动化测试，将应用测试包安装到测试设备上，在cmd窗口中执行aa命令，完成对用例测试。

`aa test`命令执行配置参数

| 执行参数全写  | 执行参数缩写 | 执行参数含义                              | 执行参数示例                                                |
|---------------|--------------|-------------------------------------------|-------------------------------------------------------------|
| --bundleName  | -b           | 应用 Bundle 名称                          | -b com.test.example                                         |
| --packageName | -p           | 应用模块名，适用于 FA 模型应用            | -p com.test.example.entry                                   |
| --moduleName  | -m           | 应用模块名，适用于 STAGE 模型应用         | -m entry                                                    |
| NA            | -s           | 特定参数，以 <key, value> 键值对方式传入  | -s unittest /ets/testrunner/OpenHarmonyTestRunner           |


```shell
$ hdc shell aa test -h
usage: aa test <options>
options list:
  -h, --help                                             list available commands
  -b <bundle-name> -s unittest <test-runner>             start the test framework with options
                  [-p <package-name>]                    the name of package with test-runner, required for the FA model
                  [-m <module-name>]                     the name of module with test-runner, required for the STAGE model
                  [-s class <test-class>]
                  [-s level <test-level>]
                  [-s size <test-size>]
                  [-s testType <test-testType>]
                  [-s timeout <test-timeout>]
                  [-s <any-key> <any-value>]
                  [-w <wait-time>]
                  [-D]
```

**举例**
```shell
$ hdc shell aa test -b com.example.myapplication -m entry_test -s unittest /ets/testrunner/OpenHarmonyTestRunner -s class UiTestDemo timeout 15000
```
查看测试结果
cmd模式执行过程,会打印如下相关日志信息。
```shell
OHOS_REPORT_STATUS: class=testStop
OHOS_REPORT_STATUS: current=1
OHOS_REPORT_STATUS: id=JS
OHOS_REPORT_STATUS: numtests=447
OHOS_REPORT_STATUS: stream=
OHOS_REPORT_STATUS: test=stop_0
OHOS_REPORT_STATUS_CODE: 1

OHOS_REPORT_STATUS: class=testStop
OHOS_REPORT_STATUS: current=1
OHOS_REPORT_STATUS: id=JS
OHOS_REPORT_STATUS: numtests=447
OHOS_REPORT_STATUS: stream=
OHOS_REPORT_STATUS: test=stop_0
OHOS_REPORT_STATUS_CODE: 0
OHOS_REPORT_STATUS: consuming=4

OHOS_REPORT_RESULT: stream=Tests run: 447, Failure: 0, Error: 1, Pass: 201, Ignore: 245
OHOS_REPORT_CODE: 0

OHOS_REPORT_RESULT: breakOnError model, Stopping whole test suite if one specific test case failed or error
OHOS_REPORT_STATUS: taskconsuming=16029
```

# 性能工具
`SmartPerf`是一款基于系统开发的性能功耗测试工具，操作简单易用。工具可以检测性能、功耗相关指标，包括`FPS`、`CPU`、`GPU`、`RAM`、`Temp`等，通过量化的指标项了解应用性能状况。在开发过程中，使用的可能是有屏或无屏设备，对此`SmartPerf`提供了两种方式：分别是`SmartPerf-Device`和`SmartPerf-Daemon`。`SmartPerf-Device`适用于有屏设备，支持可视化操作。测试时是通过悬浮窗的开始和暂停来实时展示性能指标数据，保存后可生成数据报告，在报告中可分析各指标数据详情。`SmartPerf-Daemon`支持`shell命令行`方式，同时适用于有屏和无屏设备。

- CPU：每秒读取一次设备节点下CPU大中小核的频点和各核使用率，衡量应用占用CPU资源的情况，占用过多的CPU资源会导致芯片发烫。
- GPU：每秒读取一次设备节点下GPU的频点和负载信息，衡量应用占用GPU资源的情况，当GPU占用过多时，会导致性能下降，应用程序的运行速度变慢。
- FPS：应用界面每秒刷新次数，衡量应用画面的流畅度，FPS越高表示图像流畅度越好，用户体验也越好。
- POWER：每秒读取一次设备节点下的电流及电压信息。
- TEMP：每秒读取一次设备节点下电池温度、系统芯片温度等信息。
- RAM：每秒读取一次应用进程的实际物理内存，衡量应用的内存占比情况。
- snapshot：每秒截取一张应用界面截图。
```shell
$ hdc shell

# SP_daemon

// 查看daemon进程是否存在
# ps -ef | grep SP_daemon
root          1584     1 0 21:50:05 ?     00:00:00 SP_daemon
root          1595  1574 3 21:51:02 pts/0 00:00:00 grep SP_daemon

```
执行查看帮助命令
```shell
# SP_daemon --help
OpenHarmony performance testing tool SmartPerf command-line version
Usage: SP_daemon [options] [arguments]

options:
 -N             set the collection times(default value is 0) range[1,2147483647], for example: -N 10
 -PKG           set package name, must add, for example: -PKG ohos.samples.ecg
 -c             get device CPU frequency and CPU usage, process CPU usage and CPU load ..
 -g             get device GPU frequency and GPU load
 -f             get app refresh fps(frames per second) and fps jitters and refreshrate
 -profilerfps   get refresh fps and timestamp
 -sections      set collection time period(using with profilerfps)
 -t             get remaining battery power and temperature..
 -p             get battery power consumption and voltage
 -r             get process memory and total memory
 -snapshot      get screen capture
 -net           get uplink and downlink traffic
 -start         collection start command
 -stop          collection stop command
 -VIEW          set layler, for example: -VIEW DisplayNode
 -screen        get screen resolution
 -OUT           set csv output path.
 -d             get device DDR information
 -m             get other memory
example:
SP_daemon -N 20 -c -g -t -p -r -m -net -snapshot -d
SP_daemon -N 20 -PKG ohos.samples.ecg -c -g -t -p -f -r -m -net -snapshot -d
SP_daemon -start -c
SP_daemon -stop
SP_daemon -screen
```

基于`hdc`命令行的`SmartPerf`性能工具使用详细文档参考这个：https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/application-test/smartperf-guidelines.md

# 参考链接
- https://gitee.com/openharmony/developtools_hdc
- https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V2/ide-command-line-hdc-0000001237908229-V2#section116322265308
- https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/application-test/smartperf-guidelines.md
- https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/tools/aa-tool.md
- https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/tools/bm-tool.md
- https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/tools/param-tool.md
- https://github.com/mzlogin/awesome-adb


