from influxdb import InfluxDBClient
import socket, time, json
from datetime import datetime

class ServerStatus:

    def __init__(self):
        self.db = InfluxDBClient(host='localhost', port=8086)
        self.db.switch_database('swgservers')
        self.server_list = [
            { "ip": "login.swgemu.com", "port": 32755 }, # SWGEmu
            { "ip": "198.50.200.67", "port": 44455 }, # Sentinel's Republic
            { "ip": "51.79.97.56", "port": 44455 }, # Bloodfin
            { "ip": "tarkinlogin.ddns.net", "port": 44455 }, # Tarkin's Revenge
            { "ip": "ns525055.ip-158-69-123.net", "port": 44455 }, # Remastered
            { "ip": "live.projectcarbonite.com", "port": 44455 }, # Project Carbonite
            { "ip": "34.83.18.233", "port": 44455 }, # SWG Intended
            { "ip": "74.208.129.128", "port": 44455 } # SWG AoTC (Dauntless)
        ]

    def get_status(self, TCP_IP, TCP_PORT):
        BUFFER_SIZE=1024

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        data = s.recv(BUFFER_SIZE)
        s.close()

        return data.decode('utf-8')

    def construct_influx_object(self, data):
        server_name = data.split("<name>")[1].split("</name>")[0]
        status = data.split("<status>")[1].split("</status>")[0]
        uptime = data.split("<uptime>")[1].split("</uptime>")[0]
        players_connected = data.split("<connected>")[1].split("</connected>")[0]
        max_players = data.split("<max>")[1].split("</max>")[0]
        total_players = data.split("<total>")[1].split("</total>")[0]
        the_time = datetime.utcnow().isoformat()

        return [{
            "measurement": server_name,
            "status": status,
            "time": the_time,
            "fields": {
                "connected": int(players_connected),
                "uptime": int(uptime),
                "max": int(max_players),
                "total": int(total_players)
            }
        }]

    def write_to_db(self):
        try:
            for server in self.server_list:
                data = self.construct_influx_object(
                    self.get_status(
                        server["ip"], server["port"]
                    )
                )

                self.db.write_points(data)
        except:
            print("Unable to connect to server")
    
if __name__ == "__main__":
    status = ServerStatus()
    status.write_to_db()
