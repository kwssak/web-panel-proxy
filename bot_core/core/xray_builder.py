# core/xray_builder.py
import uuid
import random
import string
import json

def generate_random_string(length=12):
    """Генерация случайной строки"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_uuid():
    """Генерация UUID"""
    return str(uuid.uuid4())

def build_xray_inbound(port, protocol, transport, security, tag=None, **kwargs):
    """
    Сборка inbound конфигурации Xray
    
    protocol: vless, vmess, trojan, shadowsocks, socks, http, wireguard, hysteria2, tuic
    transport: tcp, mkcp, ws, grpc, httpupgrade, xhttp, hysteria
    security: none, tls, reality
    """
    tag = tag or f"{protocol}_{transport}_{security}_{port}"
    
    # === НАСТРОЙКИ ПРОТОКОЛА ===
    protocol_settings = {}
    
    if protocol == 'vless':
        client_id = kwargs.get('uuid', generate_uuid())
        protocol_settings = {
            "clients": [{"id": client_id, "flow": kwargs.get('flow', "")}],
            "decryption": "none"
        }
        
    elif protocol == 'vmess':
        client_id = kwargs.get('uuid', generate_uuid())
        protocol_settings = {
            "clients": [{"id": client_id, "alterId": kwargs.get('alterId', 0)}]
        }
        
    elif protocol == 'trojan':
        password = kwargs.get('password', generate_random_string(16))
        protocol_settings = {
            "clients": [{"password": password, "flow": kwargs.get('flow', "")}]
        }
        
    elif protocol == 'shadowsocks':
        protocol_settings = {
            "method": kwargs.get('ss_method', '2022-blake3-aes-128-gcm'),
            "password": kwargs.get('ss_password', generate_random_string(32)),
            "network": "tcp,udp"
        }
        
    elif protocol == 'socks':
        protocol_settings = {
            "auth": "password",
            "accounts": [{"user": "user", "pass": generate_random_string(12)}],
            "udp": True
        }
        
    elif protocol == 'http':
        protocol_settings = {
            "allowTransparent": False,
            "accounts": [{"user": "user", "pass": generate_random_string(12)}]
        }
        
    elif protocol == 'wireguard':
        protocol_settings = {
            "secretKey": kwargs.get('wg_secret_key', generate_random_string(44)),
            "address": kwargs.get('wg_address', ['10.0.0.1/32']),
            "peers": [],
            "mtu": 1420
        }
        
    elif protocol == 'hysteria2':
        password = kwargs.get('hy_password', generate_random_string(16))
        protocol_settings = {
            "password": password,
            "users": [{"password": password}],
            "upMbps": kwargs.get('up_mbps', 100),
            "downMbps": kwargs.get('down_mbps', 100)
        }
        
    elif protocol == 'tuic':
        protocol_settings = {
            "users": [{"uuid": generate_uuid(), "password": generate_random_string(16)}],
            "congestion_control": kwargs.get('congestion', 'bbr')
        }

    # === НАСТРОЙКИ ТРАНСПОРТА (STREAM) ===
    stream_settings = {"network": transport}
    
    if transport == 'ws':
        stream_settings["wsSettings"] = {
            "path": kwargs.get('path', f"/{generate_random_string(8)}"),
            "headers": {"Host": kwargs.get('host', "")}
        }
        
    elif transport == 'grpc':
        stream_settings["grpcSettings"] = {
            "serviceName": kwargs.get('service_name', "grpc"),
            "multiMode": kwargs.get('grpc_multi', False)
        }
        
    elif transport == 'xhttp':
        stream_settings["xhttpSettings"] = {
            "path": kwargs.get('path', f"/{generate_random_string(8)}"),
            "mode": kwargs.get('xhttp_mode', "auto"),
            "host": kwargs.get('host', "")
        }
        
    elif transport == 'httpupgrade':
        stream_settings["httpupgradeSettings"] = {
            "path": kwargs.get('path', "/"),
            "host": kwargs.get('host', "")
        }
        
    elif transport == 'mkcp':
        stream_settings["kcpSettings"] = {
            "uplinkCapacity": kwargs.get('uplink', 100),
            "downlinkCapacity": kwargs.get('downlink', 100),
            "congestion": kwargs.get('kcp_congestion', True),
            "readBufferSize": kwargs.get('kcp_read', 2),
            "writeBufferSize": kwargs.get('kcp_write', 2)
        }
        
    elif transport == 'tcp' or transport == 'raw':
        if kwargs.get('tcp_type') == 'http':
            stream_settings["tcpSettings"] = {
                "header": {
                    "type": "http",
                    "request": {
                        "path": [kwargs.get('path', "/")],
                        "headers": {"Host": [kwargs.get('host', "")]}
                    }
                }
            }

    # === НАСТРОЙКИ БЕЗОПАСНОСТИ ===
    if security == 'tls':
        stream_settings["security"] = "tls"
        stream_settings["tlsSettings"] = {
            "serverName": kwargs.get('sni', ""),
            "alpn": kwargs.get('alpn', ["h2", "http/1.1"]),
            "certificates": [{
                "certificateFile": kwargs.get('cert_file', "/etc/xray/cert.pem"),
                "keyFile": kwargs.get('key_file', "/etc/xray/key.pem")
            }]
        }
        
    elif security == 'reality':
        stream_settings["security"] = "reality"
        stream_settings["realitySettings"] = {
            "show": False,
            "dest": kwargs.get('reality_dest', "www.microsoft.com:443"),
            "serverNames": [kwargs.get('reality_sni', "www.microsoft.com")],
            "privateKey": kwargs.get('reality_private_key', ""),
            "shortIds": [kwargs.get('reality_short_id', generate_random_string(16))],
            "xver": kwargs.get('reality_xver', 0)
        }
        
    elif security == 'hysteria':
        # Для Hysteria2 безопасность встроена в протокол
        stream_settings["security"] = "tls"
        stream_settings["tlsSettings"] = {
            "serverName": kwargs.get('sni', ""),
            "alpn": ["h3"]
        }
        
    else:
        stream_settings["security"] = "none"

    # === ИТОГОВЫЙ INBOUND ===
    inbound = {
        "tag": tag,
        "port": port,
        "protocol": protocol,
        "settings": protocol_settings,
        "streamSettings": stream_settings,
        "sniffing": {
            "enabled": True,
            "destOverride": ["http", "tls", "quic"]
        }
    }
    
    return inbound

def generate_subscription_link(inbound_config, email, domain, port):
    """Генерация ссылки подписки (пример)"""
    # Здесь можно добавить генерацию base64 ссылки
    # Для примера возвращаем JSON
    return json.dumps(inbound_config, indent=2)
