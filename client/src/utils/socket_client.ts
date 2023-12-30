export interface MessagePayload {
    [key: string]: string
}

export class SocketClient {
    private client: WebSocket;
    private serverLastAlive: Date;
    public username: string;
    public url: string;

    constructor(username: string, url: string) {
        this.username = username
        this.url = url
        this.client = new WebSocket(this.url)
        this.serverLastAlive = new Date()
        this.serverLastAlive.setSeconds(this.serverLastAlive.getSeconds() - 15)
        this.registerEvents()
        this.heartbeat()
    }

    public sendMessage(message: string): void {
        if (this.client.readyState === WebSocket.OPEN) {
            this.client.send(message);
            console.log(`Sent message ${message}`)
        } else {
            console.log(`Cannot send message ${message} now, state is ${this.client.readyState}`)
        }
    }

    public serverIsAlive() {
        let currentTime = new Date()
        return currentTime.getTime() - this.serverLastAlive.getTime() < 12000;
    };

    private handshakeServer() {
        let connectMessage: MessagePayload = {
            'username': 'test',
            'message': 'connecting'
        }
        this.sendMessage(JSON.stringify(connectMessage))
        console.log('Connected')

    }

    private heartbeat() {
        setInterval(() => {
            let heartbeatMessage: MessagePayload = {
                'username': 'test',
                'system': 'heartbeat'
            }
            this.sendMessage(JSON.stringify(heartbeatMessage));
            console.log(`Heartbeat sent, server is alive: ${this.serverIsAlive()}`)
        }, 5000);
    }

    private processSystemEvents(data: any) {
        if (data['system'] == 'server_is_alive') {
            this.serverLastAlive = new Date()
        }
    }

    private processMessages(data: any) {
        // pass
    }

    private registerEvents(): void {
        this.client.addEventListener('open', () => {
            console.log('Connected to the server, sending handshake');
            this.handshakeServer();
            console.log('Handshake done!')
        });

        this.client.addEventListener('close', () => {
            console.log('Disconnected from the server');
        });

        this.client.addEventListener('message', (message: any) => {
            let data = JSON.parse(message.data)
            console.log('Data received:', data)

            if ('message' in data) {
                this.processMessages(data)
            } else if ('system' in data) {
                this.processSystemEvents(data)
            }
        });

        // other possible events
    }
}
