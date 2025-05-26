#!/usr/bin/env python3
import os
import subprocess
import urllib.request
import shutil

# === KONFIGURASI ===
KERNEL_SOURCE_URL = "https://github.com/realme-kernel-opensource/realmeC2-AndroidQ_kernel-source.git"
CONFIG_URL = "https://github.com/synnaulaid/realmeC2_config/raw/refs/heads/master/config.gz"
NDK_ZIP_URL = "https://dl.google.com/android/repository/android-ndk-r21e-linux-x86_64.zip"

NDK_ZIP_FILE = "android-ndk-r21e.zip"
NDK_DIR = os.path.abspath("android-ndk-r21e")
TOOLCHAIN_PATH = f"{NDK_DIR}/toolchains/llvm/prebuilt/linux-x86_64/bin"
CROSS_COMPILE = "aarch64-linux-android-"
ARCH = "arm64"
KERNEL_DIR = "realme_kernel"
DRIVER_DIR = "mt7601u"

def run(cmd, cwd=None, env=None):
    print(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd, env=env)

def download_file(url, dst):
    print(f"[+] Downloading: {url}")
    urllib.request.urlretrieve(url, dst)
    print(f"[✓] Saved to: {dst}")

def setup_ndk():
    if not os.path.isdir(NDK_DIR):
        download_file(NDK_ZIP_URL, NDK_ZIP_FILE)
        run(f"unzip -q {NDK_ZIP_FILE}")
    else:
        print("[i] NDK sudah tersedia.")
    os.environ["PATH"] = f"{TOOLCHAIN_PATH}:" + os.environ["PATH"]
    print("[+] NDK toolchain added to PATH.")

def clone_kernel():
    if not os.path.exists(KERNEL_DIR):
        run(f"git clone {KERNEL_SOURCE_URL} {KERNEL_DIR}")
    else:
        print("[i] Kernel source sudah ada.")

def get_config():
    config_path = os.path.join(KERNEL_DIR, "config.gz")
    if not os.path.isfile(config_path):
        download_file(CONFIG_URL, config_path)
    run("zcat config.gz > .config", cwd=KERNEL_DIR)

def prepare_kernel():
    env = os.environ.copy()
    env["ARCH"] = ARCH
    env["SUBARCH"] = ARCH
    env["CROSS_COMPILE"] = f"{TOOLCHAIN_PATH}/{CROSS_COMPILE}"
    env["CC"] = f"{TOOLCHAIN_PATH}/clang"
    env["CLANG_TRIPLE"] = "aarch64-linux-android-"
    env["LLVM"] = "1"

    run("make LLVM=1 olddefconfig", cwd=KERNEL_DIR, env=env)
    run("make LLVM=1 prepare", cwd=KERNEL_DIR, env=env)
    run("make LLVM=1 modules_prepare", cwd=KERNEL_DIR, env=env)

def build_driver():
    if not os.path.exists(DRIVER_DIR):
        run(f"git clone https://github.com/terence-deng/mt7601u.git {DRIVER_DIR}")
    
    env = os.environ.copy()
    env["ARCH"] = ARCH
    env["SUBARCH"] = ARCH
    env["CROSS_COMPILE"] = f"{TOOLCHAIN_PATH}/{CROSS_COMPILE}"
    env["CC"] = f"{TOOLCHAIN_PATH}/clang"
    env["CLANG_TRIPLE"] = "aarch64-linux-android-"
    env["LLVM"] = "1"
    env["KERNELDIR"] = os.path.abspath(KERNEL_DIR)

    run(f"make -C {env['KERNELDIR']} M=$(pwd) ARCH={ARCH} CROSS_COMPILE={CROSS_COMPILE} modules", cwd=DRIVER_DIR, env=env)

def main():
    print("=== AUTO BUILD MT7601U.ko UNTUK ANDROID ARM64 ===\n")
    setup_ndk()
    clone_kernel()
    get_config()
    prepare_kernel()
    build_driver()
    print("\n[✓] Build selesai. File: mt7601u/mt7601u.ko")

if __name__ == "__main__":
    main()
