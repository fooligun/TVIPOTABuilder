import os, shutil, urllib.request, sys
rootDir = os.path.dirname(__file__) + "/firmware"
provisionUrl = "raduga.tv/download/tvip"
shutil.rmtree(rootDir, True)
os.mkdir(rootDir, 0o777)
os.chdir(rootDir)

signPackageUrl = "http://update.tvip.ru/utils/sign_tools.tgz"
urllib.request.urlretrieve(signPackageUrl, rootDir + "/sign.tgz")
os.system("tar zxvf " + rootDir + "/sign.tgz")
signApk = rootDir + "/signapk.jar"
signPem = rootDir + "/key.x509.pem"
signPk8 = rootDir + "/key.pk8"

dirs = {
    "s410": {
        "linux-qt": ["beta", "release"],
        "android": ["beta", "release"]
    },
    "s412": {
        "linux-qt": ["beta", "release"],
        "android": ["beta", "release"]
    }
}

for stb in dirs:
    stbDir = rootDir + "/" + stb
    os.mkdir(stbDir, 0o777)
    for systems in dirs.get(stb):
        systemDir = stbDir + "/" + systems
        os.mkdir(systemDir, 0o777)
        for versions in dirs.get(stb).get(systems):
            versionDir = systemDir + "/" + versions
            os.mkdir(versionDir, 0o777)
            os.chdir(versionDir)

            #download ota
            downloadUrl = "http://update.tvip.ru/stb/" + stb + "/" + systems + "/" + versions + "/tvip_firmware.ota.zip"
            downloadFile = versionDir + "/def_tvip_firmware.ota.zip"
            urllib.request.urlretrieve(downloadUrl, downloadFile)

            #change configs files
            os.mkdir("firmware", 0o777)
            os.system("unzip -o -q " + downloadFile + " -d firmware")
            systemsConfigsPath = versionDir + "/firmware/system/etc/"
            open(systemsConfigsPath + 'default_provision_server', 'w').write(provisionUrl)
            open(systemsConfigsPath + 'default_update_server', 'w').write(provisionUrl)
            osVersion = open(systemsConfigsPath + 'tvip_firmware.version').read()
            open(versionDir + "/tvip_firmware.info","w").write(osVersion + "\r\n#end#")

            #pack and sign
            os.chdir(versionDir + "/firmware")
            os.system("zip -r ../unsigned_tvip_firmware.ota.zip .")
            os.chdir(versionDir)
            os.system("java -jar " + signApk + " -w " + signPem + " " + signPk8 + " unsigned_tvip_firmware.ota.zip tvip_firmware.ota.zip")

            #remove temp files
            shutil.rmtree(versionDir + "/firmware", True)
            os.remove(versionDir + "/unsigned_tvip_firmware.ota.zip")
            os.remove(versionDir + "/def_tvip_firmware.ota.zip")
sys.exit()