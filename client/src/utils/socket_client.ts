export interface MessagePayload {
  [key: string]: string
}

export class SocketClient {
    private client: WebSocket;
    public username: string;
    public url: string;

    constructor(username: string, url: string) {
        this.username = username
        this.url = url
        this.client = new WebSocket(this.url)
        // Register event listeners
        this.registerEvents();
    }

    public handshakeServer() {
        let connectMessage: MessagePayload = {
            'username': 'test',
            'message': 'connecting'
        }
        this.sendMessage(JSON.stringify(connectMessage))
        console.log('Connected')

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

        this.client.addEventListener('message', (data: any) => {
            console.log('Message received:', data);
        });

        // other possible events
    }

    // Example function to emit an event to the server
    public sendMessage(message: string): void {
        if (this.client.readyState === WebSocket.OPEN) {
            this.client.send(message);
            console.log(`Sent message ${message}`)
        } else {
            console.log(`Cannot send message ${message} now, state is ${this.client.readyState}`)
        }
    }
}
