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

def run(cmd, cwd=None):
    print(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

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
    if not os.path.exists("realme_kernel"):
        run(f"git clone {KERNEL_SOURCE_URL} realme_kernel")
    else:
        print("[i] Kernel source sudah ada.")

def get_config():
    config_path = os.path.join("realme_kernel", "config.gz")
    if not os.path.isfile(config_path):
        download_file(CONFIG_URL, config_path)
        run("zcat config.gz > .config", cwd="realme_kernel")
    else:
        print("[i] config.gz sudah tersedia.")

def prepare_kernel():
    run(f"make ARCH={ARCH} CROSS_COMPILE={CROSS_COMPILE} olddefconfig", cwd="realme_kernel")
    run(f"make ARCH={ARCH} CROSS_COMPILE={CROSS_COMPILE} prepare", cwd="realme_kernel")
    run(f"make ARCH={ARCH} CROSS_COMPILE={CROSS_COMPILE} modules_prepare", cwd="realme_kernel")

def build_driver():
    if not os.path.exists("mt7601u"):
        run("git clone https://github.com/terence-deng/mt7601u.git")
    run(f"make ARCH={ARCH} CROSS_COMPILE={CROSS_COMPILE} KERNELDIR=../realme_kernel", cwd="mt7601u")

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
