from influxdb import InfluxDBClient
import socket, time, json

class ServerStatus:

    def __init__(self):
        self.db = InfluxDBClient(host='localhost', port=8086)
        self.db.switch_database('swgservers')
        self.server_list = [
            {
                "ip": "login.swgemu.com", # SWGEmu
                "port": 32755
            },
            {
                "ip": "198.50.227.105", # Sentinel's Republic
                "port": 44455
            },
            {
                "ip": "51.79.97.56", # Bloodfin
                "port": 44455
            },
            {
                "ip": "tarkinlogin.ddns.net", # Tarkin's Revenge
                "port": 44455
            },
            {
                "ip": "ns525055.ip-158-69-123.net", # Remastered
                "port": 44455
            },
            {
                "ip": "live.projectcarbonite.com", # Project Carbonite
                "port": 44455
            },
            {
                "ip": "34.83.18.233", # SWG Intended
                "port": 44455
            },
            {
                "ip": "74.208.129.128", # SWG AoTC (Dauntless)
                "port": 44455
            }
        ]

    def get_status(self, TCP_IP, TCP_PORT):
        BUFFER_SIZE=1024

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        data = s.recv(BUFFER_SIZE)
        s.close()

        return data.decode('utf-8')

    def parse_status(self, data):
        server_name = data.split("<name>")[1].split("</name>")[0]
        status = data.split("<status>")[1].split("</status>")[0]
        uptime = data.split("<uptime>")[1].split("</uptime>")[0]
        players_connected = data.split("<connected>")[1].split("</connected>")[0]
        max_players = data.split("<max>")[1].split("</max>")[0]
        total_players = data.split("<total>")[1].split("</total>")[0]

        return {"server": server_name, "status": status, "uptime": uptime, 
                "connected": players_connected, "max": max_players, "total": total_players}

    def construct_influx_object(self, data):
        the_time = round(time.time())

        data = [{
            "measurement": data["server"],
            "status": data["status"],
            "tags": {
                "connected": data["connected"]
            },
            "time": the_time,
            "fields": {
                "uptime": data["uptime"],
                "max": data["max"],
                "total": data["total"]
            }
        }]

        return data

    def write_to_db(self):
        for server in self.server_list:
            data = self.construct_influx_object(
                status.parse_status(
                    status.get_status(
                        server["ip"], server["port"]
                    )
                )
            )
            result = self.db.write_points(data)
            print(result)
    
if __name__ == "__main__":
    status = ServerStatus()
    status.write_to_db()