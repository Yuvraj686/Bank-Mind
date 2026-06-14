import { useEffect, useRef, useCallback } from 'react';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/dashboard';
const RECONNECT_INTERVAL = 5000;

export function useWebSocket(onMessage) {
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    const token = localStorage.getItem('bankmind_token');
    if (!token) return;

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[WS] Connected to BankMind dashboard');
        if (reconnectRef.current) {
          clearInterval(reconnectRef.current);
          reconnectRef.current = null;
        }
        // Start ping loop
        const ping = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000);
        ws._pingInterval = ping;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data !== 'pong') {
            onMessageRef.current?.(data);
          }
        } catch (_) {}
      };

      ws.onerror = (e) => {
        console.warn('[WS] Error', e);
      };

      ws.onclose = () => {
        console.log('[WS] Disconnected — reconnecting in 5s...');
        if (ws._pingInterval) clearInterval(ws._pingInterval);
        if (!reconnectRef.current) {
          reconnectRef.current = setInterval(connect, RECONNECT_INTERVAL);
        }
      };
    } catch (e) {
      console.error('[WS] Connection failed:', e);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectRef.current) clearInterval(reconnectRef.current);
    };
  }, [connect]);

  return wsRef;
}
