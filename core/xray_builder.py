# core/xray_builder.py
import uuid
import random
import string

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def build_xray_inbound(port, protocol, transport, security, tag=None, **kwargs):
    """
    Собирает inbound конфигурацию Xray на основе независимых параметров.
    protocol: vless, vmess, trojan, shadowsocks, socks, http, wireguard, hysteria2, tuic
    transport: tcp, mkcp, ws, grpc, httpupgrade, xhttp, hysteria
    security: none, tls, reality
    """
    tag = tag or f"{protocol}_{transport}_{security}_{port}"
    
    # Базовая настройка протокола
    protocol_settings = {}
    if protocol == 'vless':
        protocol_settings = {
            "clients": [{"id": str(uuid.uuid4()), "flow": "xtls-rprx-vision" if security == 'reality' else ""}],
            "decryption": "none"
        }
    elif protocol == 'vmess':
        protocol_settings = {
            "clients": [{"id": str(uuid.uuid4()), "alterId": 0}]
        }
    elif protocol == 'trojan':
        protocol_settings = {
            "clients": [{"password": generate_random_string(12)}]
        }
    elif protocol == 'shadowsocks':
        protocol_settings = {
            "method": kwargs.get('ss_method', '2022-blake3-aes-128-gcm'),
            "password": kwargs.get('ss_password', generate_random_string(16)),
            "network": "tcp,udp"
        }
    elif protocol == 'hysteria2':
        protocol_settings = {
            "password": kwargs.get('hy_password', generate_random_string(16)),
            "users": [{"password": generate_random_string(16)}] # Упрощенно для примера
        }
    # ... (аналогично добавляются socks, http, wireguard, tuic)

    # Настройка транспорта (Stream Settings)
    stream_settings = {"network": transport}
    
    if transport == 'ws':
        stream_settings["wsSettings"] = {"path": kwargs.get('path', f"/{generate_random_string(8)}"), "headers": {"Host": kwargs.get('host', "")}}
    elif transport == 'grpc':
        stream_settings["grpcSettings"] = {"serviceName": kwargs.get('service_name', "grpc")}
    elif transport == 'xhttp':
        stream_settings["xhttpSettings"] = {"path": kwargs.get('path', f"/{generate_random_string(8)}"), "mode": "auto"}
    elif transport == 'mkcp':
        stream_settings["kcpSettings"] = {"uplinkCapacity": 100, "downlinkCapacity": 100, "congestion": True}
    elif transport == 'httpupgrade':
        stream_settings["httpupgradeSettings"] = {"path": kwargs.get('path', "/"), "host": kwargs.get('host', "")}
    
    # Настройка безопасности
    if security == 'tls':
        stream_settings["security"] = "tls"
        stream_settings["tlsSettings"] = {
            "serverName": kwargs.get('sni', ""),
            "certificates": [{"certificateFile": kwargs.get('cert_file', "/etc/xray/cert.pem"), "keyFile": kwargs.get('key_file', "/etc/xray/key.pem")}]
        }
    elif security == 'reality':
        stream_settings["security"] = "reality"
        stream_settings["realitySettings"] = {
            "show": False,
            "dest": kwargs.get('reality_dest', "www.microsoft.com:443"),
            "serverNames": [kwargs.get('reality_sni', "www.microsoft.com")],
            "privateKey": kwargs.get('reality_private_key', ""), # Генерируется отдельно через xray x25519
            "shortIds": [kwargs.get('reality_short_id', generate_random_string(8))]
        }
    else:
        stream_settings["security"] = "none"

    # Формирование итогового inbound
    inbound = {
        "tag": tag,
        "port": port,
        "protocol": protocol,
        "settings": protocol_settings,
        "streamSettings": stream_settings,
        "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}
    }
    
    # Особая обработка для Hysteria2 (требует специфичных полей вне streamSettings в некоторых версиях)
    if protocol == 'hysteria2':
        inbound["settings"]["upMbps"] = kwargs.get('up_mbps', 100)
        inbound["settings"]["downMbps"] = kwargs.get('down_mbps', 100)

    return inbound
