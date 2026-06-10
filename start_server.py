import os
import subprocess
import sys
import re
import glob

# --- Các hàm tự động quản lý cài đặt Java hệ thống của ông ---
def install_java_via_sdkman():
    sdkman_init_paths = ["/usr/local/sdkman/bin/sdkman-init.sh", os.environ.get("HOME", "") + "/.sdkman/bin/sdkman-init.sh"]
    sdkman_init = next((p for p in sdkman_init_paths if os.path.exists(p)), None)
    if not sdkman_init: return False
    try:
        print("[+] Dang doc danh sach phien ban Java tu SDKMAN...")
        cmd = f"bash -c 'source {sdkman_init} && sdk list java'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0: return False
        versions = list(dict.fromkeys(re.findall(r'\b(11\.[0-9a-zA-Z.-]+)\b', result.stdout))) or list(dict.fromkeys(re.findall(r'\b(8\.[0-9a-zA-Z.-]+)\b', result.stdout)))
        if versions:
            selected_version = next((v for v in versions if '-ms' in v or '-tem' in v), versions[0])
            print(f"[+] Dang tien hanh cai dat {selected_version} qua SDKMAN...")
            subprocess.run(f"bash -c 'source {sdkman_init} && yes | sdk install java {selected_version}'", shell=True)
            return True
    except Exception as e: print(f"[-] Loi SDKMAN: {e}")
    return False

def install_java_via_apt():
    try:
        print("[+] Dang thu cai dat OpenJDK 11 qua apt-get...")
        subprocess.run(["sudo", "apt-get", "update", "-y"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "apt-get", "install", "-y", "openjdk-11-jre-headless"], check=True)
        return True
    except Exception: return False

# Chuyển làm việc về đúng thư mục chứa script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
codespace_name = os.environ.get("CODESPACE_NAME")
port_domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")

print("=" * 70)
print("             MINECRAFT FORGE 1.16.5 SERVER LAUNCHER")
print("=" * 70)

if codespace_name:
    public_ip = f"{codespace_name}-25565.{port_domain}"
    print(f"\n[+] Phat hien dang chay trong GitHub Codespace!")
    print(f"[+] DIA CHI IP DE KET NOI (Minecraft Server IP):")
    print(f"    \033[92m\033[1m{public_ip}\033[0m")
else:
    print(f"\n[+] Dang chay o may local.")
    print(f"[+] IP ket noi: localhost:25565")

os.makedirs("crash-reports", exist_ok=True)
try:
    # Tìm Java hệ thống phù hợp (Forge 1.16.5 cần Java 8 hoặc 11)
    java_cmd = "java"
    if os.name == 'nt':
        patterns = ["C:\\Program Files\\Java\\jre1.8.*\\bin\\java.exe", "C:\\Program Files\\Java\\jdk1.8.*\\bin\\java.exe", "C:\\Program Files\\Java\\jre-11.*\\bin\\java.exe", "C:\\Program Files\\Java\\jdk-11.*\\bin\\java.exe"]
        paths = []
        for p in patterns: paths.extend(glob.glob(p))
        if paths: java_cmd = paths[0]
    else:
        patterns = ["/usr/local/sdkman/candidates/java/8*/bin/java", "/usr/local/sdkman/candidates/java/11*/bin/java", "/usr/lib/jvm/java-8*/bin/java", "/usr/lib/jvm/java-11*/bin/java"]
        paths = []
        for p in patterns: paths.extend(glob.glob(p))
        if paths: java_cmd = paths[0]
        else:
            if install_java_via_sdkman() or install_java_via_apt():
                for p in patterns: paths.extend(glob.glob(p))
                if paths: java_cmd = paths[0]

    # Khởi chạy trực tiếp file gốc với tham số cấu hình
    cmd = [java_cmd, "-Xms4G", "-Xmx8G", "-XX:+UseG1GC", "-jar", "forge-1.16.5-36.2.42.jar", "nogui"]
    print(f"[+] Lenh khoi chay: {' '.join(cmd)}")
    
    if os.name == 'nt' and java_cmd == "java":
        subprocess.run(cmd, shell=True)
    else:
        subprocess.run(cmd)

except KeyboardInterrupt:
    print("\n[!] Dang tat server...")
except Exception as e:
    print(f"[!] Loi: {e}")