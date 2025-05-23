import React, { useState, useEffect, useRef } from 'react';

interface LogEntry {
    id: number;
    message: string;
    timestamp: string;
}

const Logger: React.FC = () => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
    const wsRef = useRef<WebSocket | null>(null);
    const logContainerRef = useRef<HTMLDivElement>(null);
    const logIdCounter = useRef(0);

    const connectWebSocket = () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        setConnectionStatus('connecting');
        const ws = new WebSocket('ws://localhost:8000/ws');

        ws.onopen = () => {
            console.log('WebSocket connecté');
            setConnectionStatus('connected');
        };

        ws.onmessage = (event) => {
            const newLog: LogEntry = {
                id: logIdCounter.current++,
                message: event.data,
                timestamp: new Date().toLocaleTimeString()
            };

            setLogs(prevLogs => [...prevLogs, newLog]);
        };

        ws.onclose = () => {
            console.log('WebSocket fermé');
            setConnectionStatus('disconnected');
            // Tentative de reconnexion après 3 secondes
            setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (error) => {
            console.error('Erreur WebSocket:', error);
            setConnectionStatus('disconnected');
        };

        wsRef.current = ws;
    };

    const clearLogs = () => {
        setLogs([]);
    };

    // Auto-scroll vers le bas quand de nouveaux logs arrivent
    useEffect(() => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [logs]);

    // Connexion automatique au montage du composant
    useEffect(() => {
        connectWebSocket();

        // Nettoyage à la fermeture du composant
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    const getStatusColor = () => {
        switch (connectionStatus) {
            case 'connected': return 'green';
            case 'connecting': return 'orange';
            case 'disconnected': return 'red';
        }
    };

    const getStatusText = () => {
        switch (connectionStatus) {
            case 'connected': return 'Connecté';
            case 'connecting': return 'Connexion...';
            case 'disconnected': return 'Déconnecté';
        }
    };

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
            <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2>Logger en Temps Réel</h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div
                            style={{
                                width: '12px',
                                height: '12px',
                                borderRadius: '50%',
                                backgroundColor: getStatusColor()
                            }}
                        />
                        <span>{getStatusText()}</span>
                    </div>
                    <button
                        onClick={clearLogs}
                        style={{
                            padding: '8px 16px',
                            backgroundColor: '#f44336',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }}
                    >
                        Vider
                    </button>
                </div>
            </div>

            <div
                ref={logContainerRef}
                style={{
                    height: '400px',
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    padding: '15px',
                    backgroundColor: '#1e1e1e',
                    color: '#fff',
                    fontFamily: 'Consolas, Monaco, monospace',
                    fontSize: '14px',
                    overflowY: 'auto',
                    whiteSpace: 'pre-wrap'
                }}
            >
                {logs.length === 0 ? (
                    <div style={{ color: '#888', fontStyle: 'italic' }}>
                        En attente des logs...
                    </div>
                ) : (
                    logs.map((log) => (
                        <div
                            key={log.id}
                            style={{
                                marginBottom: '5px',
                                padding: '4px',
                                borderLeft: '3px solid #4CAF50',
                                paddingLeft: '10px'
                            }}
                        >
              <span style={{ color: '#888', fontSize: '12px' }}>
                [{log.timestamp}]
              </span>
                            <span style={{ marginLeft: '8px' }}>
                {log.message}
              </span>
                        </div>
                    ))
                )}
            </div>

            <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '4px', fontSize: '14px' }}>
                <strong>Instructions:</strong>
                <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                    <li>Démarrez le serveur Python: <code>python main.py</code></li>
                    <li>Tapez vos messages dans le terminal Python</li>
                    <li>Les messages apparaîtront ici en temps réel</li>
                </ul>
            </div>
        </div>
    );
};

export default Logger;