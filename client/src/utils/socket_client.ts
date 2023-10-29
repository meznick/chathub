import { io, Socket } from 'socket.io-client';

const ENDPOINT = 'http://localhost:1234'; // Replace with your server's endpoint

export class SocketClient {
    private socket: Socket;

    constructor() {
        this.socket = io(ENDPOINT);

        // Register event listeners
        this.registerEvents();
    }

    private registerEvents(): void {
        this.socket.on('connect', () => {
            console.log('Connected to the server');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from the server');
        });

        this.socket.on('message', (data: any) => {
            console.log('Message received:', data);
        });

        // Add other event listeners as needed
    }

    // Example function to emit an event to the server
    public sendMessage(message: string): void {
        if (this.socket.connected) {
            this.socket.emit('send_message', message);
        }
    }

    // Implement other methods as needed
}
